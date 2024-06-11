---
layout: default
title: Notebooks
parent: Examples
nav_order: 11
description: overview of the major modules and classes of LLMWare  
permalink: /examples/notebooks
---
# Notebooks - Introduction by Examples
We introduce ``llmware`` through self-contained examples.

# Understanding Google Colab and Jupyter Notebooks

Welcome to our project documentation! A common point of confusion among developers new to data science and machine learning workflows is the relationship and differences between Google Colab and Jupyter Notebooks. This README aims to clarify these parts to ensure everyone is on the same page.

## What are Jupyter Notebooks?

Jupyter Notebooks is an open-source web application that lets you create and share documents that have live code, equations, visualizations, and narrative text. Uses include: data cleaning and transformation, numerical simulation, statistical modeling, data visualization, machine learning, and much more.

## What is Google Colab?

Google Colab (or Colaboratory) is a free Jupyter notebook environment that requires no setup and runs in the cloud. It offers a similar interface to Jupyter Notebooks and lets users write and execute Python in a web browser. Google Colab also provides free access to computing resources, including GPUs and TPUs, making it highly popular for machine learning and data analysis projects.

## Key Similarities

- **Interface:** Both platforms use the Jupyter Notebook interface, which supports mixing executable code, equations, visualizations, and narrative text in a single document.
- **Language Support:** Primarily, both are used for executing Python code. However, Jupyter Notebooks support other languages such as R and Julia.
- **Use Cases:** They are widely used for data analysis, machine learning, and education, allowing for easy sharing of results and methodologies.

## Increase Google Colab Computational Power with T4 GPU

Our models are designed to run on at least 16GB of RAM. By default Google Colab provides ~13GB of RAM, which significantly slows computational speed. To ensure the best performance when using our models, we highly recommend enabling the T4 GPU in Colab. This will provide the notebook with additional resources, including 16GB of RAM, allowing our models to run smoothly and efficiently.

Steps to enabling T4 GPU in Colab:
1. In your Colab notebook, click on the "Runtime" tab
2. Select "Change runtime type"
3. Under "Hardware Accelerator", select T4 GPU

NOTE: There is a weekly usage limit on using T4 for free.

## Key Differences

- **Execution Environment:** Jupyter Notebooks can be run locally on your machine or on a server, but Google Colab is hosted in the cloud.
- **Access to Resources:** Google Colab provides free access to hardware accelerators (GPUs and TPUs) which is not inherently available in Jupyter Notebooks unless specifically set up by the user on their servers.
- **Collaboration:** Google Colab offers easier collaboration features, similar to Google Docs, letting multiple users work on the same notebook simultaneously.

## Conclusion

While Google Colab and Jupyter Notebooks might seem different they are built on the same idea and offer similar functionalities with a few distinctions, mainly in execution environment and access to computing resources. Understanding these platforms' capabilities can significantly enhance your data science and machine learning projects.

We hope this guide has helped clarify the similarities and differences between Google Colab and Jupyter Notebooks. Happy coding!

