# System Flow

Complete data flow and architecture of the AI Job Discovery Platform.

---

## User Flow

```
User uploads resume PDF
        ↓
Frontend (Next.js)
        ↓
Backend API receives file
        ↓
Saves to uploads/ directory
        ↓
Returns file_id to frontend
        ↓
Frontend triggers job discovery
        ↓
Backend runs 3-agent pipeline
        ↓
Returns 100-200 jobs with apply links
        ↓
Frontend displays job cards
```

---

## Complete Data Flow

```
┌─────────────────────────────────────────┐
│     User Uploads Resume (PDF)           │
└──────────────┬──────────────────────────┘
               ↓
┌─────────────────────────────────────────┐
│  Frontend: Next.js + TypeScript         │
│  http://localhost:3000                  │
│  - Drag and drop UI                     │
│  - File validation                      │
│  - Loading states                       │
└──────────────┬──────────────────────────┘
               ↓
        POST /upload
               ↓
┌─────────────────────────────────────────┐
│  Backend: FastAPI                       │
│  http://localhost:8000                  │
│  - Saves PDF to uploads/                │
│  - Returns file_id                      │
└──────────────┬──────────────────────────┘
               ↓
    POST /discover-jobs/{file_id}
               ↓
┌─────────────────────────────────────────┐
│  Resume Intelligence Agent (RIA)        │
│  - Extract text from PDF (pdfplumber)   │
│  - Parse with Gemini 2.5 Flash-Lite     │
│  - Output: Personal info, skills, exp   │
│  Processing: 1-2 seconds                │
└──────────────┬──────────────────────────┘
               ↓
┌─────────────────────────────────────────┐
│  Smart Query Agent (SQA)                │
│  - Generate 100+ search queries         │
│  - 6 platforms: Google, JSearch, etc    │
│  - 120+ company career pages            │
│  Processing: <1 second                  │
└──────────────┬──────────────────────────┘
               ↓
┌─────────────────────────────────────────┐
│  Job Discovery Agent (JDA)              │
│  - Layer 1: Company careers (Serper)    │
│  - Layer 2: Google Search (Serper)      │
│  - Layer 3: RemoteOK API                │
│  - Layer 4: We Work Remotely            │
│  - Layer 5: Wellfound                   │
│  - Layer 6: YC Jobs                     │
│  - Layer 7: Hacker News                 │
│  - Layer 8: Remote.co                   │
│  - Validate genuine jobs                │
│  - Deduplicate results                  │
│  Processing: 40-60 seconds              │
└──────────────┬──────────────────────────┘
               ↓
┌─────────────────────────────────────────┐
│  Response: 100-200 Real Jobs            │
│  {                                      │
│    jobs: [                              │
│      {                                  │
│        title: "Senior Engineer"         │
│        company: "Google"                │
│        location: "Remote"               │
│        experience: "3-5 years"          │
│        skills_required: [...]           │
│        apply_url: "..."                 │
│        source: "company_careers"        │
│      }                                  │
│    ],                                   │
│    total_jobs: 104                      │
│  }                                      │
└──────────────┬──────────────────────────┘
               ↓
┌─────────────────────────────────────────┐
│  Frontend Displays Jobs                 │
│  - Job cards with company, title        │
│  - Location and experience              │
│  - Skills badges                        │
│  - Apply Now button                     │
│  - Source badge                         │
└─────────────────────────────────────────┘
```

---

## Agent Pipeline

```
┌────────────────────────────────────────────┐
│  Resume Intelligence Agent (RIA)           │
├────────────────────────────────────────────┤
│  Technology: Gemini 2.5 Flash-Lite         │
│  Input: PDF file                           │
│  Process:                                  │
│    1. Extract text with pdfplumber         │
│    2. Parse with LLM                       │
│    3. Validate JSON structure              │
│  Output:                                   │
│    - Personal info                         │
│    - 8 skill categories                    │
│    - Experience with duration              │
│    - Education                             │
│    - Projects                              │
│    - Years of experience                   │
│    - Primary job role prediction           │
│  API Usage: 1 Gemini call                  │
│  Time: 1-2 seconds                         │
└────────────────────────────────────────────┘
                   ↓
┌────────────────────────────────────────────┐
│  Smart Query Agent (SQA)                   │
├────────────────────────────────────────────┤
│  Technology: Rule-based logic              │
│  Input: Parsed resume JSON                 │
│  Process:                                  │
│    1. Extract key factors                  │
│    2. Generate Google queries (45)         │
│    3. Generate JSearch queries (18)        │
│    4. Generate Jooble queries (15)         │
│    5. Generate Wellfound queries (12)      │
│    6. Generate YC keywords (12)            │
│    7. Select 120+ companies                │
│  Output:                                   │
│    - 100+ search queries                   │
│    - 120+ company pages                    │
│  API Usage: None                           │
│  Time: <1 second                           │
└────────────────────────────────────────────┘
                   ↓
┌────────────────────────────────────────────┐
│  Job Discovery Agent (JDA)                 │
├────────────────────────────────────────────┤
│  Technology: Multi-layer scraping          │
│  Input: Search queries from SQA            │
│  Process:                                  │
│    Layer 1: Company careers                │
│      - Visit 30 company pages via Serper   │
│      - Extract job listings from pages     │
│      - Validate genuine job URLs           │
│    Layer 2: Google Search                  │
│      - 8 queries via Serper API            │
│      - Filter job-related results          │
│      - Validate URL patterns               │
│    Layer 3-8: Free sources                 │
│      - RemoteOK API                        │
│      - We Work Remotely HTML               │
│      - Wellfound Next.js + HTML            │
│      - YC Jobs API + Next.js               │
│      - Hacker News HTML                    │
│      - Remote.co HTML                      │
│  Validation:                               │
│    - Filter career homepage URLs           │
│    - Only genuine job postings             │
│    - Check for job IDs or ATS systems      │
│  Output:                                   │
│    - 100-200 validated jobs                │
│    - Deduplicated results                  │
│  API Usage: 38 Serper calls                │
│  Time: 40-60 seconds                       │
└────────────────────────────────────────────┘
```

