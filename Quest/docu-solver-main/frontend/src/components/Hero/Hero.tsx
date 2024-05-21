import { Link } from "react-router-dom";
import hero from "../../assets/images/hero.png";

const Hero = () => {
  return (
    <div className="flex justify-between items-center gap-16 my-20">
      <div className="text-gray-600 text-base ">
        <div className="text-5xl text-black font-medium">
          Unlock your{" "}
          <span className="block text-green-600 font-semibold tracking-wider">
            {" "}
            Academic Potential
          </span>
        </div>
        <div>
          Effortlessly extract answers from your study materials and ace your
          exams
        </div>

        <button className="my-10 px-6 py-3 bg-green-400 text-black font-semibold tracking-widest rounded-xl text-base cursor-pointer hover:bg-green-500 hover:text-black">
          <Link to="/upload-files">Get Started</Link>
        </button>
      </div>
      <div className="w-3/5">
        <img src={hero} alt="A boy is thinking" />
      </div>
    </div>
  );
};

export default Hero;
