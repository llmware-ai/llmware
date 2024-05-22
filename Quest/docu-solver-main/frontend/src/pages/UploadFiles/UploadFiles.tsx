import React, { useState } from 'react';
import { useToast } from '@/components/ui/use-toast'; // Import useToast from the specified file
import { HiOutlineDocumentAdd, HiOutlineX } from 'react-icons/hi'; // Import icons for file upload and removal
import axios from "axios"

const UploadPage: React.FC = () => {
  const [files, setFiles] = useState<File[]>([]);
  const [analyseButtonDisabled, setAnalyseButtonDisabled] = useState(true);
  const { toast } = useToast(); // Assuming you have used react-toast-notifications

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const fileList = event.target.files;
    if (fileList) {
      const filesArray = Array.from(fileList);
      const pdfFiles = filesArray.filter(
        (file) => file.type === 'application/pdf'
      );
      setFiles((prevFiles) => [...prevFiles, ...pdfFiles]);
      setAnalyseButtonDisabled(pdfFiles.length === 0);
    }
  };

  const handleRemoveFile = (index: number) => {
    const updatedFiles = [...files];
    updatedFiles.splice(index, 1);
    setFiles(updatedFiles);
    setAnalyseButtonDisabled(updatedFiles.length === 0);
  };

  const handleFormSubmit = async  (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    const formData = new FormData();
    files.forEach((file) => {
      formData.append('file', file);
    });

    try {
       await axios.post('http://127.0.0.1:8000/api/upload-files', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      toast({
        variant: 'default',
        description: '✅ Files uploaded successfully!',
      });

      window.location.href = "http://localhost:5173/chat"; // Redirect after successful upload
    } catch (error) {
      toast({
        variant: 'destructive',
        description: `❌ Error uploading file: ${error.response?.data?.detail || error.message}`,
      });
    }

    window.location.href= "http://localhost:5173/chat"
  };

  return (
    <div className="flex justify-center items-center h-screen">
      <div className="bg-gray-100 py-12 px-12 rounded-3xl w-5/12 flex flex-col shadow-2xl">
        <div className="flex items-center justify-between mb-6 ">
          <h2 className="text-4xl font-bold text-blue-500">Upload Files</h2>
        </div>

        <form className="flex flex-col gap-6 mt-3" onSubmit={handleFormSubmit}>
          <div className="bg-white border border-gray-300 rounded-lg p-4">
            <label
              htmlFor="file"
              className="flex items-center text-xl font-medium text-gray-800 mb-2 cursor-pointer"
            >
              <HiOutlineDocumentAdd className="mr-2 w-6 h-6" />
              Choose PDF Files:
            </label>
            <div className="flex flex-col space-y-5">
              {files.length > 0 &&
                files.map((file, index) => (
                  <div
                    key={index}
                    className="flex items-center justify-between bg-gray-200 px-3 py-2 rounded-lg mt-5"
                  >
                    <span className="text-black text-base py-1 px-2 rounded-lg">
                      {file.name}
                    </span>
                    <button
                      type="button"
                      onClick={() => handleRemoveFile(index)}
                      className="flex items-center justify-center bg-red-500 text-white rounded-full h-8 w-8 hover:bg-red-600"
                    >
                      <HiOutlineX />
                    </button>
                  </div>
                ))}
              <input
                type="file"
                id="file"
                name="file"
                multiple
                accept=".pdf"
                onChange={handleFileChange}
                className="hidden"
                required
              />
            </div>
          </div>

          <button
            type="submit"
            className={`text-xl bg-green-500 hover:bg-green-600 text-white font-bold py-3 px-4 rounded-lg focus:outline-none ${
              analyseButtonDisabled && 'opacity-50 cursor-not-allowed'
            }`}
            disabled={analyseButtonDisabled}
          >
            Analyze
          </button>
        </form>
      </div>
    </div>
  );
};

export default UploadPage;
