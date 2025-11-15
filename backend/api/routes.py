from fastapi import APIRouter, UploadFile, File, HTTPException
from agents.resume_intelligence_agent import get_resume_agent
from agents.smart_query_agent import get_smart_query_agent
from agents.job_discovery_agent import get_job_discovery_agent
from utils.database import save_resume_data, save_job_factors
import aiofiles
import os
from pathlib import Path
import uuid
from typing import Dict

router = APIRouter()

# Create uploads directory
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)


@router.post("/upload")
async def upload_resume(file: UploadFile = File(...)):
    """
    Upload a resume PDF file
    Returns file_id for processing
    """
    try:
        # Validate file type
        if not file.filename.endswith('.pdf'):
            raise HTTPException(status_code=400, detail="Only PDF files are allowed")
        
        # Generate unique file ID
        file_id = str(uuid.uuid4())
        file_extension = file.filename.split('.')[-1]
        file_path = UPLOAD_DIR / f"{file_id}.{file_extension}"
        
        # Save file
        async with aiofiles.open(file_path, 'wb') as out_file:
            content = await file.read()
            await out_file.write(content)
        
        return {
            "success": True,
            "file_id": file_id,
            "filename": file.filename,
            "message": "Resume uploaded successfully"
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error uploading file: {str(e)}")


@router.post("/parse/{file_id}")
async def parse_resume(file_id: str, user_id: str = None):
    """
    Parse uploaded resume and extract structured information
    Optionally stores in Firestore if user_id is provided
    
    Query params:
        user_id: Optional user identifier for Firestore storage
    """
    try:
        # Find the file
        file_path = UPLOAD_DIR / f"{file_id}.pdf"
        
        if not file_path.exists():
            raise HTTPException(status_code=404, detail="Resume file not found")
        
        # STEP 1: Parse resume using RIA agent
        ria_agent = get_resume_agent()
        profile = await ria_agent.parse_resume(str(file_path))
        
        # STEP 2: Use Smart Query Agent to extract job factors and generate 100+ queries
        sqa_agent = get_smart_query_agent()
        smart_output = await sqa_agent.execute(profile)
        
        # STEP 3: Save to Neon DB
        personal_info = profile.get("personal_info", {})
        resume_id = await save_resume_data(
            file_name=file_path.name,
            full_name=personal_info.get("full_name", ""),
            email=personal_info.get("email"),
            phone=personal_info.get("phone"),
            location=personal_info.get("location"),
            summary=profile.get("summary"),
            raw_text=profile.get("raw_text"),
            user_id=user_id
        )
        
        # Flatten all queries for DB storage
        all_queries = []
        all_queries.extend(smart_output["google_search_queries"])
        all_queries.extend(smart_output["api_queries"]["jsearch"])
        all_queries.extend(smart_output["api_queries"]["jooble"])
        all_queries.extend(smart_output["wellfound_queries"])
        all_queries.extend(smart_output["yc_queries"])
        
        job_factors_id = await save_job_factors(
            resume_id=resume_id,
            experience_years=float(smart_output.get("experience_level", "0").split("(")[-1].split(" ")[0]) if "(" in smart_output.get("experience_level", "0") else 0,
            job_role=smart_output["target_role"],
            tech_stack=smart_output["primary_skills"],
            tools=[],
            primary_skills=smart_output["primary_skills"],
            search_queries=all_queries
        )
        
        return {
            "success": True,
            "step1_complete": True,
            "step2_complete": True,
            "profile": profile,
            "queries_output": smart_output,
            "database": {
                "resume_id": resume_id,
                "job_factors_id": job_factors_id
            },
            "message": f"Resume parsed and {len(all_queries)} queries generated"
        }
    
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"❌ Error parsing resume: {str(e)}")
        print(f"Full traceback:\n{error_details}")
        raise HTTPException(status_code=500, detail=f"Error parsing resume: {str(e)}")


@router.get("/profile/{file_id}")
async def get_profile(file_id: str):
    """
    Get parsed profile for a file ID
    (In production, this would fetch from database)
    """
    try:
        file_path = UPLOAD_DIR / f"{file_id}.pdf"
        
        if not file_path.exists():
            raise HTTPException(status_code=404, detail="Resume not found")
        
        # Parse again (in production, fetch from DB)
        agent = get_resume_agent()
        profile = await agent.parse_resume(str(file_path))
        
        return {
            "success": True,
            "profile": profile
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving profile: {str(e)}")


@router.post("/discover-jobs/{file_id}")
async def discover_jobs(file_id: str, user_id: str = None):
    """
    Step 3: Job Discovery Agent - Scrape jobs from multiple sources
    Uses queries from SQA to discover jobs from:
    - JSearch & Jooble APIs
    - Wellfound & YCombinator job boards
    - Google Search results
    - Company career pages (100+ companies)
    """
    try:
        file_path = UPLOAD_DIR / f"{file_id}.pdf"
        if not file_path.exists():
            raise HTTPException(status_code=404, detail="Resume file not found")
        
        # STEP 1: Parse resume using RIA agent
        ria_agent = get_resume_agent()
        profile = await ria_agent.parse_resume(str(file_path))
        
        # STEP 2: Use Smart Query Agent to generate queries
        sqa_agent = get_smart_query_agent()
        smart_output = await sqa_agent.execute(profile)
        
        # STEP 3: Use Job Discovery Agent to scrape jobs
        jda_agent = get_job_discovery_agent()
        discovery_result = await jda_agent.execute(smart_output)
        
        # Close HTTP client
        await jda_agent.close()
        
        return {
            "success": True,
            "step1_complete": True,
            "step2_complete": True,
            "step3_complete": True,
            "profile": profile,
            "queries_output": smart_output,
            "discovery_result": discovery_result,
            "message": f"Discovered {discovery_result['total_jobs']} jobs from {len(discovery_result['sources_scraped'])} sources"
        }
    
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"❌ Error in job discovery: {str(e)}")
        print(f"Full traceback:\n{error_details}")
        raise HTTPException(status_code=500, detail=f"Error discovering jobs: {str(e)}")
