import React, { useState } from 'react';

const FeaturesSection = () => {
    const [selected, setSelected] = useState(1);
    return (
        <div>
            <h1 className='text-center text-4xl font-bold tracking-wider'>DISCOVER WITH <span className='text-[#4fe331]'>ArticleInsight</span></h1>
            <div className='grid '>
                <div className="flex flex-col md:flex-row gap-10 mx-10 md:mx-24 mt-14 hover:cursor-pointer ">
                    <div className={selected == 1 ? " border-b-[6px] rounded-2xl border-blue-400 flex justify-center flex-col items-center mx-4 " : "flex justify-center flex-col items-center mx-4 border-b rounded-2xl hover:bg-gray-900 hover:shadow-md hover:shadow-blue-600"} onClick={() => { setSelected(1) }}>
                        <h1 className='text-xl text-blue-400'>Comprehensive Article Summaries</h1>
                        <p className='text-lg text-[#aaabc4] my-5 text-center'>Generate detailed summaries of your articles, capturing the essential points effectively.</p>
                    </div>

                    <div className={selected == 2 ? " border-b-[6px] rounded-2xl border-blue-400 flex justify-center flex-col items-center mx-4" : "flex justify-center flex-col items-center mx-4 border-b rounded-2xl hover:bg-gray-900 hover:shadow-md hover:shadow-blue-600"} onClick={() => { setSelected(2) }}>
                        <h1 className='text-xl text-blue-400'>AI-Generated Tags and Categories</h1>
                        <p className='text-lg text-[#aaabc4] my-5 text-center'>Discover relevant tags and categories for your articles to enhance searchability and organization.</p>
                    </div>

                    <div className={selected == 3 ? " border-b-[6px] rounded-2xl border-blue-400 flex justify-center flex-col items-center mx-4" : "flex justify-center flex-col items-center mx-4 border-b rounded-2xl hover:bg-gray-900 hover:shadow-md hover:shadow-blue-600"} onClick={() => { setSelected(3) }}>
                        <h1 className='text-xl text-blue-400'>Sentiment and Insights Analysis</h1>
                        <p className='text-lg text-[#aaabc4] my-5 text-center'>Analyze the sentiment of comments and uncover insights from article responses.</p>
                    </div>

                    <div className={selected == 4 ? " border-b-[6px] rounded-2xl border-blue-400 flex justify-center flex-col items-center mx-4" : "flex justify-center flex-col items-center mx-4 border-b rounded-2xl hover:bg-gray-900 hover:shadow-md hover:shadow-blue-600"} onClick={() => { setSelected(4) }}>
                        <h1 className='text-xl text-blue-400'>Ask Questions about Articles</h1>
                        <p className='text-lg text-[#aaabc4] my-5 text-center'>Get answers to specific questions about the content of your articles.</p>
                    </div>
                </div>

                <div className='mx-auto py-10 max-w-7xl mt-4'>
                    {selected == 1 && <Feature1 />}
                    {selected == 2 && <Feature2 />}
                    {selected == 3 && <Feature3 />}
                    {selected == 4 && <Feature4 />}
                </div>
            </div>
        </div>
    );
}

const Feature1 = () => {
    return (
        <>
            <div className="bg-black p-8 rounded-lg shadow-blue-400 shadow-lg">
                <ul className="pl-5 space-y-3 text-white text-lg leading-relaxed my-4 font-sans">
                    <li className="border-b border-blue-500 pb-2">
                        With <span className="text-blue-400">ArticleInsight</span>, you can transform lengthy articles into concise, comprehensive summaries.
                    </li>
                    <li className="border-b border-blue-500 pb-2">
                        Our platform uses advanced models from <span className="text-blue-400">LLMWare.ai</span> to analyze and distill the core points of your articles.
                    </li>
                    <li className="border-b border-blue-500 pb-2">
                        Save time and effort by quickly understanding the essential information from any article.
                    </li>
                    <li className="border-b border-blue-500 pb-2">
                        <span className="text-blue-400">ArticleInsight</span> ensures you have access to accurate and relevant summaries, making your research and reading more efficient.
                    </li>
                </ul>
            </div>
        </>
    );
}

const Feature2 = () => {
    return (
        <>
            <div className="bg-black p-8 rounded-lg shadow-blue-400 shadow-lg">
                <ul className="pl-5 space-y-3 text-white text-lg leading-relaxed my-4 font-sans">
                    <li className="border-b border-blue-500 pb-2">
                        Enhance your articles with AI-generated tags and categories using <span className="text-blue-400">ArticleInsight</span>.
                    </li>
                    <li className="border-b border-blue-500 pb-2">
                        Our platform leverages <span className="text-blue-400">LLMWare.ai</span> models to automatically generate relevant tags and identify key categories.
                    </li>
                    <li className="border-b border-blue-500 pb-2">
                        Improve the searchability and organization of your content effortlessly.
                    </li>
                    <li className="border-b border-blue-500 pb-2">
                        <span className="text-blue-400">ArticleInsight</span> makes it easy to categorize and highlight important themes in your writing.
                    </li>
                </ul>
            </div>
        </>
    );
}

const Feature3 = () => {
    return (
        <>
            <div className="bg-black p-8 rounded-lg shadow-blue-400 shadow-lg">
                <ul className="pl-5 space-y-3 text-white text-lg leading-relaxed my-4 font-sans">
                    <li className="border-b border-blue-500 pb-2">
                        Understanding the sentiment and insights behind your articles is crucial for deeper analysis.
                    </li>
                    <li className="border-b border-blue-500 pb-2">
                        <span className="text-blue-400">ArticleInsight</span> uses <span className="text-blue-400">LLMWare.ai</span> models to analyze the sentiment of comments and uncover underlying themes.
                    </li>
                    <li className="border-b border-blue-500 pb-2">
                        Whether you need to gauge the overall tone or extract meaningful insights from responses, <span className="text-blue-400">ArticleInsight</span> has you covered.
                    </li>
                    <li className="border-b border-blue-500 pb-2">
                        Gain a comprehensive understanding of your content's impact and the key messages from readers.
                    </li>
                </ul>
            </div>
        </>
    );
}

const Feature4 = () => {
    return (
        <>
            <div className="bg-black p-8 rounded-lg shadow-blue-400 shadow-lg">
                <ul className="pl-5 space-y-3 text-white text-lg leading-relaxed my-4 font-sans">
                    <li className="border-b border-blue-500 pb-2">
                        With <span className="text-blue-400">ArticleInsight</span>, you can interact with your articles on a deeper level by asking specific questions about the content.
                    </li>
                    <li className="border-b border-blue-500 pb-2">
                        Our platform leverages advanced AI from <span className="text-blue-400">LLMWare.ai</span> to provide precise and informative answers to your queries.
                    </li>
                    <li className="border-b border-blue-500 pb-2">
                        Enhance your understanding and engagement by exploring detailed answers and explanations related to your articles.
                    </li>
                    <li className="border-b border-blue-500 pb-2">
                        <span className="text-blue-400">ArticleInsight</span> empowers you to delve into your content with greater depth and clarity.
                    </li>
                </ul>
            </div>
        </>
    );
}

export default FeaturesSection;
