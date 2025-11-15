"""
Database utilities for Neon PostgreSQL with Prisma ORM
"""

from prisma import Prisma
from typing import Dict, Optional
import os

db = Prisma()


async def connect_db():
    """Connect to database"""
    if not db.is_connected():
        await db.connect()


async def disconnect_db():
    """Disconnect from database"""
    if db.is_connected():
        await db.disconnect()


async def save_resume_data(
    file_name: str,
    full_name: str,
    email: Optional[str],
    phone: Optional[str],
    location: Optional[str],
    summary: Optional[str],
    raw_text: Optional[str],
    user_id: Optional[str] = None,
    file_url: Optional[str] = None
) -> str:
    """
    Save parsed resume data to database
    Returns resume ID
    """
    await connect_db()
    
    resume = await db.resume.create(
        data={
            "userId": user_id,
            "fileName": file_name,
            "fileUrl": file_url,
            "fullName": full_name,
            "email": email,
            "phone": phone,
            "location": location,
            "summary": summary,
            "rawText": raw_text
        }
    )
    
    return resume.id


async def save_job_factors(
    resume_id: str,
    experience_years: float,
    job_role: str,
    tech_stack: list,
    tools: list,
    primary_skills: list,
    search_queries: list
) -> str:
    """
    Save job factors from Smart Query Agent
    Returns job_factors ID
    """
    await connect_db()
    
    job_factors = await db.jobfactors.create(
        data={
            "resumeId": resume_id,
            "experienceYears": experience_years,
            "jobRole": job_role,
            "techStack": tech_stack,
            "tools": tools,
            "primarySkills": primary_skills,
            "searchQueries": search_queries
        }
    )
    
    return job_factors.id
