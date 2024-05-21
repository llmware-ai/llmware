import React from 'react'
import { Link } from 'react-router-dom'
import Navbar from '../components/Navbar'
import Footer from '../components/Footer'


export default function AboutPage() {
    return (
        <div className="flex flex-col min-h-[100dvh]">
            <div className="bg-black text-white">
                <Navbar />
            </div>
            <main className="flex-1">
                <section className="w-full pt-12 md:pt-24 lg:pt-32 border-y">
                    <div className="px-6 md:px-8 space-y-12 xl:space-y-16">
                        <div className="grid max-w-[1300px] mx-auto gap-6 md:gap-12 md:grid-cols-2">
                            <div>
                                <h1 className="lg:leading-tighter text-4xl md:text-5xl xl:text-6xl">
                                    Article Summary
                                </h1>
                                <p className="mx-auto max-w-[700px] text-lg ">
                                    Quickly summarize articles, extract keywords, analyze sentiment, and get answers to your questions -
                                    all with our powerful AI-driven web app.
                                </p>
                            </div>
                            <div className="flex flex-col items-start space-y-6">
                                <div className="inline-block rounded-lg bg-gray-100 px-4 py-2 text-lg ">
                                    Key Features
                                </div>
                                <ul className="grid gap-3 py-6">
                                    <li className="flex items-center gap-2">
                                        <CheckIcon className="w-6 h-6" />
                                        <span className="text-lg">Automatically extract keywords from article content</span>
                                    </li>
                                    <li className="flex items-center gap-2">
                                        <CheckIcon className="w-6 h-6" />
                                        <span className="text-lg">Perform sentiment analysis on user comments</span>
                                    </li>
                                    <li className="flex items-center gap-2">
                                        <CheckIcon className="w-6 h-6" />
                                        <span className="text-lg">Get answers to your questions about the article from an AI assistant</span>
                                    </li>
                                </ul>
                                <div className="space-x-6">
                                    <Link
                                        className="inline-flex items-center justify-center rounded-md bg-gray-900 px-6 py-3 text-lg text-gray-50 shadow-lg transition-colors hover:bg-gray-800 focus:outline-none focus-visible:ring-2 focus-visible:ring-gray-900 disabled:pointer-events-none disabled:opacity-50 "
                                        to='/home'
                                    >
                                        Get Started
                                    </Link>
                                    <Link
                                        className="inline-flex items-center justify-center rounded-md border border-gray-200 bg-white px-6 py-3 text-lg font-medium shadow-lg transition-colors hover:bg-gray-100 hover:text-gray-900 focus:outline-none focus-visible:ring-2 focus-visible:ring-gray-900 disabled:pointer-events-none disabled:opacity-50"
                                        to='/'
                                    >
                                        Learn More
                                    </Link>
                                </div>
                            </div>
                        </div>
                    </div>
                </section>
                <section className="flex justify-center items-center w-full py-12 md:py-24 lg:py-32 bg-white">
                    <div className="container space-y-12 px-6 md:px-8">
                        <div className="flex flex-col items-center justify-center space-y-6 text-center">
                            <div className="inline-block rounded-lg bg-gray-100 px-4 py-2 text-lg ">
                                Benefits
                            </div>
                            <h2 className="text-4xl md:text-5xl font-bold tracking-tighter">
                                Streamline Your Research
                            </h2>
                            <p className="max-w-[900px] text-lg text-gray-500 md:text-xl lg:text-base xl:text-lg">
                                Our app helps you quickly summarize articles, identify key insights, and get answers to your questions
                                - saving you time and effort in your research.
                            </p>
                        </div>
                        <div className="mx-auto grid items-start justify-center gap-8 sm:max-w-4xl sm:grid-cols-2 md:gap-12 lg:max-w-5xl lg:grid-cols-3">
                            <div className="grid gap-3">
                                <h3 className="text-xl font-bold">Automated Summarization</h3>
                                <p className="text-lg text-gray-500">
                                    Our AI-powered summarization engine quickly distills long articles into concise, easy-to-digest
                                    summaries.
                                </p>
                            </div>
                            <div className="grid gap-3">
                                <h3 className="text-xl font-bold">Keyword Extraction</h3>
                                <p className="text-lg text-gray-500">
                                    Identify the most important concepts and topics in an article with our keyword extraction feature.
                                </p>
                            </div>
                            <div className="grid gap-3">
                                <h3 className="text-xl font-bold">Sentiment Analysis</h3>
                                <p className="text-lg text-gray-500">
                                    Understand the overall sentiment expressed in user comments with our sentiment analysis capabilities.
                                </p>
                            </div>
                            <div className="grid gap-3">
                                <h3 className="text-xl font-bold">AI-Powered Q&A</h3>
                                <p className="text-lg text-gray-500">
                                    Ask questions about the article content and get answers from our intelligent assistant.
                                </p>
                            </div>
                            <div className="grid gap-3">
                                <h3 className="text-xl font-bold">Easy to Use</h3>
                                <p className="text-lg text-gray-500">
                                    Our intuitive interface makes it simple to summarize articles, analyze comments, and get answers to
                                    your questions.
                                </p>
                            </div>
                            <div className="grid gap-3">
                                <h3 className="text-xl font-bold">Powerful Insights</h3>
                                <p className="text-lg text-gray-500">
                                    Uncover valuable insights and trends by leveraging the power of AI-driven article analysis.
                                </p>
                            </div>
                        </div>
                    </div>
                </section>

                <section className="w-full py-12 md:py-24 lg:py-32 bg-gray-100 flex justify-center align-center">
                    <div className="container grid items-center justify-center gap-8 px-6 md:px-8 text-center">
                        <div className="space-y-6">
                            <div className="inline-block rounded-lg bg-gray-100 px-4 py-2 text-lg ">
                                How it Works
                            </div>
                            <h2 className="text-4xl md:text-5xl font-bold tracking-tighter">
                                Streamlined Article Analysis
                            </h2>
                            <p className="mx-auto max-w-[600px] text-lg text-gray-500 md:text-xl lg:text-base xl:text-lg">
                                Our app makes it easy to summarize articles, extract keywords, analyze sentiment, and get answers to
                                your questions.
                            </p>
                        </div>
                        <div className="mx-auto w-full max-w-sm space-y-6">
                            <div className="flex flex-col gap-3">
                                <div className="flex items-center gap-3">
                                    <CheckIcon className="h-6 w-6 text-green-500" />
                                    <span className="text-lg">Enter article URL</span>
                                </div>
                                <div className="flex items-center gap-3">
                                    <CheckIcon className="h-6 w-6 text-green-500" />
                                    <span className="text-lg">Get article summary and keywords</span>
                                </div>
                                <div className="flex items-center gap-3">
                                    <CheckIcon className="h-6 w-6 text-green-500" />
                                    <span className="text-lg">Analyze comments and sentiment</span>
                                </div>
                                <div className="flex items-center gap-3">
                                    <CheckIcon className="h-6 w-6 text-green-500" />
                                    <span className="text-lg">Ask questions, get answers</span>
                                </div>
                            </div>
                        </div>
                    </div>
                </section>
                <Footer />
            </main>
        </div>
    )
}

function BookIcon(props) {
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
            <path d="M4 19.5v-15A2.5 2.5 0 0 1 6.5 2H20v20H6.5a2.5 2.5 0 0 1 0-5H20" />
        </svg>
    )
}


function CheckIcon(props) {
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
            <path d="M20 6 9 17l-5-5" />
        </svg>
    )
}