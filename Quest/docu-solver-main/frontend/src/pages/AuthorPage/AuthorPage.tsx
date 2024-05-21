import { Link } from "react-router-dom";

import { FaFacebook, FaInstagram, FaLinkedin, FaGithub } from "react-icons/fa";
import { FaXTwitter } from "react-icons/fa6";

import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";

import LG from "@/assets/images/avatar/LG.png";
import Header from "@/components/Header";
import Footer from "@/components/Footer";
import Layout from "@/layout/Layout";
const teams = [
  {
    shortName: "ST",
    fullName: "Susheel Thapa",
    profileImage: LG,
    position: "Full Stack Developer",
    socialMedia: {
      facebook: "https://www.facebook.com/susheelthapaa/",
      instagram: "https://www.instagram.com/_susheelthapa/",
      github: "https://github.com/SusheelThapa",
      linkedin: "https://www.linkedin.com/in/susheelthapa/",
      twitter: "https://twitter.com/_susheel_thapa",
    },
  },
];

const OurTeam = () => {
  return (
    <>
      <Layout className="px-64">
        <Header />
        <div className="flex justify-center items-center">
          <div className="my-12 mb-20 bg-stone-50 py-20 rounded-3xl w-2/3">
            <div className="flex justify-center items-center">
              {teams.map(
                ({
                  shortName,
                  fullName,
                  profileImage,
                  position,
                  socialMedia,
                }) => {
                  return (
                    <div
                      key={shortName}
                      className="flex flex-col justify-center items-center  gap-6"
                    >
                      <Avatar className="w-44 h-44">
                        <AvatarImage src={profileImage} />
                        <AvatarFallback className="bg-gray-200">
                          {shortName}
                        </AvatarFallback>
                      </Avatar>
                      <div className="text-2xl text-green-900 font-extrabold text-center">
                        <p>{fullName}</p>
                        <p className="mt-2 text-lg text-orange-400 font-bold">
                          {position}
                        </p>
                      </div>
                      <div className="flex justify-center items-center gap-3 text-lg text-gray-400">
                        <Link to={socialMedia.facebook}>
                          <FaFacebook className="hover:text-black" />
                        </Link>
                        <Link to={socialMedia.instagram}>
                          <FaInstagram className="hover:text-black" />
                        </Link>
                        <Link to={socialMedia.github}>
                          <FaGithub className="hover:text-black" />
                        </Link>
                        <Link to={socialMedia.twitter}>
                          <FaXTwitter className="hover:text-black" />
                        </Link>
                        <Link to={socialMedia.linkedin}>
                          <FaLinkedin className="hover:text-black" />
                        </Link>
                      </div>
                    </div>
                  );
                }
              )}
            </div>
          </div>
        </div>
      </Layout>
      <Footer />
    </>
  );
};

export default OurTeam;
