import "./Hero.scss";
//images
import TAB01 from "../../assets/images/tab02.png";
import TAB02 from "../../assets/images/tab01.png";
import TAB03 from "../../assets/images/tab03.png";
import TAB04 from "../../assets/images/tab04.png";
//gsap
import gsap from "gsap";
import { useGSAP } from "@gsap/react";
import { useStore } from "../../context/StoreContext";
import { useNavigate } from "react-router-dom";
import { useState, useEffect } from "react";
import { createAcc } from "../../utils/utils";

const Hero = () => {
  const { wallet, setWallet } = useStore();
  const navigate = useNavigate();

  const [walletAddress, setWalletAddress] = useState(null);
  const [provider, setProvider] = useState(null);

  useEffect(() => {
    if (window.ethereum) {
      setProvider(window.ethereum);
    }
  }, []);

  const requestAccount = async () => {
    if (provider) {
      try {
        const accounts = await provider.request({
          method: "eth_requestAccounts",
        });
        setWalletAddress(accounts[0]);
        setWallet(accounts[0]);
        console.log(accounts[0]);
        localStorage.setItem("wallet", accounts[0]);
      } catch (err) {
        console.error("Error:", err);
      }
    } else {
      console.log("MetaMask not detected");
    }
  };
  //gsap
  useGSAP(() => {
    const tl = gsap.timeline();
    tl.fromTo(
      ".main-txt h1 span",
      {
        scale: 0,
      },
      {
        scale: 1,
        ease: "back.inOut",
        duration: 0.5,
      }
    );
    tl.fromTo(
      ".tab",
      {
        scale: 0,
        rotate: 20,
      },
      {
        scale: 1,
        rotate: 0,
        stagger: 0.1,
        ease: "back.inOut",
      }
    );
  });

  const createProfile = async() => {
    if (wallet) {
      const result = await createAcc(wallet);
      if (result) {
        navigate("/fam");
      }
    } else {
      requestAccount();
    }
  };
  return (
    <div className="hero">
      <div className="main-txt">
        <div className="head-container">
          <h1 className="main-head">Make your</h1>
        </div>
        <div className="head-container">
          <div className="tab01 tab">
            <img src={TAB01} alt="tab" />
          </div>
          <h1 className="main-head">
            <span>Family's</span> Health
          </h1>
          <div className="tab02 tab">
            <img src={TAB02} alt="tab" />
          </div>
        </div>
        <div className="head-container">
          <div className="tab03 tab">
            <img src={TAB03} alt="tab" />
          </div>
          <h1 className="main-head">Perfect</h1>
          <div className="tab04 tab">
            <img src={TAB04} alt="tab" />
          </div>
        </div>
      </div>
      <button onClick={() => createProfile()} className="create-btn">
        Create Profile
      </button>
    </div>
  );
};
export default Hero;
