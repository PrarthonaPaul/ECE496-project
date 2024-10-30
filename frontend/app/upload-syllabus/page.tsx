"use client";


import { useDropzone } from 'react-dropzone';
import React, { useCallback } from 'react';

const Upload = () => {
  const onDrop = useCallback(() => {
    console.log();
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({ onDrop });

  return (
    <div className="flex flex-col items-center justify-center min-h-screen">
      <h2 className="text-2xl font-bold mb-4">Attach your syllabus in PDF format.</h2>
      <div
        {...getRootProps()}
        className="border-2 border-dashed border-teal-500 rounded-lg w-3/4 h-48 flex flex-col items-center justify-center cursor-pointer"
      >
        <input {...getInputProps()} />
        {
          isDragActive ? (
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
          )
        }
      </div>
      <button className="mt-4 px-4 py-2 bg-gray-200 rounded-lg hover:bg-gray-300">Cancel</button>
    </div>
  );
};

export default Upload;
