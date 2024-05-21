import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { FaGithub } from "react-icons/fa";

const Navbar = () => {
    const [isOpen, setIsOpen] = useState(false);

    const toggleMenu = () => {
        setIsOpen(!isOpen);
    };

    return (
        <div>
            <nav className="bg-white fixed w-full z-20 top-0 start-0 border-b border-gray-200">
                <div className="max-w-screen-xl flex flex-wrap items-center justify-between mx-auto p-4">
                    <Link to='/' className="flex items-center space-x-3 rtl:space-x-reverse">
                        <span className="self-center text-2xl font-semibold whitespace-nowrap">PDF<span className=" text-yellow-500">Assistant</span></span>
                    </Link>
                    <div className="flex md:order-2 space-x-3 md:space-x-0 rtl:space-x-reverse">
                        <a href="https://github.com/Subash-Lamichhane/PDFAssistant" className="hidden md:flex">
                            <button type="button" className="bg-gray-300 hover:bg-gray-400 text-black md:px-5 md:py-2 rounded-md flex items-center space-x-2 mx-3 font-[600]">
                                <FaGithub />
                                <span>GitHub</span>
                            </button>
                        </a>
                        <a href="https://quine.sh/repo/Subash-Lamichhane-PDFAssistant-802497373" className="hidden md:flex">
                            <button type="button" className="bg-[#4fe331] hover:bg-green-600 text-black md:px-5 md:py-2 rounded-md flex items-center space-x-2 px-2 font-[600]">
                                <span>Quine</span>
                            </button>
                        </a>
                        <button
                            onClick={toggleMenu}
                            type="button"
                            className="inline-flex items-center p-2 w-10 h-10 justify-center text-sm text-gray-500 rounded-lg md:hidden hover:bg-gray-100 focus:outline-none focus:ring-2 focus:ring-gray-200"
                            aria-controls="navbar-sticky"
                            aria-expanded={isOpen ? "true" : "false"}
                        >
                            <span className="sr-only">Open main menu</span>
                            <svg className="w-5 h-5" aria-hidden="true" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 17 14">
                                <path stroke="currentColor" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M1 1h15M1 7h15M1 13h15" />
                            </svg>
                        </button>
                    </div>
                    <div className={`items-center justify-between w-full md:flex md:w-auto md:order-1 ${isOpen ? 'block' : 'hidden'}`} id="navbar-sticky">
                        <ul className="flex flex-col p-4 md:p-0 mt-4 font-medium border border-gray-100 rounded-lg bg-gray-50 md:space-x-8 rtl:space-x-reverse md:flex-row md:mt-0 md:border-0 md:bg-white">
                            <li>
                                <Link to='/home' className="block py-2 px-3 text-lg md:text-xl bg-blue-700 rounded md:bg-transparent md:p-0 md:hover:text-blue-700" aria-current="page">Home</Link>
                            </li>
                            <li>
                                <Link to='/about' className="block py-2 px-3 text-lg md:text-xl text-gray-900 rounded hover:bg-gray-100 md:hover:bg-transparent md:hover:text-blue-700 md:p-0">About</Link>
                            </li>
                        </ul>
                    </div>
                </div>
            </nav>
        </div>
    );
}

export default Navbar;
