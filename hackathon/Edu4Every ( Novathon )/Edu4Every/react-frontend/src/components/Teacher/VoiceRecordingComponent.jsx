import React, { useState, useRef } from 'react';
import axios from 'axios';
import { jsPDF } from 'jspdf';
import { MicrophoneIcon, PauseIcon, StopIcon,SparklesIcon } from '@heroicons/react/24/solid';

const VoiceRecordingComponent = () => {
    const [isRecording, setIsRecording] = useState(false);
    const [isPaused, setIsPaused] = useState(false);
    const [audioBlob, setAudioBlob] = useState(null);
    const [audioUrl, setAudioUrl] = useState(null);
    const [transcriptionData, setTranscriptionData] = useState([]);
    const [loading, setLoading] = useState(false);
    const [imageLoading, setImageLoading] = useState(false);
    const [disableDownload, setDisableDownload] = useState(true); // Initially disable download button
    const mediaRecorderRef = useRef(null);

    const startRecording = async () => {
        if (isPaused) {
            resumeRecording();
        } else {
            try {
                const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
                mediaRecorderRef.current = new MediaRecorder(stream);
                const chunks = [];
                mediaRecorderRef.current.ondataavailable = (e) => { chunks.push(e.data); };
                mediaRecorderRef.current.onstop = () => {
                    const audioBlob = new Blob(chunks, { type: 'audio/wav' });
                    setAudioBlob(audioBlob);
                    const audioUrl = URL.createObjectURL(audioBlob);
                    setAudioUrl(audioUrl);
                };
                mediaRecorderRef.current.start();
                setIsRecording(true);
                setIsPaused(false);
            } catch (err) {
                console.error('Error starting recording:', err);
            }
        }
    };

    const pauseRecording = () => {
        if (mediaRecorderRef.current) {
            mediaRecorderRef.current.pause();
            setIsPaused(true);
        }
    };

    const resumeRecording = () => {
        if (mediaRecorderRef.current) {
            mediaRecorderRef.current.resume();
            setIsPaused(false);
        }
    };

    const stopRecording = () => {
        if (mediaRecorderRef.current) {
            mediaRecorderRef.current.stop();
            const tracks = mediaRecorderRef.current.stream.getTracks();
            tracks.forEach((track) => track.stop());
            setIsRecording(false);
            setIsPaused(false);
        }
    };

    const sendTranscript = async () => {
        if (!audioBlob) return;
        const formData = new FormData();
        formData.append('file', audioBlob, 'recording.wav');
        setLoading(true);
        try {
            const response = await axios.post(
                'https://5940-111-92-80-102.ngrok-free.app/transcribe-audio/transcribe-and-summarize',
                formData,
                { headers: { 'Content-Type': 'multipart/form-data' } }
            );
            console.log('Transcript received:', response.data);
            setTranscriptionData(Array.isArray(response.data) ? response.data : [response.data]); // Handle array or single object
            // Enable download button after receiving transcription
            setDisableDownload(false); 
        } catch (error) {
            console.error('Error during transcription:', error.response ? error.response.data : error.message);
        } finally {
            setLoading(false);
        }
    };

    const fetchImageForTopic = async (topic, index) => {
        setImageLoading(true);
        try {
            const response = await axios.post(
                `https://5940-111-92-80-102.ngrok-free.app/search-image/search-image?query=${encodeURIComponent(topic)}`,
                {},
                { headers: { 'accept': 'application/json' } }
            );
            console.log('Image fetched:', response.data);
            if (response.data?.image_url) {
                // Update transcription data with image URL
                setTranscriptionData((prevData) => 
                    prevData.map((item, idx) =>
                        idx === index ? { ...item, imageUrl: response.data.image_url } : item
                    )
                );
            }
        } catch (error) {
            console.error('Error fetching image:', error.response ? error.response.data : error.message);
        } finally {
            // Enable download button regardless of success or failure
            setImageLoading(false); 
            setDisableDownload(false); 
        }
    };

    const downloadTranscription = () => {
        if (!transcriptionData.length) return;
    
        const doc = new jsPDF();
        const pageWidth = doc.internal.pageSize.getWidth();
        const pageHeight = doc.internal.pageSize.getHeight();
        const margin = 10;
        const maxWidth = pageWidth - margin * 2; // Ensure text fits within the page width
    
        let y = margin;
    
        transcriptionData.forEach(({ topic, notes, imageUrl }, index) => {
            if (y + 10 > pageHeight - margin) {
                doc.addPage(); // Add a new page if content exceeds current page
                y = margin;
            }
    
            // Add the topic in bold
            doc.setFont('Helvetica', 'bold');
            doc.text(`Topic ${index + 1}: ${topic}`, margin, y);
            y += 10;
    
            // Add the image if it exists
            if (imageUrl) {
                // Convert image URL to base64 format before adding it
                const img = new Image();
                img.onload = function () {
                    const imgWidth = maxWidth; // Fixed width for the image
                    const imgHeight = (50 * imgWidth) / 100; // Maintain aspect ratio; adjust height as needed
    
                    // Draw the image on the PDF
                    doc.addImage(img, 'JPEG', margin, y, imgWidth, imgHeight);
                    y += imgHeight + 10; // Move down after adding image
    
                    // After adding image, continue adding text and save the PDF if all content is added
                    addTextAndSavePDF(doc, transcriptionData, y, margin, pageHeight, maxWidth);
                };
    
                img.onerror = function () {
                    console.error('Error loading image.');
                };
    
                img.src = imageUrl;
            } else {
                // If no image, directly add text content
                addTextAndSavePDF(doc, transcriptionData, y, margin, pageHeight, maxWidth);
            }
        });
    };
    
    const addTextAndSavePDF = (doc, transcriptionData, y, margin, pageHeight, maxWidth) => {
        transcriptionData.forEach(({ notes }, index) => {
            if (y + 10 > pageHeight - margin) {
                doc.addPage(); // Add a new page if content exceeds current page
                y = margin;
            }
    
            // Add the notes with line wrapping
            doc.setFont('Helvetica', 'normal');
            const lines = doc.splitTextToSize(`Note: ${notes}`, maxWidth);
            lines.forEach((line) => {
                if (y + 10 > pageHeight - margin) {
                    doc.addPage();
                    y = margin;
                }
                doc.text(line, margin, y);
                y += 10;
            });
        });
    
        doc.save('transcription.pdf');
    };
    
    return (
        <div className="fixed top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 bg-white shadow-xl rounded-lg p-6 w-1/2 max-w-4xl h-500 overflow-auto">
 <div className="text-center h-full" >
                    <h1 className="text-3xl font-bold text-gray-800 flex items-center justify-center h-12">
                        <SparklesIcon className="h-8 w-8 mr-3 text-purple-600" />
                        Voice Insight
                    </h1>
                    <p className="text-gray-600 mt-2">Record, transcribe, and generate insights from your audio</p>
                </div>

            
            <div className="flex justify-center items-center space-x-4">
                <button onClick={startRecording} className={`bg-gray-300 text-gray-700 p-3 rounded-full hover:bg-gray-400 disabled:opacity-50 ${isRecording ? 'bg-green-500' : ''}`} disabled={isRecording && !isPaused}>
                    <MicrophoneIcon className="h-6 w-6" />
                </button>
                
                <button onClick={pauseRecording} className="bg-yellow-500 text-white p-3 rounded-full hover:bg-yellow-600 disabled:opacity-50" disabled={!isRecording || isPaused}>
                    <PauseIcon className="h-6 w-6" />
                </button>
                
                <button onClick={stopRecording} className="bg-red-500 text-white p-3 rounded-full hover:bg-red-600 disabled:opacity-50" disabled={!isRecording}>
                    <StopIcon className="h-6 w-6" />
                </button>
            </div>

            {audioUrl && (
                <div className="mt-4 text-center">
                    <audio controls src={audioUrl} className="w-full max-w-xs mx-auto" />
                </div>
            )}

            {audioBlob && (
                <div className="mt-6">
                    <button onClick={sendTranscript} className="w-full bg-blue-500 text-white py-3 rounded-lg hover:bg-blue-600 transition-colors disabled:opacity-50" disabled={loading}>
                        {loading ? 'Processing...' : 'Send Transcript'}
                    </button>
                </div>
            )}

            {transcriptionData.length > 0 && (
                <div className="mt-6">
                    <h3 className="text-lg font-bold text-gray-700">Transcription:</h3>
                    <ul className="bg-gray-100 p-3 rounded-lg mt-2 text-gray-600 max-h-64 overflow-y-auto">
                        {transcriptionData.map((item, index) => (
                            <li key={index} className="mb-4">
                                <strong>{`Topic ${index + 1}: ${item.topic}`}</strong>
                                {item.imageUrl && (
                                    <img 
                                        src={item.imageUrl} 
                                        alt="Topic illustration" 
                                        className="my-2" 
                                        style={{ maxWidth: '100%', maxHeight: '200px' }}  // Ensure the image is displayed properly
                                    />
                                )}
                                <p className="ml-2">{item.notes}</p>
                                <button 
                                    onClick={() => fetchImageForTopic(item.topic, index)} 
                                    className="mt-2 bg-green-500 text-white px-4 py-2 rounded-lg hover:bg-green-600 disabled:opacity-50" 
                                    disabled={imageLoading || disableDownload}
                                >
                                    {imageLoading ? 'Loading Image...' : 'Reload Image'}
                                </button>
                            </li>
                        ))}
                    </ul>

                    <button 
                        onClick={downloadTranscription} 
                        className="w-full bg-purple-500 text-white py-3 rounded-lg hover:bg-purple-600 transition-colors disabled:opacity-50 mt-4" 
                        disabled={disableDownload}
                    >
                        Download PDF
                    </button>
                </div>
            )}
        </div>
    );
};

export default VoiceRecordingComponent;