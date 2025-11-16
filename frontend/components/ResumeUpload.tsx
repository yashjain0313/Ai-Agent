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
    <div className="min-h-screen bg-black text-white">
      <div className="max-w-6xl mx-auto px-4 py-12 space-y-8">
        {/* Header */}
        <div className="border-b border-gray-800 pb-8">
          <h1 className="text-4xl md:text-5xl font-bold text-white mb-3">
            AI Job Discovery Platform
          </h1>
          <p className="text-gray-400 text-lg">
            Upload resume, get real jobs from 100+ sources worldwide
          </p>
        </div>

        {/* Upload Area */}
        <div
          {...getRootProps()}
          className={`rounded-none border-2 border-dashed ${
            isDragActive
              ? "border-white bg-gray-900"
              : "border-gray-700 hover:border-gray-500 bg-gray-950"
          } cursor-pointer transition-colors`}
        >
          <input {...getInputProps()} />
          <div className="p-12 text-center">
            {!uploading ? (
              <div className="space-y-3">
                <Upload className="mx-auto h-12 w-12 text-gray-400" />
                <div>
                  <p className="text-lg font-medium text-white">
                    {isDragActive
                      ? "Drop PDF here"
                      : "Drop PDF or click to upload"}
                  </p>
                  <p className="text-sm text-gray-500 mt-1">PDF format only</p>
                </div>
              </div>
            ) : (
              <div className="space-y-3">
                <Loader2 className="mx-auto h-12 w-12 text-white animate-spin" />
                <p className="text-white">
                  Analyzing resume and discovering jobs
                </p>
                <p className="text-sm text-gray-500">30-60 seconds</p>
              </div>
            )}
          </div>
        </div>

        {/* Error */}
        {error && (
          <div className="border border-red-600 bg-red-950/30 p-4">
            <p className="text-red-300">{error}</p>
          </div>
        )}

        {/* Jobs Display */}
        {discoveryResult && (
          <div className="space-y-6">
            {/* Stats */}
            <div className="bg-white text-black p-6 border border-gray-200">
              <h2 className="text-3xl font-bold mb-1">
                {discoveryResult.total_jobs} Jobs Found
              </h2>
              <p className="text-gray-700">Matched from global sources</p>
            </div>

            {/* Job Listings */}
            <div className="space-y-3">
              {discoveryResult.jobs.map((job: any, idx: number) => (
                <div
                  key={idx}
                  className="border border-gray-800 bg-gray-950 p-6 hover:border-gray-600 transition-colors"
                >
                  <div className="mb-4">
                    <div className="flex items-start justify-between gap-4 mb-2">
                      <h3 className="text-xl font-bold text-white">
                        {job.title}
                      </h3>
                      <span className="px-2 py-1 bg-white/10 text-white text-xs font-mono border border-white/20 shrink-0">
                        {job.source}
                      </span>
                    </div>
                    <p className="text-lg text-gray-200 font-medium">
                      {job.company}
                    </p>
                  </div>

                  <div className="flex gap-6 text-sm text-gray-400 mb-4">
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
                            className="px-2 py-1 border border-white/30 text-xs text-gray-200"
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
                    className="inline-block px-6 py-2 bg-white text-black font-semibold hover:bg-gray-200 transition-colors"
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
