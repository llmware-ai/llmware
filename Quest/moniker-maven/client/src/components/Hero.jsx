import React from 'react';
import heroImage from '../assets/hero-image.jpg'; 
import { Link } from 'react-router-dom';
const Hero = () => {
  return (
    <div
      className="bg-cover bg-center relative"
      style={{ backgroundImage: `url(${heroImage})`, height: 'calc(100vh - 64px)' }} 
    >
      <div className="absolute inset-0 bg-black opacity-50"></div>
      <div className="container mx-auto flex flex-col justify-center items-center text-white relative z-10 h-full">
        <div className="text-center">
          <h1 className="text-4xl md:text-6xl font-bold mb-4">Moniker Maven</h1>
          <p className="text-lg md:text-xl max-w-md">Discover the perfect names for your bundle of joy or furry friend with ease and delight.</p>
          <Link to='/home'>
          <button className="button">Get Started  </button>
          </Link>
        </div>
      </div>
    </div>
  );
};

export default Hero;
