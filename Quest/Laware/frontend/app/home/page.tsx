"use client";

import React from "react";
import axios from 'axios';

// const handleOpen = () =>{

//   axios.post('http://127.0.0.1:8000/answer', {
//     query: 'what is the criteria to be nepali ?',
//   })
//   .then(function (response:any) {
//     console.log(response);
//   })
//   .catch(function (error:any) {
//     console.log(error);
//   });

// } 

const Home = () => {
  return (
      <div className="">
    <div className="my-100 text-xl">
      Welcome to our platform, your go-to resource for querying and
      understanding the Constitution of Nepal 2015 (Nepali: नेपालको संविधान
      २०७२). Our mission is to make the complexities of the law accessible to
      everyone, not just law students and professionals. Whether you are a
      student, a researcher, or a curious citizen, our platform provides an easy
      and efficient way to get answers to your legal questions. With our
      user-friendly interface, you can explore various sections and subsections
      of the Constitution without the hassle of memorizing them, ensuring you
      get accurate and timely information.
      <br />
      <br />
       Our platform is designed to bridge
      the gap between legal jargon and everyday understanding. We believe that
      legal knowledge should not be confined to those with formal education in
      law. By facilitating simple and direct queries related to the
      Constitution, we empower you to gain insights and make informed decisions.
      Dive into the details of Nepal&apos;s Constitution effortlessly and find the
      information you need, quickly and reliably. Join us in making legal
      knowledge more accessible and understandable for everyone.
    </div>
      </div>
  );
};

export default Home;
