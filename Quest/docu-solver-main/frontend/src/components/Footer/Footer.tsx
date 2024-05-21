import { Link } from "react-router-dom";

import { FaFacebook, FaInstagram, FaLinkedin, FaTiktok } from "react-icons/fa";
import { FaXTwitter } from "react-icons/fa6";

const Footer = () => {
  return (
    <div className="flex flex-col gap-10 justify-between items-center bg-black text-gray-300 py-6 pt-10 text-sm">
      <div className=" mx-auto flex  justify-evenly items-center w-full ">
        <div className="flex flex-col gap-1 justify-center items-start">
          <Link to="/">
            <div className="text-3xl font-bold">DocuSolver</div>
          </Link>
          <div className="text-base text-gray-400">
            Automated Exam Revision Platform
          </div>
          <div className="mt-3 flex text-xl gap-2 text-gray-500 ">
            <FaFacebook className="hover:text-white" />
            <FaInstagram className="hover:text-white" />
            <FaTiktok className="hover:text-white" />
            <FaXTwitter className="hover:text-white" />
            <FaLinkedin className="hover:text-white" />
          </div>
        </div>
        <div className="flex justify-end items-start gap-x-32 w-2/5">
          <div className="flex flex-col gap-3">
            <div className="hover:text-white">About Us</div>
            <div className="hover:text-white">Features</div>
            <div className="hover:text-white">Feedback</div>
            <div className="hover:text-white">Contact Us</div>
          </div>
          <div className="flex flex-col gap-3">
            <Link to="/author"> Author</Link>
            <div className="hover:text-white">Partner</div>
            <div className="hover:text-white">FAQ</div>
          </div>
        </div>
      </div>
      <div className="text-gray-400 text-base">
        &#169; DocuSolver 2024. All rights reserved.
      </div>
    </div>
  );
};

export default Footer;
