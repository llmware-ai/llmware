"use client";

import { Typography } from "@material-tailwind/react";
import Image from "next/image";
import React from "react";

interface FooterProps {
  // Define any props here if needed
}

const Footer: React.FC<FooterProps> = () => {
  return (
    <footer className="w-full bg-white p-8">
      <div className="flex flex-row flex-wrap items-center justify-center gap-y-6 gap-x-12 bg-white text-center md:justify-between">
        <Image src="/logo.png" alt="logo-ct" width="100" height="100" />
        <ul className="flex flex-wrap items-center gap-y-2 gap-x-8">
          <li>
            <Typography
              as="a"
              href="/home"
              color="blue-gray"
              className="font-normal transition-colors hover:text-blue-500 focus:text-blue-500"
            >
              Home
            </Typography>
          </li>
          <li>
            <Typography
              as="a"
              href="/constitution"
              color="blue-gray"
              className="font-normal transition-colors hover:text-blue-500 focus:text-blue-500"
            >
              Query
            </Typography>
          </li>
          <li>
            <Typography
              as="a"
              href="/display"
              color="blue-gray"
              className="font-normal transition-colors hover:text-blue-500 focus:text-blue-500"
            >
              Constitution 2015
            </Typography>
          </li>
        </ul>
      </div>
      <hr className="my-8 border-blue-gray-50" />
      <Typography color="blue-gray" className="text-center font-normal">
        &copy; 2024 Nepal Constitution. All Rights Reserved.
      </Typography>
    </footer>
  );
};

export default Footer;
