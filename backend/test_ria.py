"""
Example: Testing the Resume Intelligence Agent
"""

import asyncio
from agents.resume_intelligence_agent import resume_agent
import json


async def test_resume_parser():
    """Test the RIA agent with a sample resume"""
    
    # Path to your test resume PDF
    pdf_path = "uploads/sample_resume.pdf"
    
    print("=" * 60)
    print("🤖 Resume Intelligence Agent Test")
    print("=" * 60)
    
    try:
        # Parse the resume
        print("\n📄 Parsing resume...")
        result = await resume_agent.parse_resume(pdf_path)
        
        # Display results
        print("\n✅ Parsing completed successfully!\n")
        
        # Personal Info
        print("👤 PERSONAL INFO:")
        personal = result.get("personal_info", {})
        print(f"   Name: {personal.get('full_name')}")
        print(f"   Email: {personal.get('email')}")
        print(f"   Phone: {personal.get('phone')}")
        print(f"   Location: {personal.get('location')}")
        
        # Skills
        print("\n💡 SKILLS:")
        skills = result.get("skills", {})
        print(f"   Languages: {', '.join(skills.get('programming_languages', []))}")
        print(f"   Frameworks: {', '.join(skills.get('frameworks', []))}")
        print(f"   Databases: {', '.join(skills.get('databases', []))}")
        print(f"   Cloud: {', '.join(skills.get('cloud', []))}")
        
        # Experience
        print("\n💼 EXPERIENCE:")
        experience = result.get("experience", [])
        for exp in experience:
            print(f"   {exp.get('role')} at {exp.get('company')}")
            print(f"   {exp.get('start_date')} - {exp.get('end_date')} ({exp.get('duration_months')} months)")
            print(f"   Tech: {', '.join(exp.get('technologies', []))}")
            print()
        
        # Education
        print("🎓 EDUCATION:")
        education = result.get("education", [])
        for edu in education:
            print(f"   {edu.get('degree')} - {edu.get('institution')}")
            print(f"   {edu.get('start_year')} - {edu.get('end_year')}")
            if edu.get('gpa'):
                print(f"   GPA: {edu.get('gpa')}")
            print()
        
        # Meta
        print("📊 ANALYSIS:")
        print(f"   Experience: {result.get('years_of_experience_estimated')} years")
        print(f"   Primary Role: {result.get('primary_job_role_prediction')}")
        print(f"   Certifications: {', '.join(result.get('certifications', []))}")
        
        # Search Queries
        print("\n🔍 GENERATED SEARCH QUERIES:")
        queries = resume_agent.generate_search_queries(result)
        for i, query in enumerate(queries[:10], 1):
            print(f"   {i}. {query}")
        
        # Save to JSON file
        output_file = "parsed_resume_output.json"
        with open(output_file, 'w') as f:
            json.dump(result, f, indent=2)
        
        print(f"\n💾 Full output saved to: {output_file}")
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")


if __name__ == "__main__":
    asyncio.run(test_resume_parser())
