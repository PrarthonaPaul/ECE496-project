"use client";

import { useDropzone } from 'react-dropzone';
import React, { useCallback } from 'react';
import { useState, useEffect } from 'react';

interface PDFData {
  id: number;
  title: string;
  pdf: string;
  uploaded_at: string;
}
const Upload = () => {
  const [data, setData] = useState<PDFData[] | null>(null); // Define the type for data as an array of PDFData or null
  const [title, setTitle] = useState<string>(''); // State to manage title input

  // Function to get cookie by name
  const getCookie = (name: string): string | undefined => {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);

    // Check if the parts array has at least 2 elements
    if (parts.length < 2) return undefined;

    // Return the cookie value if found
    return parts.pop()?.split(';')?.shift();
};

  // Define the onDrop callback with the upload functionality
  const onDrop = useCallback((acceptedFiles: File[]) => {
    // Initialize FormData to prepare the file for upload
    const formData = new FormData();
    // formData.append("title", "My PDF Title"); // Replace with dynamic title as needed
    acceptedFiles.forEach((file) => {
      // Set the file name as the title by removing the file extension
      const title = file.name.replace(/\.[^/.]+$/, ""); // Remove the extension
      formData.append("title", title); // Append the title
      formData.append("pdf", file); // Append the file itself
  });
    

    // Get the CSRF token from cookies
    const csrfToken = getCookie('csrftoken'); // Retrieve the CSRF token
    const headers: HeadersInit = {};
  if (csrfToken) {
    headers['X-CSRFToken'] = csrfToken; // Add the CSRF token if it exists
  }
  

  // Send the POST request to the backend
  fetch("http://localhost:8000/upload/", {
    method: "POST",
    body: formData,
    headers, // Use the headers object
    credentials: 'include',
  })
  .then(response => response.json())
  .then(data => {
    if (data.data) {
      setData(data.data); // Populate `data` state with the list of PDFs
      console.log("File uploaded successfully");
    } else {
      console.error("File upload failed");
    }
  })
  .catch(error => console.error("Error:", error));
     
  }, []);

  // Set up the Dropzone properties
  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'], // Only accept PDF files
    },
  });

  return (
    <div className="flex flex-col items-center justify-center min-h-screen">
      <h2 className="text-2xl font-bold mb-4">Attach your syllabus in PDF format.</h2>
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
      <button className="mt-4 px-4 py-2 bg-gray-200 rounded-lg hover:bg-gray-300">Cancel</button>
      {/* Render fetched PDF data only after upload */}
      {data && (
        <div>
          <h2 className="text-xl font-bold mt-8">PDF Files Data</h2>
          <ul className="text-sm text-gray-800 mt-4">
            {data.map((pdf) => (
              <li key={pdf.id}>
                <strong>{pdf.title}</strong> - Uploaded at {pdf.uploaded_at}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
};

export default Upload;



// "use client";

// import { useDropzone } from 'react-dropzone';
// import React, { useCallback, useState } from 'react';

// const Upload = () => {
//   const [data, setData] = useState(null); // State to store fetched PDF data

//   // Function to get cookie by name
//   const getCookie = (name: string): string | undefined => {
//     const value = `; ${document.cookie}`;
//     const parts = value.split(`; ${name}=`);
//     if (parts.length < 2) return undefined;
//     return parts.pop()?.split(';')?.shift();
//   };

//   // Define the onDrop callback with the upload functionality
//   const onDrop = useCallback((acceptedFiles: File[]) => {
//     const formData = new FormData();
//     acceptedFiles.forEach((file) => {
//       formData.append("file", file); // Assuming "file" is the expected key on the server
//     });

//     const csrfToken = getCookie('csrftoken');
//     const headers: HeadersInit = {};
//     if (csrfToken) {
//       headers['X-CSRFToken'] = csrfToken;
//     }

//     fetch("http://localhost:8000/upload/", {
//       method: "POST",
//       body: formData,
//       headers,
//       credentials: 'include',
//     })
//       .then(response => response.json())
//       .then(data => {
//         if (data.data) {
//           setData(data.data); // Update state with the new list of PDFs
//           console.log("File uploaded successfully");
//         } else {
//           console.error("File upload failed");
//         }
//       })
//       .catch(error => console.error("Error:", error));
//   }, []);

//   // Set up the Dropzone properties
//   const { getRootProps, getInputProps, isDragActive } = useDropzone({
//     onDrop,
//     accept: { 'application/pdf': ['.pdf'] }, // Only accept PDF files
//   });

//   return (
//     <div className="flex flex-col items-center justify-center min-h-screen">
//       <h2 className="text-2xl font-bold mb-4">Attach your syllabus in PDF format.</h2>
//       <div
//         {...getRootProps()}
//         className="border-2 border-dashed border-teal-500 rounded-lg w-3/4 h-48 flex flex-col items-center justify-center cursor-pointer"
//       >
//         <input {...getInputProps()} />
//         {isDragActive ? (
//           <p className="text-teal-500">Drop the files here...</p>
//         ) : (
//           <>
//             <svg
//               className="w-8 h-8 text-teal-500 mb-4"
//               fill="none"
//               stroke="currentColor"
//               viewBox="0 0 24 24"
//               xmlns="http://www.w3.org/2000/svg"
//             >
//               <path
//                 strokeLinecap="round"
//                 strokeLinejoin="round"
//                 strokeWidth="2"
//                 d="M7 16l4-4 4 4m0-12a4 4 0 00-8 0v4H5a2 2 0 00-2 2v4a2 2 0 002 2h14a2 2 0 002-2v-4a2 2 0 00-2-2h-3V4z"
//               ></path>
//             </svg>
//             <p className="text-teal-500">Drop a file here to upload, or click here to browse</p>
//           </>
//         )}
//       </div>
//       <button className="mt-4 px-4 py-2 bg-gray-200 rounded-lg hover:bg-gray-300">Cancel</button>

//       {/* Render fetched PDF data only after upload */}
//       {data && (
//         <div>
//           <h2 className="text-xl font-bold mt-8">PDF Files Data</h2>
//           <pre className="text-sm text-gray-800 mt-4">{JSON.stringify(data, null, 2)}</pre>
//         </div>
//       )}
//     </div>
//   );
// };

// export default Upload;