---

## Technology Stack

### Frontend

```
Next.js 14        - React framework
TypeScript        - Type safety
Tailwind CSS      - Styling
Axios             - HTTP client
react-dropzone    - File upload UI
Lucide React      - Icons
```

### Backend

```
FastAPI           - Web framework
Prisma ORM        - Database client
Neon PostgreSQL   - Database
Google Gemini     - LLM (2.5 Flash-Lite)
Serper API        - Google Search
httpx             - Async HTTP client
BeautifulSoup4    - HTML parsing
pdfplumber        - PDF text extraction
```

### External Services

```
Gemini API        - Resume parsing (1 call/resume)
Serper API        - Job search (38 calls/resume)
RemoteOK          - Job listings (free, no API key)
Wellfound         - Startup jobs (free)
YC Jobs           - YC startups (free)
Hacker News       - Tech jobs (free)
We Work Remotely  - Remote jobs (free)
Remote.co         - Remote jobs (free)
```

---

## Data Models

### Resume Model (Neon PostgreSQL)

```
Resume
  - id: UUID
  - fileId: String (unique)
  - fileName: String
  - fullName: String
  - email: String
  - phone: String
  - location: String
  - skills: JSON
  - experience: JSON
  - education: JSON
  - yearsOfExperience: Float
  - primaryRole: String
  - createdAt: DateTime
  - updatedAt: DateTime
```

### Job Factors Model

```
JobFactors
  - id: UUID
  - resumeId: String (references Resume)
  - targetRole: String
  - primarySkills: String[]
  - experienceLevel: String
  - preferredLocation: String
  - searchQueries: JSON
  - createdAt: DateTime
```

---

## Job Validation Logic

### URL Validation

```
EXCLUDE (Career Pages):
  /careers
  /jobs (homepage only)
  /about/careers
  /work-with-us
  /join-us
  /talent

INCLUDE (Genuine Jobs):
  /job/[id]
  /position/[id]
  /opening/[id]
  workday.com links
  greenhouse.io links
  lever.co links
  ashbyhq.com links
  Any URL with: job-id, req-, requisition
```

### Job Extraction

```
When visiting career pages:
  1. Parse HTML with BeautifulSoup
  2. Find links matching job patterns
  3. Extract job title from link text
  4. Extract location (Remote, SF, NYC, etc.)
  5. Extract experience (regex: "3+ years")
  6. Extract skills (Python, React, AWS, etc.)
  7. Validate URL is genuine job posting
  8. Return max 3 jobs per company
```

---

## Processing Timeline

```
Total Time: 45-65 seconds per resume

Breakdown:
  Upload + Save:           0-2 seconds
  Resume Parsing (RIA):    1-2 seconds
  Query Generation (SQA):  <1 second
  Job Discovery (JDA):     40-60 seconds
    - Company careers:     30-36 seconds (30 companies × 1s)
    - Google Search:       8-10 seconds (8 queries × 1s)
    - Free sources:        10-14 seconds (parallel)
  Response + Display:      1-2 seconds
```

---

## Current Status

### Completed

- Resume Intelligence Agent (RIA) - PDF parsing with Gemini
- Smart Query Agent (SQA) - 100+ query generation
- Job Discovery Agent (JDA) - 8-layer scraping
- Frontend UI - Upload and display jobs
- Backend API - FastAPI with Prisma ORM
- Database - Neon PostgreSQL with 2 models
- Job validation - Genuine posting filters
- Career page scraping - Extract real job listings
- Deduplication - Remove duplicate jobs
- Source attribution - Show where jobs came from

### Working Features

- Upload PDF resume
- Parse resume in 1-2 seconds
- Generate 100+ search queries
- Scrape 8 job sources
- Validate genuine job postings
- Visit company career pages
- Extract job details from pages
- Return 100-200 real jobs
- Display jobs with apply buttons
- Show job source badges
