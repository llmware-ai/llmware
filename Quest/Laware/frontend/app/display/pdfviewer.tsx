// 'use client'

// import { useEffect, useRef, useState } from 'react';
// import * as pdfjs from 'pdfjs-dist/legacy/build/pdf';
// import { PDFDocumentProxy, PDFPageProxy } from 'pdfjs-dist/types/src/display/api';

// pdfjs.GlobalWorkerOptions.workerSrc = `//cdnjs.cloudflare.com/ajax/libs/pdf.js/${pdfjs.version}/pdf.worker.js`;

// interface PdfViewerProps {
//   fileUrl: string;
//   pageNumber: number;
// }

// const pdfviewer: React.FC<PdfViewerProps> = ({ fileUrl, pageNumber }) => {
//   const [pdf, setPdf] = useState<PDFDocumentProxy | null>(null);
//   const iframeRef = useRef<HTMLIFrameElement>(null);

//   useEffect(() => {
//     const loadPdf = async () => {
//       const loadingTask = pdfjs.getDocument(fileUrl);
//       const pdfDoc = await loadingTask.promise;
//       setPdf(pdfDoc);
//     };

//     loadPdf();
//   }, [fileUrl]);

//   useEffect(() => {
//     if (pdf && pageNumber) {
//       const renderPage = async (pageNum: number) => {
//         const page: PDFPageProxy = await pdf.getPage(pageNum);
//         const viewport = page.getViewport({ scale: 1.5 });
//         const canvas = document.createElement('canvas');
//         const context = canvas.getContext('2d');
//         if (!context) return;
//         canvas.height = viewport.height;
//         canvas.width = viewport.width;

//         const renderContext = {
//           canvasContext: context,
//           viewport: viewport,
//         };

//         await page.render(renderContext).promise;
//         const iframeDoc = iframeRef.current?.contentDocument || iframeRef.current?.contentWindow?.document;
//         if (iframeDoc) {
//           iframeDoc.body.innerHTML = '';
//           iframeDoc.body.appendChild(canvas);
//         }
//       };

//       renderPage(pageNumber);
//     }
//   }, [pdf, pageNumber]);

//   return (
//     <iframe ref={iframeRef} style={{ width: '100%', height: '100vh', border: 'none' }} />
//   );
// };

// export default pdfviewer;
