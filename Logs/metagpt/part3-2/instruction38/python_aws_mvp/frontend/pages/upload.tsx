import React, { useState, useRef } from "react";
import Head from "next/head";
import styles from "../styles/Upload.module.css";
import { useRouter } from "next/router";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";

interface PresignedUrlResponse {
  presigned_url: string;
  file_id: string;
}

export default function UploadPage() {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [uploadProgress, setUploadProgress] = useState<number>(0);
  const [uploadStatus, setUploadStatus] = useState<string>("");
  const [errorMsg, setErrorMsg] = useState<string>("");
  const [successMsg, setSuccessMsg] = useState<string>("");
  const [isUploading, setIsUploading] = useState<boolean>(false);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const router = useRouter();

  // Helper to get JWT token from localStorage
  const getToken = () => {
    return localStorage.getItem("token");
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setErrorMsg("");
    setSuccessMsg("");
    setUploadStatus("");
    setUploadProgress(0);
    if (e.target.files && e.target.files.length > 0) {
      setSelectedFile(e.target.files[0]);
    }
  };

  const handleDrop = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setErrorMsg("");
    setSuccessMsg("");
    setUploadStatus("");
    setUploadProgress(0);
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      setSelectedFile(e.dataTransfer.files[0]);
    }
  };

  const handleDragOver = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
  };

  const requestPresignedUrl = async (file: File): Promise<PresignedUrlResponse | null> => {
    const token = getToken();
    if (!token) {
      router.push("/login");
      return null;
    }
    try {
      const res = await fetch(`${API_BASE_URL}/storage/presigned-url`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          filename: file.name,
          content_type: file.type,
        }),
      });
      if (!res.ok) {
        const data = await res.json();
        setErrorMsg(data.detail || "Failed to get presigned URL.");
        return null;
      }
      const data = await res.json();
      return data;
    } catch (err) {
      setErrorMsg("Network error while requesting presigned URL.");
      return null;
    }
  };

  const uploadFileToS3 = async (file: File, presignedUrl: string): Promise<boolean> => {
    try {
      const res = await fetch(presignedUrl, {
        method: "PUT",
        body: file,
        headers: {
          "Content-Type": file.type,
        },
      });
      if (!res.ok) {
        setErrorMsg("Failed to upload file to S3.");
        return false;
      }
      return true;
    } catch (err) {
      setErrorMsg("Network error during S3 upload.");
      return false;
    }
  };

  const validateUpload = async (file_id: string, file: File): Promise<boolean> => {
    const token = getToken();
    if (!token) {
      router.push("/login");
      return false;
    }
    try {
      const res = await fetch(`${API_BASE_URL}/storage/validate-upload`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          file_id,
          filename: file.name,
          content_type: file.type,
          size: file.size,
        }),
      });
      if (!res.ok) {
        const data = await res.json();
        setErrorMsg(data.detail || "Failed to validate upload.");
        return false;
      }
      return true;
    } catch (err) {
      setErrorMsg("Network error during upload validation.");
      return false;
    }
  };

  const handleUpload = async () => {
    setErrorMsg("");
    setSuccessMsg("");
    setUploadStatus("");
    setUploadProgress(0);

    if (!selectedFile) {
      setErrorMsg("Please select a file to upload.");
      return;
    }

    setIsUploading(true);
    setUploadStatus("Requesting presigned URL...");

    // Step 1: Request presigned URL from backend
    const presignedData = await requestPresignedUrl(selectedFile);
    if (!presignedData) {
      setIsUploading(false);
      setUploadStatus("");
      return;
    }

    setUploadStatus("Uploading to S3...");
    setUploadProgress(10);

    // Step 2: Upload file to S3 using presigned URL
    const uploadSuccess = await uploadFileToS3(selectedFile, presignedData.presigned_url);
    if (!uploadSuccess) {
      setIsUploading(false);
      setUploadStatus("");
      return;
    }

    setUploadStatus("Validating upload...");
    setUploadProgress(80);

    // Step 3: Validate upload with backend
    const validateSuccess = await validateUpload(presignedData.file_id, selectedFile);
    if (!validateSuccess) {
      setIsUploading(false);
      setUploadStatus("");
      return;
    }

    setUploadProgress(100);
    setUploadStatus("Upload complete!");
    setSuccessMsg(`File "${selectedFile.name}" uploaded successfully.`);
    setSelectedFile(null);
    setIsUploading(false);
  };

  return (
    <div className={styles.container}>
      <Head>
        <title>Upload | python_aws_mvp</title>
        <meta name="viewport" content="width=device-width, initial-scale=1" />
      </Head>
      <header className={styles.header}>
        <h1 className={styles.title}>File Upload</h1>
      </header>
      <main className={styles.main}>
        <div
          className={styles.dropZone}
          onDrop={handleDrop}
          onDragOver={handleDragOver}
          tabIndex={0}
          aria-label="Drag and drop files here"
        >
          <p>Drag and drop a file here, or</p>
          <button
            className={styles.selectButton}
            onClick={() => fileInputRef.current?.click()}
            disabled={isUploading}
          >
            Select File
          </button>
          <input
            type="file"
            ref={fileInputRef}
            style={{ display: "none" }}
            onChange={handleFileChange}
            disabled={isUploading}
          />
        </div>
        {selectedFile && (
          <div className={styles.fileInfo}>
            <strong>Selected File:</strong> {selectedFile.name} ({(selectedFile.size / 1024).toFixed(2)} KB)
          </div>
        )}
        {uploadStatus && (
          <div className={styles.status}>
            {uploadStatus}
            {isUploading && (
              <div className={styles.progressBar}>
                <div
                  className={styles.progress}
                  style={{ width: `${uploadProgress}%` }}
                />
              </div>
            )}
          </div>
        )}
        {errorMsg && <div className={styles.error}>{errorMsg}</div>}
        {successMsg && <div className={styles.success}>{successMsg}</div>}
        <button
          className={styles.uploadButton}
          onClick={handleUpload}
          disabled={!selectedFile || isUploading}
        >
          {isUploading ? "Uploading..." : "Upload"}
        </button>
      </main>
      <footer className={styles.footer}>
        &copy; {new Date().getFullYear()} python_aws_mvp &mdash; Upload
      </footer>
    </div>
  );
}