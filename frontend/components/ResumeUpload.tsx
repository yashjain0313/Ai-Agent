"use client";

import React, { useCallback, useState } from "react";
import { useDropzone } from "react-dropzone";
import { Upload, Loader2 } from "lucide-react";
import { uploadResumeToBackend, discoverJobs } from "@/lib/api";

export default function ResumeUpload() {
  const [uploading, setUploading] = useState(false);
  const [fileId, setFileId] = useState<string>("");
  const [discoveryResult, setDiscoveryResult] = useState<any>(null);
  const [error, setError] = useState<string>("");

  const onDrop = useCallback(async (acceptedFiles: File[]) => {
    const file = acceptedFiles[0];
    if (!file) return;

    // Reset
    setError("");
    setDiscoveryResult(null);
    setUploading(true);

    try {
      // Upload
      const { file_id } = await uploadResumeToBackend(file);
      setFileId(file_id);

      // Auto-trigger job discovery (runs RIA + SQA + JDA in backend)
      const result = await discoverJobs(file_id);
      setDiscoveryResult(result.discovery_result);
      setUploading(false);
    } catch (err: any) {
      setError(err.message || "An error occurred");
      setUploading(false);
    }
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: { "application/pdf": [".pdf"] },
    maxFiles: 1,
    multiple: false,
  });

  return (
    <div className="min-h-screen bg-black text-white py-12 px-4">
      <div className="max-w-6xl mx-auto space-y-8">
        {/* Header */}
        <div className="text-center border-b border-gray-800 pb-8">
          <h1 className="text-5xl font-bold bg-gradient-to-r from-white to-gray-500 bg-clip-text text-transparent mb-4">
            AI Job Discovery Platform
          </h1>
          <p className="text-gray-400 text-lg">
            Upload Resume → Get Real Jobs from 100+ Sources Worldwide
          </p>
        </div>

        {/* Upload Area */}
        <div
          {...getRootProps()}
          className={`border-2 border-dashed rounded-xl p-12 text-center cursor-pointer transition-all duration-200 ${
            isDragActive
              ? "border-white bg-gray-900"
              : "border-gray-700 hover:border-gray-500 bg-gray-950"
          }`}
        >
          <input {...getInputProps()} />
          {!uploading ? (
            <div className="space-y-4">
              <Upload className="mx-auto h-16 w-16 text-gray-500" />
              <div>
                <p className="text-xl font-semibold text-gray-300">
                  {isDragActive ? "Drop here" : "Drop PDF or Click"}
                </p>
                <p className="text-sm text-gray-500 mt-2">
                  Supports PDF resumes only
                </p>
              </div>
            </div>
          ) : (
            <div className="space-y-4">
              <Loader2 className="mx-auto h-16 w-16 text-white animate-spin" />
              <p className="text-gray-300">
                Analyzing resume and discovering jobs...
              </p>
              <p className="text-sm text-gray-500">
                This may take 30-60 seconds
              </p>
            </div>
          )}
        </div>

        {/* Error */}
        {error && (
          <div className="bg-red-950 border border-red-800 rounded-lg p-4">
            <p className="text-red-400">{error}</p>
          </div>
        )}

        {/* Jobs Display */}
        {discoveryResult && (
          <div className="space-y-6">
            {/* Header Stats */}
            <div className="bg-gradient-to-r from-blue-600 to-purple-600 rounded-xl p-6 text-center">
              <h2 className="text-3xl font-bold text-white mb-2">
                {discoveryResult.total_jobs} Jobs Found
              </h2>
              <p className="text-blue-100">
                Matched to your resume from global sources
              </p>
            </div>

            {/* Job Listings */}
            <div className="space-y-4">
              {discoveryResult.jobs.map((job: any, idx: number) => (
                <div
                  key={idx}
                  className="bg-gray-950 border border-gray-800 rounded-xl p-6 hover:border-gray-600 hover:shadow-xl transition-all"
                >
                  <div className="flex justify-between items-start mb-3">
                    <div className="flex-1">
                      <h3 className="text-white font-bold text-xl mb-1">
                        {job.title}
                      </h3>
                      <span className="px-2 py-1 mt-1 mb-1 bg-blue-900/30 border border-blue-700 text-blue-300 text-xs rounded">
                        {job.source}
                      </span>
                      <p className="text-gray-300 font-medium text-lg">
                        {job.company}
                      </p>
                    </div>
                  </div>
                  <div className="flex items-center gap-6 text-gray-400 mb-4">
                    <span className="flex items-center gap-1">
                      📍 {job.location}
                    </span>
                    <span className="flex items-center gap-1">
                      💼 {job.experience}
                    </span>
                  </div>
                  {job.skills_required && job.skills_required.length > 0 && (
                    <div className="flex flex-wrap gap-2 mb-4">
                      {job.skills_required
                        .slice(0, 6)
                        .map((skill: string, i: number) => (
                          <span
                            key={i}
                            className="px-3 py-1 bg-gray-900 border border-gray-700 rounded-full text-sm text-gray-300"
                          >
                            {skill}
                          </span>
                        ))}
                    </div>
                  )}
                  <a
                    href={job.apply_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-flex items-center gap-2 px-6 py-3 bg-gradient-to-r from-green-600 to-emerald-600 hover:from-green-700 hover:to-emerald-700 text-white font-semibold rounded-lg transition-all"
                  >
                    Apply Now →
                  </a>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
