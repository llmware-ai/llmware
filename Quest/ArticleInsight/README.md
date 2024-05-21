
---
# ArticleInsight: Your AI-Powered Article Analysis Tool
<p align="center">
<p align="center">
<a href="https://github.com/rajesh-adk-137/ArticleInsight/" target="blank">
<img src="https://img.shields.io/github/watchers/rajesh-adk-137/ArticleInsight?style=for-the-badge&logo=appveyor" alt="Watchers"/>
</a>
<a href="https://github.com/rajesh-adk-137/ArticleInsight/fork" target="blank">
<img src="https://img.shields.io/github/forks/rajesh-adk-137/ArticleInsight?style=for-the-badge&logo=appveyor" alt="Forks"/>
</a>
<a href="https://github.com/rajesh-adk-137/ArticleInsight/stargazers" target="blank">
<img src="https://img.shields.io/github/stars/rajesh-adk-137/ArticleInsight?style=for-the-badge&logo=appveyor" alt="Star"/>
</a>
</p>
<p align="center">
<a href="https://github.com/rajesh-adk-137/ArticleInsight/issues" target="blank">
<img src="https://img.shields.io/github/issues/rajesh-adk-137/ArticleInsight?style=for-the-badge&logo=appveyor" alt="Issue"/>
</a>
<a href="https://github.com/rajesh-adk-137/ArticleInsight/pulls" target="blank">
<img src="https://img.shields.io/github/issues-pr/rajesh-adk-137/ArticleInsight?style=for-the-badge&logo=appveyor" alt="Open Pull Request"/>
</a>
</p>
<p align="center">
<a href="https://github.com/rajesh-adk-137/ArticleInsight/blob/master/LICENSE" target="blank">
<img src="https://img.shields.io/github/license/rajesh-adk-137/ArticleInsight?style=for-the-badge&logo=appveyor" alt="License" />
</a>
</p>
</p>

## Table of Contents

