import axios from "axios";

const API_BASE_URL =
  process.env.NEXT_PUBLIC_BACKEND_URL || "http://localhost:8000";

const apiClient = axios.create({
  baseURL: `${API_BASE_URL}/api`,
  headers: {
    "Content-Type": "application/json",
  },
});

export interface ResumeProfile {
  full_name: string;
  email?: string;
  phone?: string;
  location?: string;
  skills: string[];
  experience_years?: string;
  job_titles: string[];
  companies: string[];
  education: string[];
  projects: string[];
  certifications: string[];
  desired_roles: string[];
  preferred_locations: string[];
  job_type?: string;
  summary: string;
  raw_text?: string;
}

export interface ParseResponse {
  success: boolean;
  step1_complete: boolean;
  step2_complete: boolean;
  profile: any;
  queries_output: {
    target_role: string;
    experience_level: string;
    primary_skills: string[];
    google_search_queries: string[];
    api_queries: {
      jsearch: string[];
      jooble: string[];
    };
    wellfound_queries: string[];
    yc_queries: string[];
    company_career_pages: string[];
  };
  database: {
    resume_id: string;
    job_factors_id: string;
  };
  message: string;
}

export interface DiscoverJobsResponse {
  success: boolean;
  step1_complete: boolean;
  step2_complete: boolean;
  step3_complete: boolean;
  profile: any;
  queries_output: any;
  discovery_result: {
    jobs: Array<{
      title: string;
      company: string;
      location: string;
      experience: string;
      skills_required: string[];
      apply_url: string;
      source: string;
    }>;
    sources_scraped: Record<string, number>;
    total_jobs: number;
  };
  message: string;
}

export const uploadResumeToBackend = async (
  file: File
): Promise<{ file_id: string; filename: string }> => {
  const formData = new FormData();
  formData.append("file", file);

  const response = await apiClient.post("/upload", formData, {
    headers: {
      "Content-Type": "multipart/form-data",
    },
  });

  return response.data;
};

export const parseResume = async (fileId: string): Promise<ParseResponse> => {
  const response = await apiClient.post(`/parse/${fileId}`);
  return response.data;
};

export const getProfile = async (fileId: string): Promise<ParseResponse> => {
  const response = await apiClient.get(`/profile/${fileId}`);
  return response.data;
};

export const discoverJobs = async (
  fileId: string
): Promise<DiscoverJobsResponse> => {
  const response = await apiClient.post(`/discover-jobs/${fileId}`);
  return response.data;
};

export default apiClient;
