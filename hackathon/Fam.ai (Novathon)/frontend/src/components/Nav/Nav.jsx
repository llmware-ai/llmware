import React from "react";
import { Link } from "react-router-dom";
import "./Nav.scss";
import { useState, useEffect } from "react";
import { useStore } from "../../context/StoreContext";

import POLLY from "../../assets/images/pollylo.svg";
import ETH from "../../assets/images/eth.png";
import ETHLOGO from "../../assets/images/ethlogo.svg";

const Nav = () => {
  const { wallet, setWallet } = useStore();
  const [walletAddress, setWalletAddress] = useState(null);
  const [provider, setProvider] = useState(null);

  const [loginPopup, setLoginPopup] = useState(false);
  const [conType, setConType] = useState(
    JSON.parse(localStorage.getItem("con"))
  );

  useEffect(() => {
    if (window.ethereum) {
      setProvider(window.ethereum);
    }
    setConType(JSON.parse(localStorage.getItem("con")));
  }, []);
  console.log(conType);

  const pollyConnect = () => {
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
          setLoginPopup(false);
          setConType("polly");
          localStorage.setItem("con", JSON.stringify("polly"));
        } catch (err) {
          console.error("Error:", err);
          setLoginPopup(false);
        }
      } else {
        console.log("MetaMask not detected");
      }
    };
    requestAccount();
  };

  const sepoliaConnect = () => {
    const requestAccount = async () => {
      if (provider) {
        try {
          // Get the current network
          const network = await provider.request({ method: "eth_chainId" });

          // Check if the network is Sepolia
          if (network !== "0xaa36a7") {
            // Sepolia chain ID in hexadecimal
            console.log("Switching to Sepolia network...");
            try {
              await provider.request({
                method: "wallet_switchEthereumChain",
                params: [{ chainId: "0xaa36a7" }], // Sepolia chain ID
              });
            } catch (switchError) {
              // If the network is not available in MetaMask, add it
              if (switchError.code === 4902) {
                try {
                  await provider.request({
                    method: "wallet_addEthereumChain",
                    params: [
                      {
                        chainId: "0xaa36a7",
                        chainName: "Sepolia Testnet",
                        nativeCurrency: {
                          name: "Ethereum",
                          symbol: "ETH",
                          decimals: 18,
                        },
                        rpcUrls: ["https://rpc.sepolia.org"],
                        blockExplorerUrls: ["https://sepolia.etherscan.io"],
                      },
                    ],
                  });
                  setLoginPopup(false);
                } catch (addError) {
                  console.error("Failed to add Sepolia network:", addError);
                  setLoginPopup(false);
                  return;
                }
              } else {
                console.error("Failed to switch network:", switchError);
                return;
              }
            }
          }

          // Request accounts
          const accounts = await provider.request({
            method: "eth_requestAccounts",
          });
          setWalletAddress(accounts[0]);
          setWallet(accounts[0]);
          console.log("Connected account:", accounts[0]);
          localStorage.setItem("wallet", accounts[0]);
          setLoginPopup(false);
          setConType("eth");
          localStorage.setItem("con", JSON.stringify("eth"));
        } catch (err) {
          console.error("Error connecting to Sepolia:", err);
          setLoginPopup(false);
        }
      } else {
        console.log("MetaMask not detected");
      }
    };

    requestAccount();
  };

  return (
    <div className="nav-container">
      <div className="nav-left-container">
        <Link to="/" className="logo">
          <svg
            xmlns="http://www.w3.org/2000/svg"
            width={32}
            height={33}
            fill="none"
          >
            <g fill="#020000" clipPath="url(#a)">
              <path d="M11.934 14.164h2.41V5.546c0-.62.259-1.215.72-1.654a2.52 2.52 0 0 1 1.736-.685 2.52 2.52 0 0 1 1.737.685c.46.44.72 1.034.72 1.654v.457l1.404-1.32c.348-.326.736-.61 1.156-.848a5.1 5.1 0 0 0-2.097-2.56 5.5 5.5 0 0 0-3.3-.813 5.44 5.44 0 0 0-3.138 1.268 5 5 0 0 0-1.677 2.826l-.046.17c0 .06 0 .116-.03.176-.028.06 0 .165 0 .248a.1.1 0 0 0 0 .044v6.257000000000001H9.092zM31.815 14.874h-9.854l-1.699 1.618 5.3 5.046 1.098 1.046.092.088v.033l.03.038.028.033.04.055v.033a.1.1 0 0 0 0 .039q.018.045.047.088v.038q.032.064.058.132v.166a.4.4 0 0 1 0 .082v.044a1 1 0 0 1 0 .138.2.2 0 0 1 0 .05v.038q.009.142 0 .286.007.142 0 .286v.07200000000000001c0 .01 0 .093-.03.132a.3.3 0 0 1 0 .066v.033c0 .033 0 .104-.046.16a.1.1 0 0 1 0 .032c0 .05-.04.105-.063.154l-.035.072-.052.088a.4.4 0 0 1-.04.066v.027l-.064.089a.6.6 0 0 1-.075.093l-.144.149-.064.055-.063.055a2.54 2.54 0 0 1-1.734.55 2.62 2.62 0 0 1-1.642-.726l-.3-.292v2.339c-.002.458-.06.914-.174 1.359a5.52 5.52 0 0 0 3.868.764 5.35 5.35 0 0 0 3.35-1.993 4.87 4.87 0 0 0 .976-3.645 5 5 0 0 0-1.94-3.276l-3.254-3.115h6.357a5 5 0 0 0 .03-2.685" />
              <path d="M3.745 10.615c.052.12.104.242.168.363q.084.156.179.313l.052.083.063.093.047.066q.289.42.664.77l4.38 4.178-1.733 1.65h4.046l1.681-1.617-6.357-6.109-.092-.093-.03-.039v-.033a.3.3 0 0 1-.04-.055v-.082a1 1 0 0 1-.052-.1v-.038a1 1 0 0 1-.057-.126v-.413a.3.3 0 0 0 0-.066.1.1 0 0 0 0-.044 2 2 0 0 1 0-.275 2 2 0 0 1 0-.281.1.1 0 0 0 0-.039v-.225a.1.1 0 0 0 0-.044l.046-.143v-.07200000000000001a1 1 0 0 1 .058-.137v-.033a1 1 0 0 1 .04-.083l.035-.066a.3.3 0 0 1 .04-.072v-.033l.052-.071.075-.094a1.7 1.7 0 0 1-.075-.544L7 7.049l.063-.05a.5.5 0 0 1 .11-.083 2.54 2.54 0 0 1 1.652-.484 2.5 2.5 0 0 1 1.579.672l.352.33V5.546c0-.458.056-.914.168-1.359a5.55 5.55 0 0 0-5.282.43l-.116.076c-.092.06-.18.132-.272.204l-.052.033-.265.237q-.085.072-.162.154l-.087.132h-.064v.055l-.04.044-.11.132-.121.154-.058.082-.064.083-.052.077-.034.055-.098.132-.093.154v.033q-.035.082-.08.16l-.088.181c0 .06-.052.121-.075.182v.055l-.052.149q-.024.067-.04.137a1 1 0 0 0 0 .1 4 4 0 0 0-.081.34v.055a1 1 0 0 1 0 .133.4.4 0 0 1 0 .077 4.87 4.87 0 0 0 .104 2.327zM21.383 5.034l-.138.133-4.387 4.176-1.705-1.65v3.851l.856.897.791.754 2.457-2.338L22.1 8.149l1.098-1.045.185-.155.197-.132.179-.104.133-.06h.029l.086-.034h.139l.139-.038h.583c.473-.008.937.115 1.338.352.4.238.72.581.922.988.2.407.273.86.21 1.306s-.26.865-.568 1.206a2 2 0 0 1-.15.16l-1.104 1.045h-3.468V9.156l-2.843 2.708v2.3h7.513l1.936-1.844a4.93 4.93 0 0 0 1.55-3.153 4.85 4.85 0 0 0-.972-3.357l-.237-.286-.052-.071a3 3 0 0 0-.26-.27 5.37 5.37 0 0 0-3.167-1.447 6 6 0 0 0-.752 0h-.8839999999999999l-.185.11q-.135.024-.266.066l-.213.06-.37.132h-.035a6 6 0 0 0-.774.397h-.047l-.086.055-.122.082-.196.149q-.109.117-.203.247M24.51 21.544l-2.843-2.708h-2.41v8.629c0 .62-.26 1.215-.72 1.654a2.52 2.52 0 0 1-1.737.685 2.52 2.52 0 0 1-1.736-.685 2.28 2.28 0 0 1-.72-1.654v-.474l-1.398 1.327a5.9 5.9 0 0 1-1.156.842 5.1 5.1 0 0 0 2.1 2.524c.971.6 2.122.882 3.277.8a5.44 5.44 0 0 0 3.117-1.249 5 5 0 0 0 1.689-2.79 1 1 0 0 0 0-.105v-.242a.3.3 0 0 0 0-.072 1 1 0 0 0 0-.093v.002-.156a.5.5 0 0 0 0-.089v-6.147z" />
              <path d="m12.01 28.158.236-.192.139-.127 4.415-4.226 1.734 1.65v-3.852l-.913-.875-.792-.753-2.456 2.333-2.872 2.735-1.098 1.045-.185.16-.197.138h-.029l-.185.104-.132.06h-.133l-.14.05h-.115l-.115.028h-.439a2.54 2.54 0 0 1-1.292-.397 2.37 2.37 0 0 1-.873-.99c-.188-.402-.253-.845-.188-1.28s.257-.844.555-1.18l.353-.33H5.3a6.4 6.4 0 0 1-1.428-.165 4.83 4.83 0 0 0 .172 4.613c.413.7.996 1.296 1.7 1.738a5.46 5.46 0 0 0 2.347.803h.237q.367.024.734 0h.809l.249-.06.248-.078.185-.066h.035l.133-.055.08-.033.18-.17.063-.034.139-.066h.046l.174-.093h.028l.174-.105.086-.06.128-.083z" />
              <path d="M5.3 21.544H11.5v2.294l2.843-2.707v-2.295H5.3a2.6 2.6 0 0 1-.976-.144 2.5 2.5 0 0 1-.837-.499 2.3 2.3 0 0 1-.564-.772 2.24 2.24 0 0 1 0-1.842 2.3 2.3 0 0 1 .564-.772c.24-.219.525-.388.837-.499s.644-.16.976-.144h.48l-1.388-1.337a5.8 5.8 0 0 1-.89-1.073 5.25 5.25 0 0 0-2.74 2.129A4.84 4.84 0 0 0 .04 17.18a4.96 4.96 0 0 0 1.62 2.994 5.42 5.42 0 0 0 3.24 1.353z" />
            </g>
            <defs>
              <clipPath id="a">
                <path fill="#fff" d="M0 .5h32v32H0z" />
              </clipPath>
            </defs>
          </svg>
          Fam.ai
        </Link>
      </div>
      <div className="nav-right-container">
        <button onClick={() => setLoginPopup(true)} className="login-btn">
          {conType == "polly" && (
            <svg
              xmlns="http://www.w3.org/2000/svg"
              width={26}
              height={24}
              fill="none"
            >
              <path
                fill="#fff"
                d="M26 12.478v6.207a2.4 2.4 0 0 1-.286 1.103 2.2 2.2 0 0 1-.758.812l-5.077 3.097a1.95 1.95 0 0 1-1.04.303 1.95 1.95 0 0 1-1.04-.303L12.723 20.6a2.2 2.2 0 0 1-.759-.812 2.4 2.4 0 0 1-.286-1.104v-1.739l2.598-1.6v3.03l4.55 2.797 4.547-2.797v-5.578L18.826 10 8.17 16.536c-.317.19-.676.291-1.04.291-.365 0-.724-.1-1.04-.29l-5.077-3.11a2.2 2.2 0 0 1-.743-.814A2.3 2.3 0 0 1 0 11.518V5.312c.002-.387.098-.767.28-1.103a2.2 2.2 0 0 1 .759-.812L6.115.3A1.96 1.96 0 0 1 7.154 0c.365 0 .724.103 1.039.3l5.076 3.097c.315.197.576.476.759.812.182.335.28.715.283 1.103V7.05l-2.616 1.588v-3.01l-4.55-2.796L2.598 5.63v5.57l4.547 2.797L17.81 7.46c.317-.19.676-.29 1.04-.29.365 0 .723.1 1.04.29l5.074 3.11c.313.197.572.476.752.81s.276.713.278 1.098z"
              />
            </svg>
          )}
          {conType == "eth" && <img src={ETHLOGO} alt="" />}

          {wallet ? `${wallet.substring(0, 8)}xxxxx` : "Login"}
        </button>
        {loginPopup && (
          <div className="wallets">
            <div className="wallet-btn" onClick={() => pollyConnect()}>
              <img src={POLLY} alt="" />
            </div>
            <div className="wallet-btn" onClick={() => sepoliaConnect()}>
              <img src={ETH} alt="" />
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default Nav;
