import React, { useState } from 'react';
import Navbar from '../components/Navbar';
import Footer from '../components/Footer';
import { json, useNavigate } from 'react-router-dom';
import axios from 'axios';

const Home = () => {
    const navigate = useNavigate();
    const [selectedFile, setSelectedFile] = useState(null);
    const [loading, setLoading] = useState(false);

    const handleFileChange = (e) => {
        setSelectedFile(e.target.files[0]);
    };

    const handleUpload = async (e) => {
        e.preventDefault();
        if (!selectedFile) {
            alert("Please select a file first!");
            return;
        }

        const formDataSummary = new FormData();
        formDataSummary.append('file', selectedFile);
        formDataSummary.append('function_name', 'get_summary');
        formDataSummary.append('page_no', 0);

        const formDataTitle = new FormData();
        formDataTitle.append('file', selectedFile);
        formDataTitle.append('function_name', 'get_topic');
        formDataTitle.append('page_no', 0);

        const formDataTags = new FormData();
        formDataTags.append('file', selectedFile);
        formDataTags.append('function_name', 'get_tags');
        formDataTags.append('page_no', 0);



        setLoading(true);
        try {
            const response = await axios.post('http://127.0.0.1:8000/process_pdf/', formDataSummary, {
                headers: {
                    'Content-Type': 'multipart/form-data',
                },
            });
            console.log(response)

            const responseTitle = await axios.post('http://127.0.0.1:8000/process_pdf/', formDataTitle, {
                headers: {
                    'Content-Type': 'multipart/form-data',
                },
            });

            const responseTags = await axios.post('http://127.0.0.1:8000/process_pdf/', formDataTags, {
                headers: {
                    'Content-Type': 'multipart/form-data',
                },
            });
            // console.log("Tag response=", responseTags)
            const tagsArray = responseTags.data.result.tags
            const cleanedString = tagsArray
                .slice(1, -1)  // Remove the square brackets at the start and end
                .split(/",\s*"/)  // Split by ", " while keeping quotes intact
                .filter(tag => !tag.includes('\"s'))  // Filter out elements containing '\"s'
                .map(tag => `"${tag}"`)  // Add quotes back to each element
                .join(', ');  // Join them back into a string with commas


            const parsedArray = JSON.parse(`[${cleanedString.slice(1, -1)}]`);
            // console.log(parsedArray.slice(0, 5));
            // Determine the final array based on its size
            const finalArray = parsedArray.length > 5 ? parsedArray.slice(0, 5) : parsedArray;
            // console.log(response.data.totalpages);
            navigate('/summary', {
                state: {
                    response: response.data.result,
                    selectedFile,
                    tagData: finalArray,
                    title: responseTitle.data.result.topics,
                    totalPages: response.data.totalpages,
                }
            });

        } catch (error) {
            console.error("There was an error uploading the file!", error);
        }
        setLoading(false);
    };


    return (
        <>
            <div className="flex flex-col min-h-screen">
                <Navbar />
                {loading == true && (
                    <div className="flex flex-1 items-center justify-center bg-white py-12 px-4 sm:px-6 lg:px-8">
                        <button
                            disabled
                            type="button"
                            className="py-4 px-8 text-lg font-medium text-gray-900 bg-gray-100 rounded-lg border border-gray-200 hover:bg-gray-100 hover:text-blue-700 focus:z-10 focus:ring-2 focus:ring-blue-700 focus:text-blue-700 inline-flex items-center"
                        >
                            <svg
                                aria-hidden="true"
                                role="status"
                                className="inline w-6 h-6 mr-4 text-gray-200 animate-spin"
                                viewBox="0 0 100 101"
                                fill="none"
                                xmlns="http://www.w3.org/2000/svg"
                            >
                                <path
                                    d="M100 50.5908C100 78.2051 77.6142 100.591 50 100.591C22.3858 100.591 0 78.2051 0 50.5908C0 22.9766 22.3858 0.59082 50 0.59082C77.6142 0.59082 100 22.9766 100 50.5908ZM9.08144 50.5908C9.08144 73.1895 27.4013 91.5094 50 91.5094C72.5987 91.5094 90.9186 73.1895 90.9186 50.5908C90.9186 27.9921 72.5987 9.67226 50 9.67226C27.4013 9.67226 9.08144 27.9921 9.08144 50.5908Z"
                                    fill="currentColor"
                                />
                                <path
                                    d="M93.9676 39.0409C96.393 38.4038 97.8624 35.9116 97.0079 33.5539C95.2932 28.8227 92.871 24.3692 89.8167 20.348C85.8452 15.1192 80.8826 10.7238 75.2124 7.41289C69.5422 4.10194 63.2754 1.94025 56.7698 1.05124C51.7666 0.367541 46.6976 0.446843 41.7345 1.27873C39.2613 1.69328 37.813 4.19778 38.4501 6.62326C39.0873 9.04874 41.5694 10.4717 44.0505 10.1071C47.8511 9.54855 51.7191 9.52689 55.5402 10.0491C60.8642 10.7766 65.9928 12.5457 70.6331 15.2552C75.2735 17.9648 79.3347 21.5619 82.5849 25.841C84.9175 28.9121 86.7997 32.2913 88.1811 35.8758C89.083 38.2158 91.5421 39.6781 93.9676 39.0409Z"
                                    fill="#1C64F2"
                                />
                            </svg>
                            Your File is being processed...
                        </button>
                    </div>
                )}
                {loading == false &&
                    <main className="flex flex-1 items-center justify-center bg-white py-12 px-4 sm:px-6 lg:px-8">
                        <div className="mx-auto w-full max-w-md space-y-8 bg-gray-100 p-8 rounded-lg shadow-2xl">
                            <div className="space-y-2 text-center">
                                <h2 className="text-3xl font-extrabold text-gray-900">Upload a PDF</h2>
                                <p className="text-gray-600">Select a PDF file to upload.</p>
                            </div>
                            <form className="mt-8 space-y-6" onSubmit={handleUpload}>
                                <div className="space-y-1">
                                    <label htmlFor="file" className="block text-sm font-medium text-gray-700">
                                        PDF File
                                    </label>
                                    <input
                                        accept=".pdf"
                                        className="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
                                        id="file"
                                        required
                                        type="file"
                                        onChange={handleFileChange}
                                    />
                                </div>
                                <button
                                    type="submit"
                                    className="group relative w-full flex justify-center py-2 px-4 border border-transparent text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
                                >
                                    Upload
                                </button>
                            </form>
                        </div>
                    </main>
                }
                <Footer />
            </div>
        </>
    );
};

export default Home;
