import React from 'react'
import Navbar from '../components/Navbar'
import Footer from '../components/Footer'
import { Link } from 'react-router-dom'

const About = () => {
    return (
        <>
            <div className="flex flex-col min-h-screen">
                <Navbar />
                <main className="flex flex-col">
                    <section className="w-full py-12 md:py-24 lg:py-32 bg-gray-100 md:px-32">
                        <div className="container px-4 md:px-6">
                            <div className="grid gap-6 lg:grid-cols-[1fr_400px] lg:gap-12 xl:grid-cols-[1fr_550px]">
                                <div className="flex flex-col justify-center space-y-4">
                                    <div className="space-y-2">
                                        <h1 className="text-3xl font-bold tracking-tighter sm:text-5xl xl:text-6xl/none my-4">About This Project</h1>
                                        <p className="max-w-[600px] text-gray-500 md:text-xl">
                                            PDFAssistant leverages llmware to generate insightful summaries and keywords from your PDF articles, empowering you to quickly grasp key information.
                                        </p>
                                    </div>
                                    <div className="flex flex-col gap-2 min-[400px]:flex-row">
                                        <Link
                                            className="inline-flex h-10 items-center justify-center rounded-md bg-gray-900 px-8 text-sm font-medium text-gray-50 shadow transition-colors hover:bg-gray-900/90 focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-gray-950 disabled:pointer-events-none disabled:opacity-50"
                                            to='/'
                                        >
                                            Get Started
                                        </Link>
                                    </div>
                                </div>
                                <div className="container mx-auto px-4 py-12 md:px-6 lg:py-16">
                                    <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                                        <div className="flex flex-col items-start gap-2">
                                            <UsersIcon className="h-8 w-8 text-indigo-600" />
                                            <h3 className="text-lg font-semibold">Accessible to All</h3>
                                            <p className="text-gray-600 dark:text-gray-400">
                                                This tool is designed to be user-friendly and accessible, making it easy for anyone to harness the power of AI-driven PDF insights.
                                            </p>
                                        </div>
                                        <div className="flex flex-col items-start gap-2">
                                            <ClipboardIcon className="h-8 w-8 text-indigo-600" />
                                            <h3 className="text-lg font-semibold">Streamlined Insights</h3>
                                            <p className="text-gray-600 dark:text-gray-400">
                                                THis AI-powered tool extracts key information, summaries, and insights from your PDF documents, saving you time and effort.
                                            </p>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </section>
                    <section className="w-full py-12 md:py-24 lg:py-32 bg-white md:px-32">
                        <div className="container px-4 md:px-6">
                            <div className="grid gap-6 lg:grid-cols-2 lg:gap-12">
                                <div className="space-y-2">
                                    <div className="inline-block rounded-lg bg-gray-100 px-3 py-1 text-sm">Project's Mission</div>
                                    <h2 className="text-3xl font-bold tracking-tighter sm:text-5xl">
                                        Empowering You with Intelligent PDF Insights
                                    </h2>
                                    <p className="max-w-[600px] text-gray-500 md:text-xl/relaxed lg:text-base/relaxed xl:text-xl/relaxed">
                                        This project mission is to provide you with a powerful tool that simplifies the process of extracting valuable information from your PDF documents. We believe that by leveraging the latest advancements in AI technology, we can help you save time, improve productivity, and make more informed decisions.
                                    </p>
                                </div>
                                <div className="grid gap-6">
                                    <div className="grid gap-1">
                                        <h3 className="text-xl font-bold">Streamlined Workflow</h3>
                                        <p className="">
                                            This tool is designed to seamlessly integrate into your existing PDF-based workflows, allowing you to quickly and efficiently extract the insights you need.
                                        </p>
                                    </div>
                                    <div className="grid gap-1">
                                        <h3 className="text-xl font-bold">Cutting-Edge AI</h3>
                                        <p className="">
                                            We leverage the latest advancements in natural language processing and machine learning to provide you with accurate and reliable PDF insights.
                                        </p>
                                    </div>
                                    <div className="grid gap-1">
                                        <h3 className="text-xl font-bold">Accessible to All</h3>
                                        <p className="">
                                            This tool is designed to be user-friendly and accessible, making it easy for anyone to harness the power of AI-driven PDF insights.
                                        </p>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </section>
                    <section className="w-full py-12 md:py-24 lg:py-32 border-t md:px-32">
                        <div className="container grid items-center justify-center gap-4 px-4 text-center md:px-6">
                            <div className="space-y-3">
                                <h2 className="text-3xl font-bold tracking-tighter md:text-4xl/tight">Unlock the Power of PDFAssistant</h2>
                                <p className="mx-auto max-w-[600px] text-gray-500 md:text-xl/relaxed lg:text-base/relaxed xl:text-xl/relaxed">
                                    Start using our AI-powered tool to quickly extract key information, summaries, and insights from your PDF documents.
                                </p>
                            </div>
                            <div className="mx-auto w-full max-w-sm space-y-2">
                                <Link
                                    className="inline-flex h-10 items-center justify-center rounded-md bg-gray-900 px-8 text-sm font-medium text-gray-50 shadow transition-colors hover:bg-gray-900/90 focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-gray-950 disabled:pointer-events-none disabled:opacity-50"
                                    to='/home'>
                                    Get Started
                                </Link>
                            </div>
                        </div>
                    </section>
                </main>
                <Footer />
            </div>
        </>
    )
}

export default About

function ClipboardIcon(props) {
    return (
        <svg
            {...props}
            xmlns="http://www.w3.org/2000/svg"
            width="24"
            height="24"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
        >
            <rect width="8" height="4" x="8" y="2" rx="1" ry="1" />
            <path d="M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2" />
        </svg>
    )
}


function LightbulbIcon(props) {
    return (
        <svg
            {...props}
            xmlns="http://www.w3.org/2000/svg"
            width="24"
            height="24"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
        >
            <path d="M15 14c.2-1 .7-1.7 1.5-2.5 1-.9 1.5-2.2 1.5-3.5A6 6 0 0 0 6 8c0 1 .2 2.2 1.5 3.5.7.7 1.3 1.5 1.5 2.5" />
            <path d="M9 18h6" />
            <path d="M10 22h4" />
        </svg>
    )
}


function TimerIcon(props) {
    return (
        <svg
            {...props}
            xmlns="http://www.w3.org/2000/svg"
            width="24"
            height="24"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
        >
            <line x1="10" x2="14" y1="2" y2="2" />
            <line x1="12" x2="15" y1="14" y2="11" />
            <circle cx="12" cy="14" r="8" />
        </svg>
    )
}


function UsersIcon(props) {
    return (
        <svg
            {...props}
            xmlns="http://www.w3.org/2000/svg"
            width="24"
            height="24"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
        >
            <path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2" />
            <circle cx="9" cy="7" r="4" />
            <path d="M22 21v-2a4 4 0 0 0-3-3.87" />
            <path d="M16 3.13a4 4 0 0 1 0 7.75" />
        </svg>
    )
}