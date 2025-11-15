"""
Resume Intelligence Agent (RIA)
LLM-Based Resume Parser with Production-Ready JSON Structure
Part of the Multi-Agent Job Search System
"""

import pdfplumber
import json
from typing import Dict, List, Optional
from pydantic import BaseModel, Field
import os
from .base_agent import BaseAgent


# ==================== PYDANTIC MODELS ====================

class PersonalInfo(BaseModel):
    """Personal information section"""
    full_name: str = ""
    email: str = ""
    phone: str = ""
    location: str = ""


class Skills(BaseModel):
    """Categorized skills"""
    programming_languages: List[str] = Field(default_factory=list)
    frameworks: List[str] = Field(default_factory=list)
    libraries: List[str] = Field(default_factory=list)
    databases: List[str] = Field(default_factory=list)
    cloud: List[str] = Field(default_factory=list)
    devops: List[str] = Field(default_factory=list)
    tools: List[str] = Field(default_factory=list)
    soft_skills: List[str] = Field(default_factory=list)


class Experience(BaseModel):
    """Work experience entry"""
    company: str = ""
    role: str = ""
    start_date: str = ""
    end_date: str = ""
    duration_months: Optional[int] = None
    summary: str = ""
    technologies: List[str] = Field(default_factory=list)


class Education(BaseModel):
    """Education entry"""
    degree: str = ""
    institution: str = ""
    start_year: str = ""
    end_year: str = ""
    gpa: Optional[float] = None


class Project(BaseModel):
    """Project entry"""
    name: str = ""
    description: str = ""
    tech_stack: List[str] = Field(default_factory=list)


class ParsedResume(BaseModel):
    """Complete parsed resume structure"""
    personal_info: PersonalInfo = Field(default_factory=PersonalInfo)
    summary: str = ""
    skills: Skills = Field(default_factory=Skills)
    experience: List[Experience] = Field(default_factory=list)
    education: List[Education] = Field(default_factory=list)
    projects: List[Project] = Field(default_factory=list)
    certifications: List[str] = Field(default_factory=list)
    languages_spoken: List[str] = Field(default_factory=list)
    years_of_experience_estimated: Optional[float] = None
    primary_job_role_prediction: str = ""


# ==================== RESUME INTELLIGENCE AGENT ====================

