import "./ProfilePage.scss";

import BOY from "../../assets/images/male.svg";
import GIRL from "../../assets/images/female.svg";
import QR from "../../assets/images/qr.png";

import { useParams } from "react-router-dom";
import React, { useState, useRef, useEffect } from "react";
import { motion } from "motion/react";
import ChatComponent from "../../components/ChatUI/Chatui";
import toast from "react-hot-toast";
import { baseUrl } from "../../constants";
import { fetchDocuments, fetchScore, getProfileData } from "../../utils/utils";
import { useStore } from "../../context/StoreContext";
import Loader from "../../components/Loader/Loader";

import { CircularProgressbar, buildStyles } from "react-circular-progressbar";
import "react-circular-progressbar/dist/styles.css";

const ProfilePage = () => {
  const { wallet, setWallet } = useStore();
  const { uid } = useParams();
  const [profile, setProfile] = useState(null);
  const [selectedImage, setSelectedImage] = useState(null);
  const [previewImage, setPreviewImage] = useState(null);
  const fileInputRef = useRef(null);

  const [chatPopup, setChatPopup] = useState(false);
  const [loader, setLoader] = useState(false);
  const [history, setHistory] = useState(null);
  const [popup, setPopup] = useState(false);
  const [sharepopup, setsharepopup] = useState(false);
  const [healthScore, setHealthScore] = useState("");
  const [healthLoader, setHealthLoader] = useState(false);
  const [trigger,setTrigger]=useState(false);

  //get profile
  useEffect(() => {
    const fetchProfile = async () => {
      try {
        const result = await getProfileData(wallet, uid);
        setProfile(result);
        console.log(result);
      } catch (error) {
        console.error("Error fetching profiles:", error);
      }
    };

    fetchProfile();
  }, [history]);

  //get doc
  useEffect(() => {
    const fetchProfile = async () => {
      try {
        const result = await fetchDocuments(wallet, uid);
        setHistory(result);
        console.log(result);
      } catch (error) {
        console.error("Error fetching profiles:", error);
      }
    };

    fetchProfile();
  }, [trigger]);

  const handleImageUpload = (event) => {
    const file = event.target.files[0];
    if (file) {
      setSelectedImage(file);
      setPreviewImage(URL.createObjectURL(file));
    }
  };

  const uploadImage = async () => {
    setLoader(true);
    if (!selectedImage) return;

    const formData = new FormData();
    formData.append("file", selectedImage);

    try {
      // Construct the URL with the query parameter
      const url = new URL(`${baseUrl}/document/upload`);
      url.searchParams.append("prfid", uid); // Add prfid as a query parameter

      const response = await fetch(url, {
        method: "POST",
        headers: {
          // "Content-Type": "multipart/formdatas",
          Authorization: "Bearer your-auth-token",
          "ngrok-skip-browser-warning": "69420",
          Address: wallet,
        },
        body: formData, // Send the form data in the request body
      });

      if (!response.ok) {
        throw new Error("Upload failed");
      }

      const result = await response.json();
      toast.success("Successfully Uploaded!");
      console.log("Upload successful:", result);

      // Reset after successful upload
      setSelectedImage(null);
      setPreviewImage(null);
      if (fileInputRef.current) fileInputRef.current.value = "";
      setLoader(false);
      setTrigger(!trigger)
    } catch (error) {
      setLoader(false);
      console.error("Upload error:", error);
      toast.error("I can't upload it 🙂");
    }
  };

  const triggerFileInput = () => {
    fileInputRef.current.click();
  };

  const fetchHealthScore = async () => {
    setHealthLoader(true);
    const result = await fetchScore(wallet, uid);
    if (result) {
      setHealthScore(result?.overallhealthscore);
      setHealthLoader(false);
    } else {
      toast.error("Can't fetch health score 🙁");
      setHealthLoader(false);
    }
  };

  return (
    <div className="profile-page">
      <div className="profile-sec">
        {profile?.gender == "Male" ? (
          <img src={BOY} className="avatar"></img>
        ) : (
          <img src={GIRL} className="avatar"></img>
        )}
        <div className="name">{profile?.name}</div>
        <div className="grp">
          <div className="dob">
            <svg
              xmlns="http://www.w3.org/2000/svg"
              width={20}
              height={21}
              fill="none"
            >
              <path
                fill="#303030"
                d="M6.667 5.292a.63.63 0 0 1-.625-.625v-2.5a.63.63 0 0 1 .625-.625.63.63 0 0 1 .625.625v2.5a.63.63 0 0 1-.625.625M13.333 5.292a.63.63 0 0 1-.625-.625v-2.5a.63.63 0 0 1 .625-.625.63.63 0 0 1 .625.625v2.5a.63.63 0 0 1-.625.625M7.083 12.583a.8.8 0 0 1-.316-.066.9.9 0 0 1-.275-.175.86.86 0 0 1-.242-.592.8.8 0 0 1 .067-.317q.062-.15.175-.275a.9.9 0 0 1 .275-.175.85.85 0 0 1 .908.175c.15.159.242.375.242.592 0 .05-.009.108-.017.167a.5.5 0 0 1-.05.15.6.6 0 0 1-.075.15c-.025.041-.067.083-.1.125a.88.88 0 0 1-.592.241M10 12.583a.8.8 0 0 1-.317-.066.9.9 0 0 1-.275-.175.86.86 0 0 1-.241-.592.8.8 0 0 1 .066-.317q.063-.15.175-.275a.9.9 0 0 1 .275-.175.84.84 0 0 1 .909.175c.15.159.241.375.241.592q-.002.077-.016.167a.5.5 0 0 1-.05.15.6.6 0 0 1-.075.15c-.025.041-.067.083-.1.125a.88.88 0 0 1-.592.241M12.917 12.583a.8.8 0 0 1-.317-.066.9.9 0 0 1-.275-.175l-.1-.125a.6.6 0 0 1-.075-.15.5.5 0 0 1-.05-.15 1 1 0 0 1-.017-.167c0-.217.092-.433.242-.592a.9.9 0 0 1 .275-.175.83.83 0 0 1 .908.175c.15.159.242.375.242.592q-.002.077-.017.167a.5.5 0 0 1-.05.15.6.6 0 0 1-.075.15c-.025.041-.066.083-.1.125a.88.88 0 0 1-.591.241M7.083 15.5a.8.8 0 0 1-.316-.067 1 1 0 0 1-.275-.175.88.88 0 0 1-.242-.591.8.8 0 0 1 .067-.317q.062-.162.175-.275c.308-.308.875-.308 1.183 0 .15.158.242.375.242.592a.88.88 0 0 1-.242.591.88.88 0 0 1-.592.242M10 15.5a.88.88 0 0 1-.592-.242.88.88 0 0 1-.241-.591.8.8 0 0 1 .066-.317q.063-.162.175-.275c.309-.308.875-.308 1.184 0a.8.8 0 0 1 .175.275c.041.1.066.208.066.317a.88.88 0 0 1-.241.591.88.88 0 0 1-.592.242M12.917 15.5a.88.88 0 0 1-.592-.242.8.8 0 0 1-.175-.275.8.8 0 0 1-.067-.316q.002-.165.067-.317.063-.162.175-.275a.83.83 0 0 1 .908-.175q.075.025.15.075c.042.025.084.067.125.1.15.158.242.375.242.592a.88.88 0 0 1-.242.591.88.88 0 0 1-.591.242M17.083 8.7H2.917a.63.63 0 0 1-.625-.625.63.63 0 0 1 .625-.625h14.166a.63.63 0 0 1 .625.625.63.63 0 0 1-.625.625"
              />
              <path
                fill="#303030"
                d="M13.333 19.458H6.667c-3.042 0-4.792-1.75-4.792-4.791V7.583c0-3.041 1.75-4.791 4.792-4.791h6.666c3.042 0 4.792 1.75 4.792 4.791v7.084c0 3.041-1.75 4.791-4.792 4.791M6.667 4.042c-2.384 0-3.542 1.158-3.542 3.541v7.084c0 2.383 1.158 3.541 3.542 3.541h6.666c2.384 0 3.542-1.158 3.542-3.541V7.583c0-2.383-1.158-3.541-3.542-3.541z"
              />
            </svg>
            {profile?.dob}
          </div>
          <div className="data-tabs">
            <div className="tabb">{profile?.gender}</div>
            <div className="tabb">{profile?.blood}</div>
          </div>
        </div>
        <div className="btns">
          <div
            className="health-btn"
            onClick={() => {
              setPopup(!popup);
              fetchHealthScore();
            }}
          >
            Check Health score
          </div>
          <div className="share-btn" onClick={() => setsharepopup(!sharepopup)}>
            <svg
              xmlns="http://www.w3.org/2000/svg"
              width={24}
              height={24}
              fill="none"
            >
              <path
                fill="#676767"
                d="M12 8.75c-.41 0-.75-.34-.75-.75V3.81l-.72.72c-.29.29-.77.29-1.06 0a.754.754 0 0 1 0-1.06l2-2c.21-.21.54-.28.82-.16.28.11.46.39.46.69v6c0 .41-.34.75-.75.75"
              />
              <path
                fill="#676767"
                d="M14 4.75c-.19 0-.38-.07-.53-.22l-2-2a.754.754 0 0 1 0-1.06c.29-.29.77-.29 1.06 0l2 2c.29.29.29.77 0 1.06-.15.15-.34.22-.53.22M16 22.75H8c-5.75 0-5.75-3.05-5.75-5.75v-1c0-2.23 0-4.75 4.75-4.75 1.19 0 1.63.29 2.25.75.03.03.07.05.1.09l1.02 1.08c.86.91 2.42.91 3.28 0l1.02-1.08c.03-.03.06-.06.1-.09.62-.47 1.06-.75 2.25-.75 4.75 0 4.75 2.52 4.75 4.75v1c-.02 3.82-1.95 5.75-5.77 5.75m-9-10c-3.25 0-3.25 1.02-3.25 3.25v1c0 2.74 0 4.25 4.25 4.25h8c2.98 0 4.25-1.27 4.25-4.25v-1c0-2.23 0-3.25-3.25-3.25-.72 0-.87.09-1.3.41l-.97 1.03A3.73 3.73 0 0 1 12 15.37a3.73 3.73 0 0 1-2.73-1.18l-.97-1.03c-.43-.32-.58-.41-1.3-.41"
              />
              <path
                fill="#676767"
                d="M5 12.75c-.41 0-.75-.34-.75-.75v-2c0-1.94 0-4.35 3.68-4.7.4-.05.78.26.82.68.04.41-.26.78-.68.82-2.32.21-2.32 1.15-2.32 3.2v2c0 .41-.34.75-.75.75M19 12.75c-.41 0-.75-.34-.75-.75v-2c0-2.05 0-2.99-2.32-3.21a.75.75 0 0 1-.67-.82c.04-.41.4-.72.82-.67 3.68.35 3.68 2.76 3.68 4.7v2a.77.77 0 0 1-.76.75"
              />
            </svg>
          </div>
        </div>
        <div className="upload-history">
          {history?.map((item) => (
            <div className="upload-card">
              <img
                src={`${baseUrl}/assets/${item?.filename}`}
                className="upload-img"
              ></img>
              <div className="short-dec">
                {item?.inferences.slice(0, 200) + "..."}
              </div>
            </div>
          ))}
        </div>
      </div>
      <div className="uploader-wrapper">
        <input
          type="file"
          ref={fileInputRef}
          onChange={handleImageUpload}
          accept="image/*"
          style={{ display: "none" }}
        />
        {previewImage && (
          <motion.div
            className="pre-img"
            initial={{ scale: 0.4, rotate: "0deg" }}
            animate={{ scale: 1, rotate: "0deg" }}
            transition={{
              duration: 0.5,
            }}
          >
            {loader ? (
              <Loader />
            ) : (
              <img
                src={previewImage}
                alt="Preview"
                style={{ maxWidth: "200px", maxHeight: "200px" }}
              />
            )}
          </motion.div>
        )}
      </div>
      <div className="bottom-bar">
        <div
          className="add-profile-btn"
          onClick={() => {
            if (selectedImage) {
              uploadImage();
            } else {
              triggerFileInput();
            }
          }}
        >
          <svg
            xmlns="http://www.w3.org/2000/svg"
            width={24}
            height={24}
            fill="none"
          >
            <path
              fill="#fff"
              d="M12 9.75c-.41 0-.75-.34-.75-.75V3.81l-.72.72c-.29.29-.77.29-1.06 0a.754.754 0 0 1 0-1.06l2-2c.21-.21.54-.28.82-.16.28.11.46.39.46.69v7c0 .41-.34.75-.75.75"
            />
            <path
              fill="#fff"
              d="M14 4.75c-.19 0-.38-.07-.53-.22l-2-2a.754.754 0 0 1 0-1.06c.29-.29.77-.29 1.06 0l2 2c.29.29.29.77 0 1.06-.15.15-.34.22-.53.22M13.76 17.75h-3.53a2.73 2.73 0 0 1-2.46-1.52L6.6 13.89a.24.24 0 0 0-.22-.14h-4.4c-.41 0-.75-.34-.75-.75s.34-.75.75-.75h4.41c.67 0 1.27.37 1.57.97l1.17 2.34c.21.43.64.69 1.12.69h3.53c.48 0 .91-.26 1.12-.69l1.17-2.34c.3-.6.9-.97 1.57-.97H22c.41 0 .75.34.75.75s-.34.75-.75.75h-4.36c-.1 0-.18.05-.22.14l-1.17 2.34c-.5.94-1.44 1.52-2.49 1.52"
            />
            <path
              fill="#fff"
              d="M15 22.75H9c-5.43 0-7.75-2.32-7.75-7.75v-3c0-4.69 1.74-7.04 5.64-7.61.42-.06.79.22.85.63s-.22.79-.63.85C3.97 6.33 2.75 8.05 2.75 12v3c0 4.61 1.64 6.25 6.25 6.25h6c4.61 0 6.25-1.64 6.25-6.25v-3c0-3.95-1.22-5.67-4.36-6.13a.747.747 0 0 1-.63-.85c.06-.41.44-.69.85-.63 3.9.57 5.64 2.92 5.64 7.61v3c0 5.43-2.32 7.75-7.75 7.75"
            />
          </svg>
          {selectedImage ? "Upload" : "Select Document"}
        </div>
        <div className="chat-btn" onClick={() => setChatPopup(!chatPopup)}>
          <svg
            xmlns="http://www.w3.org/2000/svg"
            width={24}
            height={24}
            fill="none"
          >
            <path
              fill="#676767"
              d="M9.99 22.78c-.6 0-1.17-.3-1.56-.83l-1.2-1.6c0 .01-.05-.02-.07-.02h-.37c-3.42 0-5.54-.93-5.54-5.54v-4c0-4.21 2.57-5.31 4.73-5.5.24-.03.52-.04.81-.04h6.4c3.62 0 5.54 1.92 5.54 5.54v4c0 .29-.01.57-.05.84-.18 2.13-1.28 4.7-5.49 4.7h-.4l-1.24 1.62c-.39.53-.96.83-1.56.83M6.79 6.75q-.345 0-.66.03c-2.32.2-3.38 1.47-3.38 4.01v4c0 3.43 1.06 4.04 4.04 4.04h.4c.45 0 .96.25 1.24.61l1.2 1.61c.22.3.5.3.72 0l1.2-1.6c.29-.39.75-.62 1.24-.62h.4c2.54 0 3.81-1.07 4-3.35.03-.24.04-.46.04-.69v-4c0-2.79-1.25-4.04-4.04-4.04z"
            />
            <path
              fill="#676767"
              d="M9.99 14.19c-.56 0-1-.45-1-1s.45-1 1-1 1 .45 1 1-.44 1-1 1M13.19 14.19c-.56 0-1-.45-1-1s.45-1 1-1 1 .45 1 1-.45 1-1 1M6.8 14.19c-.56 0-1-.45-1-1s.45-1 1-1 1 .45 1 1-.45 1-1 1"
            />
            <path
              fill="#676767"
              d="M17.94 16.29c-.2 0-.4-.08-.54-.23a.73.73 0 0 1-.2-.61c.03-.21.04-.43.04-.66v-4c0-2.79-1.25-4.04-4.04-4.04H6.8q-.345 0-.66.03a.76.76 0 0 1-.61-.2.76.76 0 0 1-.23-.6c.18-2.16 1.29-4.73 5.5-4.73h6.4c3.62 0 5.54 1.92 5.54 5.54v4c0 4.21-2.57 5.31-4.73 5.5zM6.92 5.25h6.27c3.62 0 5.54 1.92 5.54 5.54v3.87c1.7-.42 2.5-1.67 2.5-3.87v-4c0-2.79-1.25-4.04-4.04-4.04h-6.4c-2.2 0-3.44.8-3.87 2.5"
            />
          </svg>
        </div>
      </div>
      {chatPopup && (
        <ChatComponent
          chatPopup={chatPopup}
          uid={uid}
          setChatPopup={setChatPopup}
        />
      )}
      {popup && (
        <div className="popup-wrapper">
          <div className="close-btn" onClick={() => setPopup(!popup)}>
            <svg
              xmlns="http://www.w3.org/2000/svg"
              width={67}
              height={67}
              fill="none"
            >
              <rect
                width={66}
                height={66}
                x={0.5}
                y={0.5}
                fill="#fff"
                rx={33}
              />
              <rect
                width={66}
                height={66}
                x={0.5}
                y={0.5}
                stroke="#E3E3E5"
                rx={33}
              />
              <path
                fill="#4F4F4F"
                d="m34 31.5 8-8 2 1.833-8.167 8.167L44 41.667 41.667 44 33.5 35.833 25.333 44 23 41.667l8.167-8.167L23 25.333 25.333 23z"
              />
            </svg>
          </div>
          <div className="popup-ui">
            <h3>Health Score</h3>
            {healthLoader ? (
              <Loader />
            ) : (
              <div className="cente-ui">
                <div
                  style={{
                    width: "200px",
                    height: "200px",
                  }}
                >
                  <CircularProgressbar
                    value={parseInt(healthScore)}
                    text={`${healthScore}%`}
                    width={100}
                    styles={buildStyles({
                      // Rotation of path and trail, in number of turns (0-1)
                      rotation: 0.25,

                      // Whether to use rounded or flat corners on the ends - can use 'butt' or 'round'
                      strokeLinecap: "butt",

                      // Text size
                      textSize: "14px",
                      pathTransitionDuration: 0.5,

                      pathColor: "#000",
                      textColor: "#000",
                      // trailColor: "#3e98c7",
                      // backgroundColor: "#000",
                    })}
                  />
                </div>
                ;
              </div>
            )}
          </div>
        </div>
      )}
      {sharepopup && (
        <div className="popup-wrapper">
          <div className="close-btn" onClick={() => setsharepopup(!sharepopup)}>
            <svg
              xmlns="http://www.w3.org/2000/svg"
              width={67}
              height={67}
              fill="none"
            >
              <rect
                width={66}
                height={66}
                x={0.5}
                y={0.5}
                fill="#fff"
                rx={33}
              />
              <rect
                width={66}
                height={66}
                x={0.5}
                y={0.5}
                stroke="#E3E3E5"
                rx={33}
              />
              <path
                fill="#4F4F4F"
                d="m34 31.5 8-8 2 1.833-8.167 8.167L44 41.667 41.667 44 33.5 35.833 25.333 44 23 41.667l8.167-8.167L23 25.333 25.333 23z"
              />
            </svg>
          </div>
          <div className="popup-ui">
            <h3>Scan QR</h3>
            <div className="cente-ui">
              <img width="240px" src={QR} alt="" />
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ProfilePage;
