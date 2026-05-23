
# Fam.ai - Gen AI-Based Medical Information Management System

### Project by **Team Lethimcode**

Fam.ai is a next-generation **AI-powered medical information management system**, secured using **blockchain technology**. The project utilizes **LLMware** and **RAG (Retrieval-Augmented Generation)** to enable seamless communication between users and the platform, ensuring efficient data storage, retrieval, and management.

---

<div align="center">
  <img src="https://cryptologos.cc/logos/ethereum-eth-logo.png" alt="Ethereum Logo" width="100" height="100"/>
  <img src="https://cryptologos.cc/logos/polygon-matic-logo.png" alt="Polygon Logo" width="100" height="100"/>
  <img src="https://cdn.nwe.io/files/x/a7/7e/6427076892cbd1e8f289553666aa.jpg" alt="llmware" width="200" height="100"/>
</div>

---

## 🚀 **Key Features**

1. **Save Medical Prescription Summaries**  
   Store and retrieve summaries of medical prescriptions for quick access and better healthcare management.  

2. **Cancer Detection from Brain MRI**  
   Advanced AI capabilities help detect cancerous patterns in Brain MRI scans.  

3. **Generate Comprehensive Health Reports**  
   Fam.ai provides an overall health report based on user inputs and medical history.

---

## 🌟 **Use Cases**

1. **Tool for Doctors**  
   A powerful assistant for doctors to manage patient records and improve diagnostic accuracy.  

2. **Insurance Company Scoring**  
   Simplifies risk evaluation for insurance companies with precise medical insights.  

3. **Family Healthcare Management**  
   Ensures secure storage and easy sharing of medical records for the entire family.

---

## 💻 **Tech Stack**

- **Backend:** Python  
- **Frontend:** React, Framer Motion, GSAP  
- **AI Integration:** LLMware, RAG  
- **Blockchain:** Solidity  

---

## 🛠️ **How to Run the Project**

### **Frontend**

1. Navigate to the frontend directory:  
   ```bash
   cd frontend
   ```
2. Install dependencies:  
   ```bash
   npm i
   ```
3. Start the development server:  
   ```bash
   npm run dev
   ```

---

### **Backend**

1. Navigate to the backend directory:  
   ```bash
   cd backend
   ```
2. Install Python dependencies:  
   ```bash
   pip install -r requirements.txt
   ```
3. Initialize the blockchain environment:  
   ```bash
   mkdir blockchain
   cd blockchain
   brownie init
   ```
4. Add the following contracts to the `contracts` folder:
   - **NFTmint.sol**  
   - **FundMe.sol**  
5. Configure the environment by adding your private key and Web3 Infura Project ID in a `.env` file.  

6. Compile the contracts:  
   ```bash
   brownie compile
   ```
7. Add the custom Polygon network:  
   ```bash
   brownie networks add custom polygon host=https://rpc.cardona.zkevm-rpc.com chainid=2442
   ```
8. Return to the backend folder and start the backend server:  
   ```bash
   cd ..
   python main.py
   ```

---

### **LLMware Integration**

#### **Run with High Response Time (Cloud)**  
Use the following Kaggle notebook for optimal LLMware performance:  
[LLMware Notebook on Kaggle](https://www.kaggle.com/code/idhanush/notebook46fcbc644e)

#### **Run Locally**  
1. Download the notebook to your computer.  
2. Open and execute the notebook using Jupyter Notebook locally.

---

## ✨ **Contributing**

We welcome contributions to enhance Fam.ai!  
Feel free to fork the repository, open issues, or submit pull requests.

---

## 📄 **License**

This project is licensed under the [MIT License](LICENSE).

---

## 🧑‍💻 **Team Members**

We are **Team Lethimcode**, passionate about revolutionizing healthcare with the power of AI and blockchain. 🚀
