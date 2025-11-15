import { storage } from "./firebase";
import { ref, uploadBytesResumable, getDownloadURL } from "firebase/storage";

export interface UploadProgress {
  progress: number;
  status: "uploading" | "success" | "error";
  downloadURL?: string;
  error?: string;
}

export const uploadResumeToFirebase = (
  file: File,
  onProgress: (progress: UploadProgress) => void
): Promise<string> => {
  return new Promise((resolve, reject) => {
    // Create a unique filename
    const timestamp = Date.now();
    const filename = `resumes/${timestamp}_${file.name}`;

    // Create storage reference
    const storageRef = ref(storage, filename);

    // Start upload
    const uploadTask = uploadBytesResumable(storageRef, file);

    uploadTask.on(
      "state_changed",
      (snapshot) => {
        // Track upload progress
        const progress =
          (snapshot.bytesTransferred / snapshot.totalBytes) * 100;
        onProgress({
          progress,
          status: "uploading",
        });
      },
      (error) => {
        // Handle upload error
        onProgress({
          progress: 0,
          status: "error",
          error: error.message,
        });
        reject(error);
      },
      async () => {
        // Handle successful upload
        try {
          const downloadURL = await getDownloadURL(uploadTask.snapshot.ref);
          onProgress({
            progress: 100,
            status: "success",
            downloadURL,
          });
          resolve(downloadURL);
        } catch (error) {
          reject(error);
        }
      }
    );
  });
};
