# PaperPal

# <p align="center"><img src="https://github.com/Ujj1225/PaperPal/blob/main/client/src/assets/readme_logo.png" width=300 /></p>

<p align="center">
    <p align="center">
        <a href="https://github.com/Ujj1225/PaperPal" target="blank">
            <img src="https://img.shields.io/github/watchers/Ujj1225/PaperPal?style=for-the-badge&logo=appveyor" alt="Watchers"/>
        </a>
        <a href="https://github.com/Ujj1225/PaperPal/fork" target="blank">
            <img src="https://img.shields.io/github/forks/Ujj1225/PaperPal?style=for-the-badge&logo=appveyor" alt="Forks"/>
        </a>
        <a href="https://github.com/Ujj1225/PaperPal/stargazers" target="blank">
            <img src="https://img.shields.io/github/stars/Ujj1225/PaperPal?style=for-the-badge&logo=appveyor" alt="Star"/>
        </a>
    </p>
    <p align="center">
        <a href="https://github.com/Ujj1225/PaperPal/issues" target="blank">
            <img src="https://img.shields.io/github/issues/Ujj1225/PaperPal?style=for-the-badge&logo=appveyor" alt="Issue"/>
        </a>
        <a href="https://github.com/Ujj1225/PaperPal/pulls" target="blank">
            <img src="https://img.shields.io/github/issues-pr/Ujj1225/PaperPal?style=for-the-badge&logo=appveyor" alt="Open Pull Request"/>
        </a>
    </p>
    <p align="center">
        <a href="https://github.com/Ujj1225/PaperPal/blob/master/LICENSE" target="blank">
            <img src="https://img.shields.io/github/license/Ujj1225/PaperPal?style=for-the-badge&logo=appveyor" alt="License" />
        </a>
    </p>
</p>

<p align="center">
</p>

## Problem Statement

* Time-Consuming Research: Researchers and students often spend extensive time reading and understanding lengthy academic papers.

* Information Overload: Processing and retaining vast amounts of information from multiple research papers can be overwhelming.

* Difficulty in Extracting Key Insights: Identifying and focusing on the most critical information within a paper is challenging without a summarization tool.

* Limited Access to Expert Answers: Finding precise and detailed answers to specific questions about research papers can be difficult without expert guidance.

## Solutions

* Automated Summarization: The tool generates concise summaries of research papers, saving users time and effort in understanding key points.

* Streamlined Information Processing: By condensing information, the tool helps users manage and retain knowledge from multiple papers more effectively.

* Focused Insights Extraction: The application highlights the most critical information, allowing users to quickly grasp important insights without extensive reading.
    
* Expert-Level Q&A: The system answers specific questions about research papers with detailed explanations, providing users with expert-level guidance and understanding.

## Demo
https://github.com/Ujj1225/Social-Sensor/assets/97169735/39e19b2a-f720-4015-847a-b9074eaa85d0

b
## Table of Contents

- [Features](#features)
- [Installation](#installation)
- [Dependencies](#dependencies)
- [License](#license)

## Features

- Research Paper Summarization

The application uses advanced natural language processing (NLP) techniques to generate concise summaries of research papers. This feature helps users quickly understand the key points and findings of lengthy academic documents.
<details>
  <summary> Paper Summarization </summary>
  <img src="https://github.com/Ujj1225/PaperPal/blob/main/client/src/assets/summarize.png" width=750/>
</details>

- Question and Answer System

The system leverages state-of-the-art models to answer questions about the content of research papers. By providing detailed explanations alongside the answers, this feature enables users to gain a deeper understanding of specific aspects of the research.
<details>
  <summary> Question and Answer </summary>
  <img src="https://github.com/Ujj1225/PaperPal/blob/main/client/src/assets/ask.png" width=750/>
</details>

- User-Friendly Interface

The platform includes a clean and intuitive interface where users can easily upload research papers, ask questions, and view summaries and answers. This feature ensures that even users without technical expertise can benefit from the application's capabilities.
<details>
  <summary> User Interface </summary>
  <img src="https://github.com/Ujj1225/PaperPal/blob/main/client/src/assets/ui.png" width=750/>
</details>

## Installation

### Prerequisites

Before running PaperPal, you must set it up by following the given setup procedure. You must set up the Frontend, Backend and Model separately. In case of any query, feel free to contact the contributors.

### Setup

#### Follow the given steps to set up walletWISE

1. Clone the repository:

   ```bash
   git clone https://github.com/Ujj1225/PaperPal.git
   ```

2. Installation of required packages

### Frontend

```bash
cd client
npm install
```

### Backend

```bash
cd backend
npm install
```

### Model 
```bash
cd model
pip install llmware
```

3. Setting up .env file for Backend

- Create a .env file

  ```bash
  PORT = (You can use any but default is: 3000)
  ```

4. Running the project:

- Frontend and Backend file must be run together.

#### Frontend

- Navigate to Client then:

```bash
  npm run dev
```

#### Backend

- Navigate to Backend then:

```bash
  node app.js
```

# You are all set to use the application!

## Dependencies

### Frontend

- For frontend can be found in [package.json](./Client%20/package.json)

### Backend

- For backend can be found in [package.json](./Backend/package.json)

### Model

- LLMWare's specialized model namely "slim-summary-tool" and "slim-boolean-tool" is used for this project. 

## License

This project is licensed under the [MIT License](/LICENSE).
