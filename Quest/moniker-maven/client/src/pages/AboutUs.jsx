import React from 'react';
import missionImage from '../assets/mission.png'; 
import visionImage from '../assets/vision.png'; 
import valuesImage from '../assets/values.jpg'; 

const AboutUs = () => {
  return (
    <div className="bg-white dark:bg-darkTheme dark:text-white py-16">
      <div className="container mx-auto px-4">
        <h2 className="text-3xl md:text-5xl font-bold text-center mb-8">About Moniker Maven</h2>
        <p className="text-lg md:text-md text-center max-w-3xl mx-auto mb-12">
          At Moniker Maven, we believe that a name is more than just a word – it's an identity, a connection, and a story. Whether you're naming a new baby or a beloved pet, our goal is to help you find the perfect name that resonates with meaning and joy.
        </p>
        <div className="flex flex-wrap justify-center items-start">
          <div className="w-full md:w-1/3 px-4 mb-8 flex flex-col items-center">
            <img src={missionImage} alt="Our Mission" className="rounded-lg shadow-md w-full h-48 object-contain"/>
            <h3 className="text-xl font-bold mt-4 mb-2 text-center">Our Mission</h3>
            <p className="text-center flex-grow">
              Our mission is to provide an intuitive and enjoyable naming experience, offering a diverse range of names and meanings to inspire and assist you in your naming journey.
            </p>
          </div>
          <div className="w-full md:w-1/3 px-4 mb-8 flex flex-col items-center">
            <img src={visionImage} alt="Our Vision" className="rounded-lg shadow-md w-full h-48 object-contain"/>
            <h3 className="text-xl font-bold mt-4 mb-2 text-center">Our Vision</h3>
            <p className="text-center flex-grow">
              We envision a world where every name is chosen with care, thought, and love, reflecting the unique identity and personality of each individual or pet.
            </p>
          </div>
          <div className="w-full md:w-1/3 px-4 mb-8 flex flex-col items-center">
            <img src={valuesImage} alt="Our Values" className="rounded-lg shadow-md w-full h-48 object-contain"/>
            <h3 className="text-xl font-bold mt-4 mb-2 text-center">Our Values</h3>
            <p className="text-center flex-grow">
              We value diversity, creativity, and user satisfaction, striving to offer a platform that is inclusive, innovative, and delightful to use.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AboutUs;
