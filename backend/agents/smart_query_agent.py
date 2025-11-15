"""
Smart Query Agent (SQA)
Extracts job-search relevant factors from parsed resume and generates 100+ targeted search queries
for Multi-Layer Job Discovery Agent (MLDA)
Focuses only on: experience, tech stack, tools, skills - ignoring irrelevant data
"""

from typing import Dict, List
from .base_agent import BaseAgent


class SmartQueryAgent(BaseAgent):
    """
    Extracts critical job-search factors and generates intelligent queries for multiple platforms
    Input: Parsed resume from RIA
    Output: Job-relevant factors + 100+ optimized search queries (no LLM API calls)
    """
    
    def __init__(self):
        super().__init__(agent_name="SmartQueryAgent", temperature=0)
        self.log("Initialized - Pure rule-based query generation")
    
    async def execute(self, parsed_resume: Dict) -> Dict:
        """
        Main execution: Extract job factors and generate 100+ queries for MLDA
        
        Args:
            parsed_resume: Complete parsed resume from RIA
            
        Returns:
            {
                "target_role": str,
                "experience_level": str,
                "primary_skills": List[str],
                "google_search_queries": List[str],  # 40+ queries
                "api_queries": {
                    "jsearch": List[str],
                    "jooble": List[str]
                },
                "wellfound_queries": List[str],
                "yc_queries": List[str],
                "company_career_pages": List[str]
            }
        """
        self.log("Extracting job-relevant factors...")
        
        # Extract critical factors
        job_factors = self._extract_job_factors(parsed_resume)
        
        # Generate 100+ queries (rule-based, no LLM)
        self.log("Generating 100+ search queries...")
        queries = self._generate_all_queries(job_factors)
        
        self.log(f"✓ Generated {self._count_total_queries(queries)} total queries")
        
        return queries
    
    def _extract_job_factors(self, parsed_resume: Dict) -> Dict:
        """
        Extract only job-search relevant data
        """
        skills_data = parsed_resume.get("skills", {})
        
        # Flatten tech stack
        tech_stack = []
        tech_stack.extend(skills_data.get("programming_languages", []))
        tech_stack.extend(skills_data.get("frameworks", []))
        tech_stack.extend(skills_data.get("libraries", []))
        
        # Tools & platforms
        tools = []
        tools.extend(skills_data.get("databases", []))
        tools.extend(skills_data.get("cloud", []))
        tools.extend(skills_data.get("devops", []))
        tools.extend(skills_data.get("tools", []))
        
        # Primary skills (top 10)
        all_skills = tech_stack + tools
        primary_skills = all_skills[:10] if all_skills else []
        
        # Experience and role
        experience_years = parsed_resume.get("years_of_experience_estimated") or 0
        job_role = parsed_resume.get("primary_job_role_prediction", "Software Developer")
        
        return {
            "experience_years": experience_years,
            "tech_stack": tech_stack,
            "tools": tools,
            "primary_skills": primary_skills,
            "job_role": job_role
        }
    
    def _generate_all_queries(self, job_factors: Dict) -> Dict:
        """
        Generate 100+ queries across all platforms (rule-based)
        """
        exp_years = job_factors["experience_years"]
        role = job_factors["job_role"]
        skills = job_factors["primary_skills"][:6]
        tech_stack = job_factors["tech_stack"][:8]
        tools = job_factors["tools"][:6]
        
        # Determine experience level
        if exp_years < 1:
            exp_level = "Fresher (0 years)"
            exp_keywords = ["fresher", "entry level", "0-1 year", "graduate", "intern", "junior"]
        elif exp_years < 3:
            exp_level = f"Junior ({int(exp_years)} years)"
            exp_keywords = ["junior", "1-2 years", "0-2 years", "entry level"]
        elif exp_years < 5:
            exp_level = f"Mid-level ({int(exp_years)} years)"
            exp_keywords = ["mid level", "2-4 years", "3-5 years"]
        else:
            exp_level = f"Senior ({int(exp_years)}+ years)"
            exp_keywords = ["senior", "5+ years", f"{int(exp_years)}+ years"]
        
        return {
            "target_role": role,
            "experience_level": exp_level,
            "primary_skills": skills,
            "google_search_queries": self._generate_google_queries(role, exp_keywords, skills, tech_stack),
            "api_queries": {
                "jsearch": self._generate_jsearch_queries(role, exp_keywords, skills),
                "jooble": self._generate_jooble_queries(role, exp_keywords, skills)
            },
            "wellfound_queries": self._generate_wellfound_queries(role, skills),
            "yc_queries": self._generate_yc_queries(skills, tech_stack),
            "company_career_pages": self._generate_company_pages(exp_years)
        }
    
    def _generate_google_queries(self, role: str, exp_keywords: List[str], skills: List[str], tech_stack: List[str]) -> List[str]:
        """
        Generate 40+ Google search queries
        """
        queries = []
        
        # Role + experience + location variations
        locations = ["remote", "India", "Bangalore", "Delhi", "Mumbai", "Hyderabad", "Pune"]
        for loc in locations:
            for exp in exp_keywords[:3]:
                queries.append(f"{role} {exp} jobs {loc}")
        
        # Role + tech stack combinations
        for tech in tech_stack[:5]:
            queries.append(f"{tech} developer jobs {exp_keywords[0]}")
            queries.append(f"{role} {tech} remote")
        
        # Skill-based queries
        for skill in skills[:4]:
            queries.append(f"{skill} developer jobs remote")
            queries.append(f"{skill} {exp_keywords[0]} job India")
        
        # Combined skills
        if len(skills) >= 2:
            queries.append(f"{skills[0]} {skills[1]} developer jobs")
            queries.append(f"{skills[0]} {skills[1]} {exp_keywords[0]}")
        
        # Startup specific
        queries.extend([
            f"{role} startup jobs India",
            f"{role} early stage startup",
            f"{skills[0]} developer startup remote" if skills else f"{role} startup remote"
        ])
        
        return queries[:45]
    
    def _generate_jsearch_queries(self, role: str, exp_keywords: List[str], skills: List[str]) -> List[str]:
        """
        Generate 15+ JSearch API queries
        """
        queries = [
            role.lower(),
            f"{role} {exp_keywords[0]}",
            f"software engineer {exp_keywords[0]}"
        ]
        
        for skill in skills[:5]:
            queries.append(f"{skill} developer")
            queries.append(f"{skill} {exp_keywords[0]}")
        
        queries.extend([
            f"{role} internship" if "fresher" in exp_keywords[0] else f"{role} remote",
            "full stack developer",
            "backend developer",
            "frontend developer"
        ])
        
        return queries[:18]
    
    def _generate_jooble_queries(self, role: str, exp_keywords: List[str], skills: List[str]) -> List[str]:
        """
        Generate 12+ Jooble API queries
        """
        queries = [
            f"{role} {exp_keywords[0]}",
            f"software engineer {exp_keywords[0]}"
        ]
        
        for skill in skills[:4]:
            queries.append(f"{skill} developer {exp_keywords[0]}")
        
        queries.extend([
            f"{role} remote",
            f"{role} startup",
            "software developer remote"
        ])
        
        return queries[:15]
    
    def _generate_wellfound_queries(self, role: str, skills: List[str]) -> List[str]:
        """
        Generate 10+ Wellfound (AngelList) queries
        """
        queries = [
            role.lower(),
            "software engineer",
            "full stack developer",
            "backend developer",
            "frontend developer"
        ]
        
        for skill in skills[:5]:
            queries.append(f"{skill} developer")
        
        return queries[:12]
    
    def _generate_yc_queries(self, skills: List[str], tech_stack: List[str]) -> List[str]:
        """
        Generate 10+ YCombinator queries (tech-focused)
        """
        queries = [
            "full stack",
            "backend",
            "frontend",
            "software engineer"
        ]
        
        for tech in tech_stack[:6]:
            queries.append(tech.lower())
        
        return queries[:12]
    
    def _generate_company_pages(self, exp_years: float) -> List[str]:
        """
        Generate 100+ company career page targets based on experience
        """
        # Indian Tech Giants & IT Services (Fresher-friendly)
        it_services = [
            "TCS careers", "Wipro careers", "Infosys careers", "HCL careers",
            "Tech Mahindra careers", "LTI Mindtree careers", "Mphasis careers",
            "Cognizant careers India", "Accenture careers India", "Capgemini careers India",
            "IBM careers India", "Oracle careers India", "SAP careers India"
        ]
        
        # Indian Unicorns & Major Startups
        unicorns = [
            "Flipkart careers", "Zomato careers", "Swiggy careers", "Paytm careers",
            "PhonePe careers", "CRED careers", "Razorpay careers", "Zerodha careers",
            "Groww careers", "Meesho careers", "Urban Company careers", "Ola careers",
            "Dunzo careers", "Licious careers", "BigBasket careers", "Nykaa careers",
            "PolicyBazaar careers", "CarDekho careers", "Delhivery careers"
        ]
        
        # Indian Fintech & Banking
        fintech = [
            "BankBazaar careers", "Paytm Money careers", "Khatabook careers",
            "CRED careers", "Jupiter careers", "Fi Money careers", "Slice careers",
            "FamPay careers", "NiYO careers", "Fampay careers", "CashFree careers",
            "Instamojo careers", "PayU careers India"
        ]
        
        # Indian SaaS & B2B
        saas = [
            "Freshworks careers", "Zoho careers", "Chargebee careers", "Postman careers",
            "BrowserStack careers", "Clevertap careers", "Exotel careers",
            "WebEngage careers", "Darwinbox careers", "Whatfix careers",
            "Yellow.ai careers", "Haptik careers", "MoEngage careers"
        ]
        
        # E-commerce & Retail Tech
        ecommerce = [
            "Amazon careers India", "Myntra careers", "Ajio careers",
            "Snapdeal careers", "Shopclues careers", "FirstCry careers",
            "Bewakoof careers", "Lenskart careers", "Purplle careers"
        ]
        
        # Global Tech Companies (India offices)
        global_tech = [
            "Google careers India", "Microsoft careers India", "Meta careers India",
            "Amazon Web Services careers India", "Adobe careers India",
            "Salesforce careers India", "Intel careers India", "Nvidia careers India",
            "VMware careers India", "Cisco careers India", "Dell careers India",
            "HP careers India", "Apple careers India", "Twitter careers India",
            "LinkedIn careers India", "Uber careers India", "Airbnb careers India"
        ]
        
        # Gaming & Entertainment
        gaming = [
            "Dream11 careers", "MPL careers", "Games24x7 careers", "Junglee Games careers",
            "Nazara careers", "Winzo careers", "Rooter careers", "Loco careers",
            "Disney+ Hotstar careers", "Netflix careers India", "Amazon Prime Video careers India"
        ]
        
        # EdTech
        edtech = [
            "Unacademy careers", "Byjus careers", "Vedantu careers", "Upgrad careers",
            "Toppr careers", "Doubtnut careers", "Physics Wallah careers",
            "Simplilearn careers", "Great Learning careers", "Scaler careers"
        ]
        
        # HealthTech
        healthtech = [
            "PharmEasy careers", "1mg careers", "Practo careers", "Medibuddy careers",
            "CureFit careers", "HealthifyMe careers", "Lybrate careers"
        ]
        
        # Logistics & Delivery
        logistics = [
            "Dunzo careers", "Shadowfax careers", "Porter careers", "BlackBuck careers",
            "Rivigo careers", "Loadshare careers", "Ecom Express careers"
        ]
        
        # Travel & Hospitality
        travel = [
            "Oyo careers", "MakeMyTrip careers", "Goibibo careers", "Ixigo careers",
            "EaseMyTrip careers", "Cleartrip careers", "Treebo careers", "FabHotels careers"
        ]
        
        # Social & Media
        social = [
            "ShareChat careers", "Moj careers", "Josh careers", "Chingari careers",
            "InMobi careers", "Times Internet careers", "Dailyhunt careers"
        ]
        
        # Agritech & Others
        others = [
            "Ninjacart careers", "DeHaat careers", "AgroStar careers",
            "Rebel Foods careers", "Zomato Infrastructure careers",
            "CarTrade careers", "CarWale careers", "BikeWale careers"
        ]
        
        # Combine all companies
        all_companies = []
        all_companies.extend(it_services)
        all_companies.extend(unicorns)
        all_companies.extend(fintech)
        all_companies.extend(saas)
        all_companies.extend(ecommerce)
        all_companies.extend(global_tech)
        all_companies.extend(gaming)
        all_companies.extend(edtech)
        all_companies.extend(healthtech)
        all_companies.extend(logistics)
        all_companies.extend(travel)
        all_companies.extend(social)
        all_companies.extend(others)
        
        # Filter based on experience
        if exp_years < 2:
            # Prioritize fresher-friendly companies
            priority = it_services + saas + global_tech + edtech
            others_list = [c for c in all_companies if c not in priority]
            return priority + others_list[:100]
        else:
            # Return all companies for experienced candidates
            return all_companies[:120]
    
    def _count_total_queries(self, queries: Dict) -> int:
        """Count total queries generated"""
        count = len(queries["google_search_queries"])
        count += len(queries["api_queries"]["jsearch"])
        count += len(queries["api_queries"]["jooble"])
        count += len(queries["wellfound_queries"])
        count += len(queries["yc_queries"])
        count += len(queries["company_career_pages"])
        return count


# Initialize agent
smart_query_agent = None

def get_smart_query_agent():
    """Get or create the smart query agent instance"""
    global smart_query_agent
    if smart_query_agent is None:
        smart_query_agent = SmartQueryAgent()
    return smart_query_agent
