# Agent System for Job Search Platform

This directory contains all autonomous agents that power the job search platform.

## 🤖 Agent Architecture

All agents inherit from `BaseAgent` which provides:

- **Gemini 2.0 Flash** LLM instance
- Consistent logging
- Standard execution interface

---

## 📋 Current Agents

### 1. **Resume Intelligence Agent (RIA)**

- **File:** `resume_intelligence_agent.py`
- **Purpose:** Parse PDF resumes and extract structured information
- **Capabilities:**
  - PDF text extraction
  - Skill identification (technical + soft skills)
  - Experience calculation
  - Education & certification extraction
  - Job preference inference
  - Professional summary generation
  - Search query generation

**Usage:**

```python
from agents.resume_intelligence_agent import resume_agent

profile = await resume_agent.parse_resume("path/to/resume.pdf")
queries = resume_agent.generate_search_queries(profile)
```

---

## 🔮 Future Agents (Phase 2+)

### 2. **Query Generator Agent (QGA)**

- Generate 20-40 optimized search queries
- Platform-specific query formatting
- Semantic variations for better coverage

### 3. **Job Discovery Agent (JDA)**

- Multi-layer job discovery:
  - Layer 1: Public APIs (JSearch, Jooble, CareerJet)
  - Layer 2: Direct scraping (YC, Wellfound, RemoteOK)
  - Layer 3: Indirect Google search → company pages
- Parallel execution for speed
- Duplicate detection

### 4. **Job Extraction & Normalization Agent (JENA)**

- Parse messy HTML from scrapers
- Extract structured job data
- Normalize fields across platforms
- Data quality validation

### 5. **Matching & Ranking Agent (MRA)**

- Calculate match scores
- Identify missing skills
- Generate personalized cover letters
- Create tailored messages
- Suggest resume improvements

---

## 🏗️ Agent Communication Flow

```
User Resume
    ↓
[RIA] Extract profile
    ↓
[QGA] Generate search queries
    ↓
[JDA] Discover jobs (APIs + Scrapers)
    ↓
[JENA] Normalize job data
    ↓
[MRA] Match & Rank jobs
    ↓
User Dashboard (Top matches + cover letters)
```

---

## 🎯 Design Principles

1. **Single Responsibility:** Each agent has one clear purpose
2. **Async-First:** All agents use async/await for non-blocking execution
3. **LLM-Powered:** Leverage Gemini 2.0 Flash for intelligent decisions
4. **Type-Safe:** Pydantic models for all data structures
5. **Logging:** Comprehensive logging for debugging
6. **Error Handling:** Graceful degradation on failures

---

## 🔧 Adding New Agents

1. Inherit from `BaseAgent`
2. Implement `async def execute()`
3. Define Pydantic models for input/output
4. Add comprehensive logging
5. Write unit tests
6. Update this README

**Template:**

```python
from .base_agent import BaseAgent
from pydantic import BaseModel
from typing import Dict, Any

class YourAgent(BaseAgent):
    def __init__(self):
        super().__init__(agent_name="YourAgent", temperature=0)

    async def execute(self, input_data: Dict) -> Dict[str, Any]:
        self.log("Starting execution...")
        # Your logic here
        return {"result": "data"}
```

---

## 🔐 Environment Requirements

- `GOOGLE_API_KEY` - Required for all agents using Gemini 2.0 Flash

---

**All agents are powered by Google Gemini 2.0 Flash for maximum intelligence and speed! 🚀**