- [Overview](#overview)
- [Key Features](#key-features)
  - [Content Categorization](#content-categorization)
  - [Article Summarization](#article-summarization)
  - [Tag Generation](#tag-generation)
  - [Sentiment Analysis](#sentiment-analysis)
  - [Question Answering](#question-answering)
- [Supported Platforms](#supported-platforms)
- [Getting Started](#getting-started)
- [Demo](#demo)
- [Dependencies](#dependencies)
- [Installation](#installation)
  - [Clone the Repository](#clone-the-repository)
  - [Frontend Setup](#frontend-setup)
  - [Backend Setup](#backend-setup)
- [Usage](#usage)
- [Screenshots](#screenshots)
- [Contributing](#contributing)
- [License](#license)
- [Acknowledgments](#acknowledgments)

## Overview

ArticleInsight is a cutting-edge web application that harnesses the power of advanced AI models from LLMWare to provide comprehensive insights and in-depth analysis of articles. Designed to streamline the process of understanding and extracting value from written content, ArticleInsight offers a suite of powerful features that cater to a wide range of users, including researchers, journalists, content creators, and avid readers.

In today's information-rich landscape, sifting through vast amounts of data and extracting meaningful insights can be a daunting task. ArticleInsight aims to alleviate this challenge by leveraging state-of-the-art natural language processing (NLP) models from LLMware to deliver accurate and insightful analyses of articles from popular platforms such as Dev.to and Medium.

## Key Features

### Content Categorization

ArticleInsight's intelligent categorization system employs advanced algorithms to classify articles into relevant category which appears as title in the response, ensuring that users can quickly identify and access content that aligns with their interests. This feature streamlines content discovery and enables users to explore specific domains more efficiently.

### Article Summarization

Recognizing the need for concise and digestible information, ArticleInsight offers a powerful summarization feature. By leveraging cutting-edge language models, the application generates comprehensive yet succinct summaries of articles, allowing users to quickly grasp the main ideas and key points without having to read through lengthy content.

### Tag Generation

Effective tagging is crucial for enhancing discoverability and organizing content. ArticleInsight's tag generation feature uses advanced NLP techniques to automatically generate relevant tags for articles, ensuring that users can easily find and navigate related content based on their interests.

### Sentiment Analysis

Understanding the sentiment behind comments and feedback is essential for gauging public opinion and sentiment towards a particular topic or article. ArticleInsight's sentiment analysis feature leverages advanced machine learning models to analyze comments and determine the overall sentiment, providing users with valuable insights into how their content is being received.

### Question Answering

ArticleInsight's question answering feature empowers users to obtain precise and contextual answers to their questions about an article's content. By leveraging deep learning models trained on vast knowledge bases, the application can provide accurate and relevant responses, enhancing the user's understanding of the subject matter.

## Supported Platforms

Initially, ArticleInsight supports articles from two popular platforms: Dev.to and Medium. Users can simply provide the URL of an article from either of these platforms, and ArticleInsight will process the content, generating insightful analyses and summaries.

## Getting Started

ArticleInsight offers a user-friendly interface that allows users to easily input article URLs and access the various features provided by the application. With its powerful AI-driven capabilities, ArticleInsight aims to revolutionize the way users consume and engage with written content, empowering them to make informed decisions and gain deeper insights effortlessly.

## Demo
<video src="https://github.com/rajesh-adk-137/ArticleInsight/assets/89499267/0b966113-b33c-455d-bc73-ead668c8fc96"></video>

## Dependencies
- React
- Uvicorn
- Yarn
- FastAPI
- Python
- LLMWare models

## Installation

### Clone the Repository
```bash
git clone https://github.com/rajesh-adk-137/ArticleInsight.git
```

### Frontend Setup

#### Navigate to the frontend directory:
```bash
cd ArticleInsight/frontend
```

#### Install dependencies:
```bash
yarn install
```

#### Start the development server:
```bash
yarn run dev
```

### Backend Setup

#### Navigate to the backend directory:
```bash
cd ../backend
```

#### Set up a virtual environment (recommended):
```bash
python -m venv env
source env/bin/activate  # On Windows use `env\Scripts\activate`
```

#### Install dependencies:
```bash
pip install -r requirements.txt
```

**Note**: The initial setup might take some time as it involves downloading five models.

#### Start the API server:
```bash
uvicorn api_article:app --reload
```

## Usage

#### Visit the frontend application:
Open your browser and navigate to `http://localhost:5173`.

#### Make sure the backend is running at:
`http://localhost:8000`.


## Screenshots
Landing Page:
![Landing](https://github.com/rajesh-adk-137/ArticleInsight/assets/89499267/28c917da-6f80-4bba-b287-ef8440fc6fdb)
Home Page:
![Home](https://github.com/rajesh-adk-137/ArticleInsight/assets/89499267/d0d1cfbf-4402-405c-9849-4244f571d264)
ArticleInsight-1:
![ArticleInsight-1](https://github.com/rajesh-adk-137/ArticleInsight/assets/89499267/9121a262-0900-4b22-9dbb-06603c157a9d)
ArticleInsight-2:
![ArticleInsight-2](https://github.com/rajesh-adk-137/ArticleInsight/assets/89499267/ac450183-c3ed-44b5-a28a-e5f90912336b)
About Section:
![About](https://github.com/rajesh-adk-137/ArticleInsight/assets/89499267/1790c9e0-b10d-4f67-9f48-cb9518f3e315)


## Contributing

We welcome contributions from the community! If you'd like to contribute to ArticleInsight, please follow these steps:

1. **Fork the Repository**: Click the "Fork" button on GitHub to create your copy.

2. **Clone Your Fork**:
   ```bash
   git clone https://github.com/yourusername/ArticleInsight.git
   ```

3. **Create a Branch**:
   ```bash
   git checkout -b your-branch-name
   ```

4. **Make Changes**: Implement your changes.

5. **Commit Your Changes**:
   ```bash
   git commit -m "Description of your changes"
   ```

6. **Push Your Changes**:
   ```bash
   git push -u origin your-branch-name
   ```

7. **Create a Pull Request**: Submit your changes for review.

## License

This project is licensed under the [MIT License](LICENSE).

## Acknowledgments

- [LLMWare](https://www.llmware.ai/) for their powerful AI models
- [React](https://reactjs.org/) for the amazing JavaScript library
- [Yarn](https://yarnpkg.com/) for the reliable package manager
- [FastAPI](https://fastapi.tiangolo.com/) for the fast and efficient web framework
- [Python](https://www.python.org/) for the versatile programming language

---


