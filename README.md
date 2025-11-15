# AI Job Discovery Platform

Multi-Agent AI system for autonomous job search with resume parsing and intelligent job discovery.

---

## Overview

This platform uses 3 specialized AI agents to automate job discovery:

1. **Resume Intelligence Agent (RIA)** - Parses resumes and extracts structured data
2. **Smart Query Agent (SQA)** - Generates 100+ targeted search queries
3. **Job Discovery Agent (JDA)** - Scrapes 8+ job sources for real opportunities

**Result**: Upload resume, get 100-200 real jobs in 60 seconds.

---

## Quick Start

### Prerequisites

- Python 3.9+
- Node.js 18+
- Google Gemini API Key (get from https://aistudio.google.com/apikey)
- Serper API Key (get from https://serper.dev)

### Backend Setup

1. Navigate to backend:

   ```bash
   cd backend
   ```

2. Create virtual environment:

   ```bash
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   ```

3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Configure environment:

   ```bash
   cp .env.example .env
   ```

   Add to `.env`:

   ```
   GOOGLE_API_KEY=your_gemini_api_key
   SERPER_API_KEY=your_serper_api_key
   DATABASE_URL=your_neon_postgresql_url
   PORT=8000
   ```

5. Run backend:
   ```bash
   python main.py
   ```
   Server starts on `http://localhost:8000`

### Frontend Setup

1. Navigate to frontend:

   ```bash
   cd frontend
   ```

2. Install dependencies:

   ```bash
   npm install
   ```

3. Run frontend:
   ```bash
   npm run dev
   ```
   App starts on `http://localhost:3000`

---

## Project Structure

```
helper/
├── backend/
│   ├── agents/
│   │   ├── resume_intelligence_agent.py    # RIA - Resume parser
│   │   ├── smart_query_agent.py            # SQA - Query generator
│   │   └── job_discovery_agent.py          # JDA - Job scraper
│   ├── api/
│   │   └── routes.py                       # FastAPI endpoints
│   ├── database/
│   │   └── client.py                       # Prisma ORM client
│   ├── prisma/
│   │   └── schema.prisma                   # Database schema
│   ├── uploads/                            # Resume storage
│   ├── main.py                             # App entry point
│   ├── requirements.txt                    # Python dependencies
│   └── .env                                # Environment config
│
├── frontend/
│   ├── components/
│   │   └── ResumeUpload.tsx               # Main UI component
│   ├── lib/
│   │   └── api.ts                         # Backend API client
│   ├── app/
│   │   ├── layout.tsx                     # Root layout
│   │   └── page.tsx                       # Home page
│   ├── package.json                       # Node dependencies
│   ├── tsconfig.json                      # TypeScript config
│   └── tailwind.config.js                 # Tailwind config
│
├── .gitignore                             # Git ignore rules
└── README.md                              # This file
```

---

## System Architecture

### Agent Pipeline Flow

```
User uploads resume (PDF)
        ↓
[Resume Intelligence Agent - RIA]
   - Extracts text from PDF
   - Parses with Gemini 2.5 Flash-Lite
   - Outputs: name, skills, experience, education
        ↓
[Smart Query Agent - SQA]
   - Generates 100+ search queries
   - Creates queries for 6 platforms
   - Outputs: Google, JSearch, Jooble, Wellfound, YC, Company pages
        ↓
[Job Discovery Agent - JDA]
   - Layer 1: Company career pages (30 companies)
   - Layer 2: Google Search (Serper API)
   - Layer 3: RemoteOK (API)
   - Layer 4: We Work Remotely (HTML)
   - Layer 5: Wellfound (Next.js data + HTML)
   - Layer 6: YC Jobs (API + Next.js data)
   - Layer 7: Hacker News (HTML)
   - Layer 8: Remote.co (HTML)
   - Validates genuine job postings
   - Deduplicates results
        ↓
100-200 Real Jobs with Apply Links
```

### Data Flow

```
Frontend                    Backend                     External APIs
--------                    -------                     -------------
Upload PDF     →     POST /upload           →     Save to uploads/
                     Returns file_id
                            ↓
               →     POST /discover-jobs    →     RIA: Gemini API (parse)
                            ↓
                            SQA: Generate queries (no API)
                            ↓
                            JDA: Serper API (38 calls)
                            ↓
                            JDA: Scrape 8 sources
                            ↓
Display Jobs   ←     Returns jobs array
```

---

## Agent Details

### Resume Intelligence Agent (RIA)

**Technology:** Google Gemini 2.5 Flash-Lite

**Input:** PDF resume file

**Output:** Structured JSON with:

- Personal info (name, email, phone, location)
- Skills (8 categories: languages, frameworks, databases, cloud, devops, tools, libraries, soft skills)
- Experience (company, role, dates, duration, technologies)
- Education (degree, institution, years, GPA)
- Projects (name, description, tech stack)
- Certifications, languages, years of experience
- Primary job role prediction

### Smart Query Agent (SQA)

**Technology:** Rule-based logic (no LLM)

**Input:** Parsed resume data from RIA

**Output:** 100+ search queries across:

- Google Search: 45 queries (location + experience + tech variations)
- JSearch API: 18 queries
- Jooble: 15 queries
- Wellfound: 12 queries
- YC Jobs: 12 keywords
- Company Pages: 120+ companies (IT Services, Unicorns, Fintech, SaaS, Global Tech)

### Job Discovery Agent (JDA)

**Technology:** Multi-layer scraping + API integration

**Input:** Search queries from SQA

**Output:** Validated, deduplicated job listings

**Scraping Layers:**

1. Company career pages (30 companies via Serper API)
2. Google Search results (8 queries via Serper API)
3. RemoteOK public API
4. We Work Remotely HTML scraping
5. Wellfound Next.js data extraction + HTML scraping
6. YC Jobs API + Next.js data extraction
7. Hacker News jobs HTML scraping
8. Remote.co HTML scraping

**Job Validation:**

- Filters out career homepage URLs
- Only includes genuine job postings
- Validates URLs contain job IDs or ATS systems
- Extracts job details from pages when possible

---

## Tech Stack

### Backend

- FastAPI - Web framework
- Prisma ORM - Database client
- Neon PostgreSQL - Database
- Google Gemini 2.5 Flash-Lite - LLM for parsing
- Serper API - Google Search
- httpx - Async HTTP client
- BeautifulSoup4 - HTML parsing
- pdfplumber - PDF text extraction

### Frontend

- Next.js 14 - React framework
- TypeScript - Type safety
- Tailwind CSS - Styling
- Axios - API client
- react-dropzone - File upload UI
- Lucide React - Icons

---

## Environment Variables

### Backend (.env)

```
GOOGLE_API_KEY=your_gemini_api_key
SERPER_API_KEY=your_serper_api_key
DATABASE_URL=postgresql://user:pass@host:5432/db
PORT=8000
```

### Frontend (.env.local)

```
NEXT_PUBLIC_BACKEND_URL=http://localhost:8000
```

---

## Development

### Run Backend

```bash
cd backend
source venv/bin/activate
python main.py
```

### Run Frontend

```bash
cd frontend
npm run dev
```

---

## Performance

- Resume parsing: 1-2 seconds
- Query generation: < 1 second
- Job discovery: 40-60 seconds
- Total time: 45-65 seconds per resume
- Jobs returned: 100-200 genuine opportunities

---

## License

MIT
