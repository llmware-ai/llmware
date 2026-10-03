import { baseUrl } from "../constants";
import toast from "react-hot-toast";

export const createAcc = async (wallet) => {
  try {
    const response = await fetch(`${baseUrl}/user/create_account`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: "Bearer your-auth-token",
        "ngrok-skip-browser-warning": "69420",
        Address: wallet,
      },
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.msg || "Acc failed to create");
    }

    const result = await response.json();
    console.log("Acc created:", result);
    toast.success("Account created 💪🏻");
    return result;
  } catch (error) {
    console.error("Acc error:", error);
    toast.error("Can't create an account🙂");
  }
};

//create new profile
export const createIndiProfile = async (wallet, formData) => {
  try {
    const response = await fetch(`${baseUrl}/user/create_profile`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: "Bearer your-auth-token",
        "ngrok-skip-browser-warning": "69420",
        address: wallet,
      },
      body: JSON.stringify({
        name: formData.name,
        dob: formData.dob,
        gender: formData.gender,
        blood: formData.bloodGroup,
      }),
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.msg || "Acc failed to create");
    }

    const result = await response.json();
    console.log("Acc created:", result);
    return result;
  } catch (error) {
    console.error("Acc error:", error);
  }
};

// get profiles
export const getProfiles = async (wallet) => {
  try {
    const response = await fetch(`${baseUrl}/user/get_profiles`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: "Bearer your-auth-token",
        "ngrok-skip-browser-warning": "69420",
        address: wallet,
      },
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.msg || "can't get profiles");
    }

    const result = await response.json();
    console.log("profiles done:", result);
    return result;
  } catch (error) {
    console.error("profiles fetch error:", error);
  }
};

// get profile data
export const getProfileData = async (wallet, prfid) => {
  try {
    const response = await fetch(`${baseUrl}/user/get_profile?prfid=${prfid}`, {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
        Authorization: "Bearer your-auth-token",
        "ngrok-skip-browser-warning": "69420",
        address: wallet,
      },
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.msg || "can't get profiles");
    }

    const result = await response.json();
    console.log("profiles done:", result);
    return result;
  } catch (error) {
    console.error("profiles fetch error:", error);
  }
};

//delete profile
export const deleteProfile = async (wallet, prfid) => {
  try {
    const response = await fetch(`${baseUrl}/user/delete_profile`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: "Bearer your-auth-token",
        "ngrok-skip-browser-warning": "69420",
        address: wallet,
      },
      body: JSON.stringify({
        prfid: prfid,
      }),
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.msg || "Acc failed to create");
    }

    const result = await response.json();
    console.log("profile deleted:", result);
    return result;
  } catch (error) {
    console.error("deletion error:", error);
  }
};

//delete profile
export const fetchDocuments = async (wallet, prfid) => {
  const url = new URL(`${baseUrl}/document/list_documents`);
  url.searchParams.append("prfid", prfid);
  try {
    const response = await fetch(url, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: "Bearer your-auth-token",
        "ngrok-skip-browser-warning": "69420",
        address: wallet,
      }
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.msg || "Acc failed to create");
    }

    const result = await response.json();
    console.log("profile deleted:", result);
    return result;
  } catch (error) {
    console.error("deletion error:", error);
  }
};

//score
export const fetchScore = async (wallet, prfid) => {
  const url = new URL(`${baseUrl}/chat/score`);
  url.searchParams.append("prfid", prfid);
  try {
    const response = await fetch(url, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: "Bearer your-auth-token",
        "ngrok-skip-browser-warning": "69420",
        address: wallet,
      }
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.msg || "Acc failed to create");
    }

    const result = await response.json();
    console.log("profile deleted:", result);
    return result;
  } catch (error) {
    console.error("deletion error:", error);
  }
};

