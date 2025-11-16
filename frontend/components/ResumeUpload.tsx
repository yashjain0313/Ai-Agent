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

    setError("");
    setDiscoveryResult(null);
    setUploading(true);

    try {
      const { file_id } = await uploadResumeToBackend(file);
      setFileId(file_id);

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
    <div className="min-h-screen bg-white text-black">
      <div className="max-w-7xl mx-auto px-4 py-8">
        {/* Header */}
        <div className="border-b border-black pb-6 mb-8">
          <h1 className="text-4xl font-bold text-black mb-2">
            AI Job Discovery Platform
          </h1>
          <p className="text-gray-600">
            Upload resume, get real jobs from 100+ sources worldwide
          </p>
        </div>

        {/* Upload Area */}
        <div
          {...getRootProps()}
          className={`border-2 ${
            isDragActive
              ? "border-black bg-gray-50"
              : "border-gray-300 hover:border-black"
          } cursor-pointer transition-colors mb-8`}
        >
          <input {...getInputProps()} />
          <div className="p-16 text-center">
            {!uploading ? (
              <div className="space-y-3">
                <Upload className="mx-auto h-12 w-12 text-black" />
                <div>
                  <p className="text-lg font-medium text-black">
                    {isDragActive
                      ? "Drop PDF here"
                      : "Drop PDF or click to upload"}
                  </p>
                  <p className="text-sm text-gray-500 mt-1">PDF format only</p>
                </div>
              </div>
            ) : (
              <div className="space-y-3">
                <Loader2 className="mx-auto h-12 w-12 text-black animate-spin" />
                <p className="text-black">
                  Analyzing resume and discovering jobs
                </p>
                <p className="text-sm text-gray-500">30-60 seconds</p>
              </div>
            )}
          </div>
        </div>

        {/* Error */}
        {error && (
          <div className="border-2 border-black bg-white p-4 mb-8">
            <p className="text-black">{error}</p>
          </div>
        )}

        {/* Jobs Display */}
        {discoveryResult && (
          <div className="space-y-6">
            {/* Stats */}
            <div className="border-2 border-black bg-black text-white p-6">
              <h2 className="text-2xl font-bold mb-1">
                {discoveryResult.total_jobs} Jobs Found
              </h2>
              <p className="text-gray-300">Matched from global sources</p>
            </div>

            {/* Job Listings */}
            <div className="space-y-3">
              {discoveryResult.jobs.map((job: any, idx: number) => (
                <div
                  key={idx}
                  className="border-2 border-black p-6 hover:bg-gray-50 transition-colors"
                >
                  <div className="mb-4">
                    <div className="flex items-start justify-between gap-4 mb-2">
                      <h3 className="text-xl font-bold text-black">
                        {job.title}
                      </h3>
                      <span className="px-2 py-1 bg-black text-white text-xs font-mono shrink-0">
                        {job.source}
                      </span>
                    </div>
                    <p className="text-lg text-black font-medium">
                      {job.company}
                    </p>
                  </div>

                  <div className="flex gap-6 text-sm text-gray-600 mb-4">
                    <span>Location: {job.location}</span>
                    <span>Experience: {job.experience}</span>
                  </div>

                  {job.skills_required && job.skills_required.length > 0 && (
                    <div className="flex flex-wrap gap-2 mb-4">
                      {job.skills_required
                        .slice(0, 6)
                        .map((skill: string, i: number) => (
                          <span
                            key={i}
                            className="px-2 py-1 border border-black text-xs text-black"
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
                    className="inline-block px-6 py-2 bg-black text-white font-medium hover:bg-gray-800 transition-colors"
                  >
                    Apply Now
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
