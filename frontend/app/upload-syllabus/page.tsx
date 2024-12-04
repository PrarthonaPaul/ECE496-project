"use client";

import { useDropzone } from "react-dropzone";
import React, { useCallback, useState } from "react";
import LoadingPage from "./loading/page"; 

const Upload = () => {
  const [title, setTitle] = useState("");
  const [isUploading, setIsUploading] = useState(false); 
  const [tasks, setTasks] = useState([]); 

  const onDrop = useCallback(
    async (acceptedFiles) => {
      if (acceptedFiles.length === 0) return;

      const formData = new FormData();
      formData.append("pdf", acceptedFiles[0]); 

      setIsUploading(true); 

      try {
        const response = await fetch("http://127.0.0.1:8000/upload/", {
          method: "POST",
          body: formData,
        });

        if (response.ok) {
          const data = await response.json();
          setTasks(data.extract_tasks || []); 
          alert("File uploaded successfully!");
        } else {
          console.error("Upload failed", response.statusText);
          alert("Failed to upload the file.");
        }
      } catch (error) {
        console.error("Error uploading file", error);
        alert("An error occurred during upload.");
      } finally {
        setIsUploading(false); 
      }
    },
    [title]
  );

  const { getRootProps, getInputProps, isDragActive } = useDropzone({ onDrop });

  // Conditional rendering for loading page
  if (isUploading) {
    return <LoadingPage />;
  }

  return (
    <div className="flex flex-col items-center justify-center min-h-screen">
      <h2 className="text-2xl font-bold mb-4">Attach your syllabus in PDF format.</h2>

      {/* Dropzone Area */}
      <div
        {...getRootProps()}
        className="border-2 border-dashed border-teal-500 rounded-lg w-3/4 h-48 flex flex-col items-center justify-center cursor-pointer"
      >
        <input {...getInputProps()} />
        {isDragActive ? (
          <p className="text-teal-500">Drop the files here...</p>
        ) : (
          <>
            <svg
              className="w-8 h-8 text-teal-500 mb-4"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
              xmlns="http://www.w3.org/2000/svg"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth="2"
                d="M7 16l4-4 4 4m0-12a4 4 0 00-8 0v4H5a2 2 0 00-2 2v4a2 2 0 002 2h14a2 2 0 002-2v-4a2 2 0 00-2-2h-3V4z"
              ></path>
            </svg>
            <p className="text-teal-500">Drop a file here to upload, or click here to browse</p>
          </>
        )}
      </div>

      {/* Display Extracted Tasks */}
      {tasks.length > 0 && (
        <div className="mt-8 w-3/4">
          <h3 className="text-xl font-semibold mb-4">Extracted Tasks:</h3>
          <ul className="list-disc pl-5">
            {tasks.map((task, index) => (
              <li key={index} className="mb-2">
                {task}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
};

export default Upload;
