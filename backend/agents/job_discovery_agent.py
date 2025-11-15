"""
Job Discovery Agent (JDA)
100% REAL job scraping - NO MOCK DATA
Uses Serper API for Google Search + Public scraping
Returns REAL job links ready to apply
"""

import asyncio
import httpx
import re
import os
import json
from typing import Dict, List, Optional
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse


class JobDiscoveryAgent:
    """
    REAL job scraping from multiple sources
    Uses Serper API + public scraping - NO MOCK DATA
    """
    
    def __init__(self):
        self.agent_name = "JobDiscoveryAgent"
        self.log("Initialized - REAL job scraping (NO MOCK DATA)")
        
        # Get Serper API key
        self.serper_api_key = os.getenv("SERPER_API_KEY")
        if not self.serper_api_key:
            self.log("⚠️  WARNING: No SERPER_API_KEY found in .env")
        
        # HTTP client with realistic headers
        self.client = httpx.AsyncClient(
            timeout=30.0,
            follow_redirects=True,
            headers={
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.5",
                "Accept-Encoding": "gzip, deflate, br",
                "DNT": "1",
                "Connection": "keep-alive",
                "Upgrade-Insecure-Requests": "1"
            }
        )
    
    def log(self, message: str):
        """Simple logging"""
        print(f"[{self.agent_name}] {message}")
    
    async def execute(self, queries_output: Dict) -> Dict:
        """
        REAL job scraping - NO MOCK DATA
        
        Args:
            queries_output: Output from SQA with queries
            
        Returns:
            {
                "jobs": List[Dict],  # REAL jobs with apply links
                "sources_scraped": Dict[str, int],
                "total_jobs": int
            }
        """
        self.log("🚀 Starting REAL job scraping (NO MOCK DATA)...")
        
        all_jobs = []
        sources_count = {}
        
        # Extract search info
        target_role = queries_output.get("target_role", "software developer")
        primary_skills = queries_output.get("primary_skills", [])
        google_queries = queries_output.get("google_search_queries", [])[:10]  # Use top 10 queries
        company_pages = queries_output.get("company_career_pages", [])[:30]  # Top 30 companies
        
        # Layer 1: Company Career Pages with Serper API (HIGH PRIORITY)
        if self.serper_api_key and company_pages:
            self.log("📡 Layer 1: Company Career Pages (Serper API)...")
            career_jobs = await self._scrape_company_careers(company_pages, target_role)
            all_jobs.extend(career_jobs)
            sources_count["company_careers"] = len(career_jobs)
        else:
            sources_count["company_careers"] = 0
        
        # Layer 2: Google Search with Serper API (REAL job links - GLOBAL)
        if self.serper_api_key:
            self.log("📡 Layer 2: Serper API (Global Job Search)...")
            serper_jobs = await self._scrape_google_serper(google_queries)
            all_jobs.extend(serper_jobs)
            sources_count["google_search"] = len(serper_jobs)
        else:
            self.log("⚠️  Skipping Google Search (no API key)")
            sources_count["google_search"] = 0
        
        # Layer 3: RemoteOK (100% free, GLOBAL remote jobs)
        self.log("📡 Layer 3: RemoteOK (Global Remote)...")
        search_term = primary_skills[0] if primary_skills else target_role.split()[0]
        remoteok_jobs = await self._scrape_remoteok(search_term)
        all_jobs.extend(remoteok_jobs)
        sources_count["remoteok"] = len(remoteok_jobs)
        
        # Layer 4: We Work Remotely (GLOBAL remote)
        self.log("📡 Layer 4: We Work Remotely...")
        wwr_jobs = await self._scrape_we_work_remotely(search_term)
        all_jobs.extend(wwr_jobs)
        sources_count["we_work_remotely"] = len(wwr_jobs)
        
        # Layer 5: Wellfound (startup jobs, GLOBAL)
        self.log("📡 Layer 5: Wellfound (Global Startups)...")
        wellfound_jobs = await self._scrape_wellfound(search_term)
        all_jobs.extend(wellfound_jobs)
        sources_count["wellfound"] = len(wellfound_jobs)
        
        # Layer 6: YC Jobs (GLOBAL)
        self.log("📡 Layer 6: YC Jobs (Global)...")
        yc_jobs = await self._scrape_yc_jobs(search_term)
        all_jobs.extend(yc_jobs)
        sources_count["yc_jobs"] = len(yc_jobs)
        
        # Layer 7: Hacker News Hiring (GLOBAL)
        self.log("📡 Layer 7: HN Hiring (Global)...")
        hn_jobs = await self._scrape_hn_hiring()
        all_jobs.extend(hn_jobs)
        sources_count["hn_hiring"] = len(hn_jobs)
        
        # Layer 8: Remote.co (GLOBAL)
        self.log("📡 Layer 8: Remote.co...")
        remoteco_jobs = await self._scrape_remote_co(search_term)
        all_jobs.extend(remoteco_jobs)
        sources_count["remote_co"] = len(remoteco_jobs)
        
        # Normalize and deduplicate
        normalized_jobs = self._normalize_jobs(all_jobs)
        unique_jobs = self._deduplicate_jobs(normalized_jobs)
        
        self.log(f"✅ Found {len(unique_jobs)} REAL jobs (NO MOCK DATA)")
        
        return {
            "jobs": unique_jobs,
            "sources_scraped": sources_count,
            "total_jobs": len(unique_jobs)
        }
    
    async def _scrape_company_careers(self, companies: List[str], role: str) -> List[Dict]:
        """
        Scrape company career pages - EXTRACT ACTUAL JOB LISTINGS from career pages
        """
        jobs = []
        
        if not self.serper_api_key:
            return jobs
        
        for company in companies[:30]:  # Process 30 companies
            try:
                # Search for company career page
                query = f"{company} careers jobs page"
                
                url = "https://google.serper.dev/search"
                headers = {
                    "X-API-KEY": self.serper_api_key,
                    "Content-Type": "application/json"
                }
                payload = {
                    "q": query,
                    "num": 1  # Just get the career page
                }
                
                response = await self.client.post(url, json=payload, headers=headers)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    for result in data.get("organic", [])[:1]:
                        try:
                            career_page_url = result.get("link", "")
                            
                            # Visit career page and extract job listings
                            career_jobs = await self._extract_jobs_from_career_page(
                                career_page_url, company, role
                            )
                            jobs.extend(career_jobs)
                            
                        except Exception as e:
                            self.log(f"Error extracting jobs from {company}: {e}")
                            continue
                
                # Rate limit: 1 request per second
                await asyncio.sleep(1.2)
                
            except Exception as e:
                self.log(f"Company careers error for '{company}': {e}")
        
        self.log(f"✓ Company Careers: Found {len(jobs)} genuine jobs from career pages")
        return jobs
    
    async def _extract_jobs_from_career_page(self, url: str, company: str, role: str) -> List[Dict]:
        """
        Visit a career page and extract ACTUAL job postings
        """
        jobs = []
        
        try:
            response = await self.client.get(url, timeout=15.0)
            
            if response.status_code != 200:
                return jobs
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Strategy 1: Look for job listing links
            job_link_patterns = [
                {'selector': 'a', 'href_contains': ['/job/', '/jobs/', '/position/', '/opening/', '/careers/']},
            ]
            
            found_links = set()
            
            # Find all links that look like job postings
            all_links = soup.find_all('a', href=True)
            
            for link in all_links:
                href = link.get('href', '')
                text = link.get_text(strip=True)
                
                # Skip if empty or too short
                if not text or len(text) < 10:
                    continue
                
                # Check if this looks like a job posting link
                if any(pattern in href.lower() for pattern in ['/job/', '/position/', '/opening/', 'greenhouse.io', 'lever.co', 'workday.com']):
                    # Make absolute URL
                    absolute_url = urljoin(url, href)
                    
                    # Check if it's a genuine job URL
                    if self._is_genuine_job_url(absolute_url, text):
                        # Avoid duplicates
                        if absolute_url not in found_links:
                            found_links.add(absolute_url)
                            
                            jobs.append({
                                "source": "company_careers",
                                "title": text[:100],  # Limit title length
                                "company": company,
                                "location": "See job page",
                                "experience": "See job page",
                                "skills": [],
                                "url": absolute_url,
                                "description": f"Job opening at {company}"
                            })
                            
                            # Limit to 3 jobs per company
                            if len(jobs) >= 3:
                                break
            
            # Strategy 2: If no direct links found, search for job titles in text
            if not jobs:
                # Look for job role keywords in the page
                role_keywords = role.lower().split()
                
                for link in all_links[:50]:  # Check first 50 links
                    text = link.get_text(strip=True).lower()
                    href = link.get('href', '')
                    
                    # Check if text contains role keywords
                    if any(keyword in text for keyword in role_keywords):
                        absolute_url = urljoin(url, href)
                        
                        # Must have some job-related path
                        if any(pattern in absolute_url.lower() for pattern in ['job', 'career', 'position', 'opening', 'apply']):
                            if absolute_url not in found_links:
                                found_links.add(absolute_url)
                                
                                jobs.append({
                                    "source": "company_careers",
                                    "title": link.get_text(strip=True)[:100],
                                    "company": company,
                                    "location": "See job page",
                                    "experience": "See job page",
                                    "skills": [],
                                    "url": absolute_url,
                                    "description": f"{role} at {company}"
                                })
                                
                                if len(jobs) >= 3:
                                    break
            
        except Exception as e:
            self.log(f"Error visiting career page {url}: {e}")
        
        return jobs
    
    def _is_genuine_job_url(self, url: str, title: str) -> bool:
        """
        Validate if URL points to a GENUINE job posting (not just careers homepage)
        """
        url_lower = url.lower()
        title_lower = title.lower()
        
        # EXCLUDE: Generic career pages (these waste user's time)
        exclude_patterns = [
            "careers", "jobs", "about/careers", "company/careers",
            "career-opportunities", "work-with-us", "join-us",
            "talent", "team", "culture"
        ]
        
        # Check if it's ONLY a career page (bad)
        is_just_careers = any(
            url_lower.endswith(pattern) or f"/{pattern}" in url_lower
            for pattern in exclude_patterns
        )
        
        # INCLUDE: Specific job posting indicators (good)
        job_indicators = [
            "/job/", "/position/", "/opening/", "/vacancy/",
            "job-id", "position-id", "req-", "requisition",
            "workday", "greenhouse", "lever", "ashbyhq",
            "breezy", "bamboo", "apply", "jobvite"
        ]
        
        has_job_indicator = any(indicator in url_lower for indicator in job_indicators)
        
        # Title should look like a job title, not generic "Careers" or "Jobs"
        has_specific_title = not any(
            title_lower == word or title_lower.startswith(word + " at")
            for word in ["careers", "jobs", "join us", "work with us"]
        )
        
        # Must have job indicator OR specific title AND not just careers page
        return (has_job_indicator or has_specific_title) and not is_just_careers
    
    async def _extract_job_from_page(self, url: str, company: str, title: str, snippet: str) -> Optional[Dict]:
        """
        Visit job page and extract actual job details
        """
        try:
            response = await self.client.get(url, timeout=10.0)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Extract location (look for common patterns)
                location = self._extract_location(soup) or "See job page"
                
                # Extract experience
                experience = self._extract_experience(soup) or "See job page"
                
                # Extract skills
                skills = self._extract_skills(soup)
                
                return {
                    "source": "company_careers",
                    "title": title,
                    "company": company,
                    "location": location,
                    "experience": experience,
                    "skills": skills,
                    "url": url,
                    "description": snippet[:200]
                }
            
            return None
            
        except Exception:
            # If page extraction fails, still return basic job info if URL is valid
            return {
                "source": "company_careers",
                "title": title,
                "company": company,
                "location": "See job page",
                "experience": "See job page",
                "skills": [],
                "url": url,
                "description": snippet[:200]
            }
    
    def _extract_location(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract location from job page"""
        try:
            # Common location patterns
            patterns = [
                {'name': 'span', 'class': ['location', 'job-location']},
                {'name': 'div', 'class': ['location', 'job-location']},
                {'name': 'p', 'class': ['location']}
            ]
            
            for pattern in patterns:
                elem = soup.find(pattern['name'], class_=pattern.get('class'))
                if elem:
                    return elem.get_text(strip=True)
            
            # Look for text containing location keywords
            text = soup.get_text()
            if 'Remote' in text:
                return "Remote"
            if 'San Francisco' in text:
                return "San Francisco, CA"
            if 'New York' in text:
                return "New York, NY"
                
            return None
        except:
            return None
    
    def _extract_experience(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract experience from job page"""
        try:
            text = soup.get_text().lower()
            
            # Look for experience patterns
            import re
            exp_patterns = [
                r'(\d+)\+?\s*years?\s*(?:of\s*)?experience',
                r'experience:?\s*(\d+)\+?\s*years?',
                r'(\d+)-(\d+)\s*years?'
            ]
            
            for pattern in exp_patterns:
                match = re.search(pattern, text)
                if match:
                    return match.group(0)
            
            return None
        except:
            return None
    
    def _extract_skills(self, soup: BeautifulSoup) -> List[str]:
        """Extract skills from job page"""
        try:
            skills = []
            text = soup.get_text().lower()
            
            # Common tech skills to look for
            skill_keywords = [
                'python', 'java', 'javascript', 'react', 'node', 'aws',
                'kubernetes', 'docker', 'sql', 'mongodb', 'typescript',
                'golang', 'rust', 'c++', 'machine learning', 'ai'
            ]
            
            for skill in skill_keywords:
                if skill in text:
                    skills.append(skill)
            
            return skills[:5]  # Return top 5 skills
        except:
            return []
    
    async def _scrape_google_serper(self, queries: List[str]) -> List[Dict]:
        """
        Scrape Google Search using Serper API - ONLY GENUINE job postings
        """
        jobs = []
        
        if not self.serper_api_key:
            return jobs
        
        for query in queries[:8]:  # Use top 8 queries to save API calls
            try:
                # Serper API endpoint
                url = "https://google.serper.dev/search"
                headers = {
                    "X-API-KEY": self.serper_api_key,
                    "Content-Type": "application/json"
                }
                # Add global locations and specific job keywords
                payload = {
                    "q": query + " (remote OR USA OR UK OR Canada OR San Francisco) apply now",
                    "num": 8
                }
                
                response = await self.client.post(url, json=payload, headers=headers)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Extract organic results
                    for result in data.get("organic", [])[:8]:
                        try:
                            link = result.get("link", "")
                            title = result.get("title", "")
                            snippet = result.get("snippet", "")
                            
                            # VALIDATE: Only genuine job postings
                            if self._is_genuine_job_url(link, title):
                                jobs.append({
                                    "source": "google_search",
                                    "title": title,
                                    "company": self._extract_company_from_url(link),
                                    "location": "See job page",
                                    "experience": "See job page",
                                    "skills": [],
                                    "url": link,
                                    "description": snippet
                                })
                        except Exception:
                            continue
                
                # Rate limit: 1 request per second
                await asyncio.sleep(1)
                
            except Exception as e:
                self.log(f"Serper API error for query '{query}': {e}")
        
        self.log(f"✓ Google Search (Serper): Found {len(jobs)} genuine jobs")
        return jobs
    
    def _extract_company_from_url(self, url: str) -> str:
        """Extract company name from URL"""
        try:
            domain = urlparse(url).netloc
            # Remove www. and common TLDs
            company = domain.replace("www.", "").split(".")[0]
            return company.capitalize()
        except:
            return "Company"
    
    async def _scrape_we_work_remotely(self, search_term: str) -> List[Dict]:
        """
        Scrape We Work Remotely - GLOBAL remote jobs
        """
        jobs = []
        try:
            url = "https://weworkremotely.com/remote-jobs/search?term=" + search_term.lower().replace(" ", "+")
            response = await self.client.get(url)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Find job listings
                job_listings = soup.find_all('li', class_='feature')
                
                for listing in job_listings[:15]:
                    try:
                        title_elem = listing.find('span', class_='title')
                        company_elem = listing.find('span', class_='company')
                        link_elem = listing.find('a', href=True)
                        
                        if title_elem and link_elem:
                            jobs.append({
                                "source": "we_work_remotely",
                                "title": title_elem.get_text(strip=True),
                                "company": company_elem.get_text(strip=True) if company_elem else "Company",
                                "location": "Remote (Global)",
                                "experience": "Varies",
                                "skills": [search_term],
                                "url": urljoin("https://weworkremotely.com", link_elem['href'])
                            })
                    except Exception:
                        continue
                        
            self.log(f"✓ We Work Remotely: Found {len(jobs)} jobs")
        except Exception as e:
            self.log(f"❌ We Work Remotely error: {e}")
        
        return jobs
    
    async def _scrape_remoteok(self, search_term: str) -> List[Dict]:
        """
        Scrape RemoteOK - 100% free, public API, GLOBAL
        """
        jobs = []
        try:
            url = f"https://remoteok.com/api?tag={search_term.lower()}"
            response = await self.client.get(url)
            
            if response.status_code == 200:
                data = response.json()
                # Skip first item (it's metadata)
                for job in data[1:16]:  # Get first 15 jobs
                    try:
                        jobs.append({
                            "source": "remoteok",
                            "title": job.get("position", "Unknown Position"),
                            "company": job.get("company", "Unknown Company"),
                            "location": job.get("location", "Remote"),
                            "experience": "Not specified",
                            "skills": job.get("tags", []),
                            "url": f"https://remoteok.com/l/{job.get('id', '')}",
                            "salary": job.get("salary_range"),
                            "description": job.get("description", "")[:200]
                        })
                    except Exception as e:
                        continue
                        
            self.log(f"✓ RemoteOK: Found {len(jobs)} jobs")
        except Exception as e:
            self.log(f"❌ RemoteOK error: {e}")
        
        return jobs
    
    async def _scrape_wellfound(self, search_term: str) -> List[Dict]:
        """
        Scrape Wellfound (AngelList) - REAL startup jobs using GraphQL API
        """
        jobs = []
        try:
            # Wellfound uses GraphQL API - let's use the job search page
            url = "https://wellfound.com/jobs"
            
            # Add query parameters for search
            params = {
                "role": search_term.lower().replace(" ", "-"),
                "remote": "true"
            }
            
            response = await self.client.get(url, params=params)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Look for Next.js data (Wellfound is built with Next.js)
                scripts = soup.find_all('script', {'id': '__NEXT_DATA__'})
                
                if scripts:
                    import json
                    try:
                        data = json.loads(scripts[0].string)
                        # Try to extract jobs from Next.js data
                        # This structure may vary, but typically in props.pageProps
                        page_props = data.get('props', {}).get('pageProps', {})
                        
                        # Look for jobs in various possible keys
                        job_listings = (
                            page_props.get('jobs', []) or 
                            page_props.get('jobListings', []) or
                            page_props.get('results', [])
                        )
                        
                        for job in job_listings[:15]:
                            try:
                                jobs.append({
                                    "source": "wellfound",
                                    "title": job.get("title") or job.get("name", "Startup Role"),
                                    "company": job.get("company", {}).get("name") or job.get("companyName", "Startup"),
                                    "location": job.get("locationStr") or job.get("location", "Remote"),
                                    "experience": f"{job.get('minYearsExperience', 0)}-{job.get('maxYearsExperience', 5)} years",
                                    "skills": job.get("tags", [])[:5],
                                    "url": f"https://wellfound.com/jobs/{job.get('id', '')}" if job.get('id') else url
                                })
                            except Exception:
                                continue
                    except json.JSONDecodeError:
                        pass
                
                # Fallback: HTML scraping for job cards
                if not jobs:
                    # Look for job cards/listings in HTML
                    job_cards = soup.find_all(['div', 'article'], class_=re.compile(r'job|listing|card', re.I))
                    
                    for card in job_cards[:15]:
                        try:
                            # Try to find title
                            title_elem = card.find(['h2', 'h3', 'a'], class_=re.compile(r'title|name|role', re.I))
                            if not title_elem:
                                title_elem = card.find('a', href=re.compile(r'/jobs/'))
                            
                            # Try to find company
                            company_elem = card.find(['div', 'span'], class_=re.compile(r'company', re.I))
                            
                            # Try to find link
                            link_elem = card.find('a', href=re.compile(r'/jobs/|/company/'))
                            
                            if title_elem and link_elem:
                                title = title_elem.get_text(strip=True)
                                company = company_elem.get_text(strip=True) if company_elem else "Startup"
                                job_url = urljoin("https://wellfound.com", link_elem['href'])
                                
                                if title and len(title) > 5:
                                    jobs.append({
                                        "source": "wellfound",
                                        "title": title,
                                        "company": company,
                                        "location": "Remote/Global",
                                        "experience": "Varies",
                                        "skills": [search_term],
                                        "url": job_url
                                    })
                        except Exception:
                            continue
                
            # If still no jobs, try direct role URL
            if not jobs:
                role_url = f"https://wellfound.com/role/r/{search_term.lower().replace(' ', '-')}"
                response = await self.client.get(role_url)
                
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    
                    # Find all job links
                    job_links = soup.find_all('a', href=re.compile(r'/company/.*/jobs/'))
                    
                    for link in job_links[:15]:
                        try:
                            href = link.get('href', '')
                            text = link.get_text(strip=True)
                            
                            if href and text and len(text) > 5:
                                jobs.append({
                                    "source": "wellfound",
                                    "title": text,
                                    "company": "Startup",
                                    "location": "Remote/Global",
                                    "experience": "Varies",
                                    "skills": [search_term],
                                    "url": urljoin("https://wellfound.com", href)
                                })
                        except Exception:
                            continue
                        
            self.log(f"✓ Wellfound: Found {len(jobs)} jobs")
        except Exception as e:
            self.log(f"❌ Wellfound error: {e}")
        
        return jobs
    
    async def _scrape_yc_jobs(self, search_term: str) -> List[Dict]:
        """
        Scrape YCombinator Work at a Startup - REAL jobs from API
        """
        jobs = []
        try:
            # Try to use the public API endpoint first
            api_url = "https://www.workatastartup.com/api/v1/jobs"
            
            response = await self.client.get(api_url)
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    
                    # Filter jobs by search term
                    for job in data[:50]:  # Check first 50 jobs
                        try:
                            title = job.get("title", "")
                            company = job.get("company", {})
                            
                            # Filter by search term
                            if search_term.lower() in title.lower() or not search_term:
                                jobs.append({
                                    "source": "yc_jobs",
                                    "title": title,
                                    "company": company.get("name", "YC Startup"),
                                    "location": job.get("location", "Varies"),
                                    "experience": f"{job.get('min_years_experience', 0)}-{job.get('max_years_experience', 5)} years",
                                    "skills": job.get("skills", [])[:5],
                                    "url": f"https://www.workatastartup.com/jobs/{job.get('id', '')}"
                                })
                                
                                if len(jobs) >= 20:
                                    break
                        except Exception:
                            continue
                except json.JSONDecodeError:
                    pass
            
            # Fallback: HTML scraping
            if not jobs:
                url = "https://www.workatastartup.com/jobs"
                response = await self.client.get(url)
                
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    
                    # Look for Next.js data (YC site uses Next.js)
                    scripts = soup.find_all('script', {'id': '__NEXT_DATA__'})
                    
                    if scripts:
                        import json
                        try:
                            data = json.loads(scripts[0].string)
                            page_props = data.get('props', {}).get('pageProps', {})
                            
                            # Look for jobs in various possible keys
                            job_listings = (
                                page_props.get('jobs', []) or 
                                page_props.get('jobListings', []) or
                                page_props.get('results', [])
                            )
                            
                            for job in job_listings[:20]:
                                try:
                                    title = job.get("title", "")
                                    
                                    # Filter by search term
                                    if search_term.lower() in title.lower() or not search_term:
                                        jobs.append({
                                            "source": "yc_jobs",
                                            "title": title,
                                            "company": job.get("company", {}).get("name", "YC Startup"),
                                            "location": job.get("location", "Varies"),
                                            "experience": "Varies",
                                            "skills": job.get("tags", [])[:5],
                                            "url": f"https://www.workatastartup.com/jobs/{job.get('id', '')}"
                                        })
                                except Exception:
                                    continue
                        except json.JSONDecodeError:
                            pass
                    
                    # Final fallback: Find job links in HTML
                    if not jobs:
                        job_links = soup.find_all('a', href=re.compile(r'/jobs/\d+'))
                        
                        for link in job_links[:20]:
                            try:
                                href = link.get('href', '')
                                text = link.get_text(strip=True)
                                
                                # Filter by search term
                                if text and (search_term.lower() in text.lower() or not search_term):
                                    if len(text) > 10:  # Reasonable title length
                                        jobs.append({
                                            "source": "yc_jobs",
                                            "title": text,
                                            "company": "YC Startup",
                                            "location": "Varies",
                                            "experience": "Varies",
                                            "skills": [search_term] if search_term else [],
                                            "url": urljoin("https://www.workatastartup.com", href)
                                        })
                            except Exception:
                                continue
                        
            self.log(f"✓ YC Jobs: Found {len(jobs)} jobs")
        except Exception as e:
            self.log(f"❌ YC Jobs error: {e}")
        
        return jobs
    
    async def _scrape_remote_co(self, search_term: str) -> List[Dict]:
        """
        Scrape Remote.co - GLOBAL remote jobs
        """
        jobs = []
        try:
            url = f"https://remote.co/remote-jobs/developer/"
            response = await self.client.get(url)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Find job cards
                job_cards = soup.find_all('div', class_='job_listing')
                
                for card in job_cards[:15]:
                    try:
                        title_elem = card.find('a', class_='font_weight_700')
                        company_elem = card.find('p', class_='m-0')
                        
                        if title_elem and title_elem.get('href'):
                            title = title_elem.get_text(strip=True)
                            company = company_elem.get_text(strip=True) if company_elem else "Company"
                            
                            # Filter by search term
                            if not search_term or search_term.lower() in title.lower():
                                jobs.append({
                                    "source": "remote_co",
                                    "title": title,
                                    "company": company,
                                    "location": "Remote (Global)",
                                    "experience": "Varies",
                                    "skills": [search_term] if search_term else [],
                                    "url": urljoin("https://remote.co", title_elem['href'])
                                })
                    except Exception:
                        continue
                        
            self.log(f"✓ Remote.co: Found {len(jobs)} jobs")
        except Exception as e:
            self.log(f"❌ Remote.co error: {e}")
        
        return jobs
    
    async def _scrape_hn_hiring(self) -> List[Dict]:
        """
        Scrape Hacker News jobs - REAL postings WORLDWIDE
        """
        jobs = []
        try:
            url = "https://news.ycombinator.com/jobs"
            response = await self.client.get(url)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Find job postings
                job_rows = soup.find_all('tr', class_='athing')
                
                for row in job_rows[:20]:
                    try:
                        title_span = row.find('span', class_='titleline')
                        if title_span:
                            link = title_span.find('a', href=True)
                            if link:
                                href = link.get('href', '')
                                title = link.get_text(strip=True)
                                
                                # Make sure it's a valid URL
                                if href.startswith('item?id='):
                                    href = f"https://news.ycombinator.com/{href}"
                                elif not href.startswith('http'):
                                    continue
                                
                                jobs.append({
                                    "source": "hn_hiring",
                                    "title": title,
                                    "company": "Various (HN)",
                                    "location": "See posting",
                                    "experience": "Varies",
                                    "skills": [],
                                    "url": href
                                })
                    except Exception:
                        continue
                        
            self.log(f"✓ HN Hiring: Found {len(jobs)} jobs")
        except Exception as e:
            self.log(f"❌ HN Hiring error: {e}")
        
        return jobs
    
    def _normalize_jobs(self, jobs: List[Dict]) -> List[Dict]:
        """
        Normalize all jobs to common format
        """
        normalized = []
        
        for job in jobs:
            try:
                normalized_job = {
                    "title": job.get("title", "Unknown Position"),
                    "company": job.get("company", "Unknown Company"),
                    "location": job.get("location", "Not specified"),
                    "experience": job.get("experience", "Not specified"),
                    "skills_required": job.get("skills", []),
                    "apply_url": job.get("url", ""),
                    "source": job.get("source", "unknown")
                }
                normalized.append(normalized_job)
            except Exception as e:
                self.log(f"Normalization error: {e}")
        
        return normalized
    
    def _deduplicate_jobs(self, jobs: List[Dict]) -> List[Dict]:
        """
        Remove duplicate jobs based on title + company
        """
        seen = set()
        unique_jobs = []
        
        for job in jobs:
            key = f"{job['title']}|{job['company']}"
            if key not in seen:
                seen.add(key)
                unique_jobs.append(job)
        
        return unique_jobs
    
    async def close(self):
        """Close HTTP client"""
        await self.client.aclose()


# Global instance
job_discovery_agent = None

def get_job_discovery_agent():
    """Get or create the job discovery agent instance"""
    global job_discovery_agent
    if job_discovery_agent is None:
        job_discovery_agent = JobDiscoveryAgent()
    return job_discovery_agent