class ResumeIntelligenceAgent(BaseAgent):
    """
    Production-Ready LLM-Based Resume Parser
    Uses pdfplumber for text extraction + Gemini 2.0 Flash for intelligent parsing
    """
    
    def __init__(self):
        super().__init__(agent_name="ResumeIntelligenceAgent", temperature=0)
        self.log("Initialized with Gemini 2.5 Flash-Lite")
    
    async def execute(self, pdf_path: str) -> Dict:
        """
        Main execution method required by BaseAgent
        Parses resume and returns structured data
        """
        return await self.parse_resume(pdf_path)
    
    def extract_pdf_text(self, pdf_path: str) -> str:
        """
        STEP 1: Extract raw text from PDF using pdfplumber
        Fallback to pytesseract for image-based PDFs
        """
        try:
            self.log(f"Extracting text from: {pdf_path}")
            text = ""
            
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text() or ""
                    text += page_text + "\n"
            
            if not text.strip():
                self.log("Warning: No text extracted. PDF might be image-based.")
                # TODO: Add pytesseract OCR fallback here if needed
                raise Exception("No text could be extracted from PDF")
            
            self.log(f"Successfully extracted {len(text)} characters")
            return text.strip()
        
        except Exception as e:
            raise Exception(f"Error extracting text from PDF: {str(e)}")
    
    async def parse_resume(self, pdf_path: str) -> Dict:
        """
        STEP 2: Send extracted text to LLM agent for structured parsing
        Returns production-ready JSON structure
        """
        try:
            # Step 1: Extract raw text
            resume_text = self.extract_pdf_text(pdf_path)
            
            # Step 2: Create the exact prompt for Gemini
            prompt = self._create_extraction_prompt(resume_text)
            
            # Step 3: Send to LLM
            self.log("Sending to Gemini 2.0 Flash for parsing...")
            response = await self.llm.ainvoke(prompt)
            
            # Step 4: Parse JSON response
            parsed_data = self._extract_json_from_response(response.content)
            
            # Step 5: Validate with Pydantic
            validated_resume = ParsedResume(**parsed_data)
            
            # Step 6: Convert to dict and add metadata
            result = validated_resume.dict()
            result["raw_text"] = resume_text  # Keep for reference
            
            self.log("✓ Resume parsed successfully")
            return result
        
        except Exception as e:
            self.log(f"✗ Error parsing resume: {str(e)}")
            raise Exception(f"Error parsing resume: {str(e)}")
    
    def _create_extraction_prompt(self, resume_text: str) -> str:
        """
        Create the exact production-ready prompt for LLM
        """
        return f"""You are an expert resume parsing agent. 
Your job is to read resume text and extract **structured JSON data only**.

Follow these rules:
- Return ONLY valid JSON.
- Do not add explanations.
- Never hallucinate missing data. If not available, return null or empty array.

Extract the following fields:

{{
  "personal_info": {{
    "full_name": "",
    "email": "",
    "phone": "",
    "location": ""
  }},
  "summary": "",
  "skills": {{
    "programming_languages": [],
    "frameworks": [],
    "libraries": [],
    "databases": [],
    "cloud": [],
    "devops": [],
    "tools": [],
    "soft_skills": []
  }},
  "experience": [
    {{
      "company": "",
      "role": "",
      "start_date": "",
      "end_date": "",
      "duration_months": null,
      "summary": "",
      "technologies": []
    }}
  ],
  "education": [
    {{
      "degree": "",
      "institution": "",
      "start_year": "",
      "end_year": "",
      "gpa": null
    }}
  ],
  "projects": [
    {{
      "name": "",
      "description": "",
      "tech_stack": []
    }}
  ],
  "certifications": [],
  "languages_spoken": [],
  "years_of_experience_estimated": null,
  "primary_job_role_prediction": ""
}}

Return only JSON. No markdown, no explanations.

Resume Text:
{resume_text}
"""
    
    def _extract_json_from_response(self, response_text: str) -> Dict:
        """
        Extract and parse JSON from LLM response
        Handles cases where LLM wraps JSON in markdown code blocks
        """
        try:
            # Remove markdown code blocks if present
            text = response_text.strip()
            
            # Remove ```json and ``` markers
            if text.startswith("```json"):
                text = text[7:]
            elif text.startswith("```"):
                text = text[3:]
            
            if text.endswith("```"):
                text = text[:-3]
            
            text = text.strip()
            
            # Parse JSON
            parsed = json.loads(text)
            return parsed
        
        except json.JSONDecodeError as e:
            self.log(f"JSON parsing error: {e}")
            self.log(f"Raw response: {response_text[:500]}")
            raise Exception(f"Failed to parse JSON from LLM response: {str(e)}")
    
    def generate_search_queries(self, parsed_resume: Dict) -> List[str]:
        """
        Generate intelligent job search queries from parsed resume
        Used by Query Generator Agent (QGA)
        """
        queries = []
        
        # Extract key data
        skills = parsed_resume.get("skills", {})
        prog_langs = skills.get("programming_languages", [])[:3]
        frameworks = skills.get("frameworks", [])[:3]
        
        role_prediction = parsed_resume.get("primary_job_role_prediction", "")
        experience_years = parsed_resume.get("years_of_experience_estimated") or 0
        
        # Determine experience level
        if experience_years == 0 or experience_years < 1:
            exp_level = "fresher"
        elif experience_years < 3:
            exp_level = f"{int(experience_years)} years"
        else:
            exp_level = f"{int(experience_years)}+ years"
        
        # Generate queries
        if role_prediction:
            queries.append(f"{role_prediction} job remote")
            queries.append(f"{role_prediction} {exp_level} experience")
            queries.append(f"{role_prediction} startup job")
        
        # Skill-based queries
        for lang in prog_langs:
            queries.append(f"{lang} developer job remote")
            queries.append(f"{lang} {exp_level} job")
        
        for framework in frameworks:
            queries.append(f"{framework} developer job")
        
        # Combined queries
        if prog_langs and role_prediction:
            queries.append(f"{prog_langs[0]} {role_prediction} job")
        
        return queries[:20]  # Return top 20 queries


# ==================== INITIALIZE AGENT ====================

# Lazy initialization - will be created when first accessed
resume_agent = None

def get_resume_agent():
    """Get or create the resume agent instance"""
    global resume_agent
    if resume_agent is None:
        resume_agent = ResumeIntelligenceAgent()
    return resume_agent
