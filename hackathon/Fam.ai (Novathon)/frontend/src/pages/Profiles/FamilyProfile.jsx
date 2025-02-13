import React, { useState, useEffect } from "react";
import "./FamilyProfilePage.scss";

import BOY from "../../assets/images/male.svg";
import GIRL from "../../assets/images/female.svg";
import Form from "../../components/form/Form";
import { AnimatePresence } from "motion/react";
import { Link } from "react-router-dom";
import ChatComponent from "../../components/ChatUI/Chatui";
import { deleteProfile, getProfiles } from "../../utils/utils";
import { useStore } from "../../context/StoreContext";
const FamilyProfile = () => {
  const { wallet, setWallet } = useStore();
  const [popup, setPopup] = useState(false);
  const [profiles, setProfiles] = useState(null);
  const [trigger, setTrigger] = useState(false);

  //to delete profile
  const deleteProfileClick = async (prfid) => {
    const result = await deleteProfile(wallet, prfid);
    setTrigger(!trigger);
  };

  useEffect(() => {
    const fetchProfiles = async () => {
      try {
        const result = await getProfiles(wallet);
        setProfiles(result);
        console.log(result);
      } catch (error) {
        console.error("Error fetching profiles:", error);
      }
    };

    fetchProfiles();
  }, [wallet, popup, trigger]);

  return (
    <div className="family-page">
      <div className="fam-profiles">
        {profiles?.map((profile) => (
          <div className="profile-card-wrapper">
            <div
              className="delete-btn"
              onClick={() => deleteProfileClick(profile.prfid)}
            >
              <svg
                xmlns="http://www.w3.org/2000/svg"
                width={20}
                height={20}
                fill="none"
              >
                <path
                  fill="#FF3C26"
                  d="M17.5 5.608h-.067C13.025 5.167 8.625 5 4.267 5.442l-1.7.166a.63.63 0 0 1-.134-1.25l1.7-.166c4.434-.45 8.925-.275 13.425.166a.626.626 0 0 1 .559.684.617.617 0 0 1-.617.566"
                />
                <path
                  fill="#FF3C26"
                  d="M7.083 4.767c-.033 0-.066 0-.108-.009a.627.627 0 0 1-.508-.716L6.65 2.95c.133-.8.317-1.908 2.258-1.908h2.184c1.95 0 2.133 1.15 2.258 1.916l.183 1.084a.62.62 0 0 1-.508.716.62.62 0 0 1-.717-.508l-.183-1.083c-.117-.725-.142-.867-1.025-.867H8.917c-.884 0-.9.117-1.025.858L7.7 4.242a.625.625 0 0 1-.617.525M12.675 18.958h-5.35c-2.908 0-3.025-1.608-3.117-2.908l-.541-8.392a.63.63 0 0 1 .583-.666.63.63 0 0 1 .667.583l.541 8.392c.092 1.266.125 1.741 1.867 1.741h5.35c1.75 0 1.783-.475 1.867-1.741l.541-8.392a.637.637 0 0 1 .667-.583.626.626 0 0 1 .583.666l-.541 8.392c-.092 1.3-.209 2.908-3.117 2.908"
                />
                <path
                  fill="#FF3C26"
                  d="M11.383 14.375H8.608a.63.63 0 0 1-.625-.625.63.63 0 0 1 .625-.625h2.775a.63.63 0 0 1 .625.625.63.63 0 0 1-.625.625M12.083 11.042H7.917a.63.63 0 0 1-.625-.625.63.63 0 0 1 .625-.625h4.166a.63.63 0 0 1 .625.625.63.63 0 0 1-.625.625"
                />
              </svg>
            </div>
            <Link
              to={`/fam/${profile.prfid}`}
              key={profile.prfid}
              className="profile-card"
            >
              <div className="left-profile-box">
                <div className="name">{profile.name}</div>
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
                  {profile.dob}
                </div>
                <div className="data-tabs">
                  <div className="tabb">{profile.gender}</div>
                  <div className="tabb">{profile.blood}</div>
                </div>
              </div>
              {profile.gender == "Male" ? (
                <img src={BOY} className="avathar"></img>
              ) : (
                <img src={GIRL} className="avathar"></img>
              )}
            </Link>
          </div>
        ))}
      </div>
      <div className="bottom-bar">
        <div className="add-profile-btn" onClick={() => setPopup(!popup)}>
          Add New Member
        </div>
      </div>
      <AnimatePresence>
        {popup && <Form popup={popup} setPopup={setPopup} />}
      </AnimatePresence>
      {/* <ChatComponent/> */}
    </div>
  );
};

export default FamilyProfile;
