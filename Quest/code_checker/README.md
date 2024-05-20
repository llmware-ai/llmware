# Code Completion with AI-Bloks LLMWare

This project utilizes AI-Bloks's LLMWare model to provide code completion capabilities. The project includes training a language model using the `llmware/bling-tiny-llama-v0` model and a Streamlit application for testing and demonstrating code completion.

## Table of Contents

- [Installation](#installation)
- [Dataset Preparation](#dataset-preparation)
- [Model Training](#model-training)
- [Streamlit App](#streamlit-app)
- [Usage](#usage)
- [Examples](#examples)
- [Video Demo](#video-demo)
- [Output](#output)
- [Acknowledgements](#acknowledgements)

## Installation

To get started, clone this repository and install the required packages:

```sh
git clone https://github.com/Anushreel/llm_checker.git
cd code-completion-llmware
pip install -r requirements.txt
```

## Dataset Preparation

The datasets should be in JSONL format. Each line in the JSONL file should represent a code example. Place your datasets in the `data` directory with the following filenames:

- `python_train_0.jsonl`
- `python_valid_0.jsonl`
- `python_test_0.jsonl`

I have used data from **codesearchnet**. The dataset is too large to upload to GitHub.

## Model Training

To train the model, run the `train_llmware.py` script. This script will load the datasets, preprocess them, and train the LLMWare model.

```sh
python train_llmware.py
```

`app_llmware.py` is a Flask app

Postman demo here

<img src="https://github.com/Anushreel/llm_checker/blob/master/Screenshot%202024-05-19%20012615.png" alt="Image Description" width="560" height="315">

## Streamlit App

The Streamlit app provides an interface for testing the code completion model. The app allows users to input incomplete code snippets and get the completed code from the model.

### Running the Streamlit App

To run the Streamlit app, use the following command:

```sh
streamlit run app.py
```
### Usage
+ Train the Model: Ensure your datasets are in place and run the training script.
+ Run the Streamlit App: Start the Streamlit app to interact with the model.
+ Input Incomplete Code: Enter an incomplete code snippet into the text area in the Streamlit app.
+ Get Completed Code: Click the "Complete Code" button to see the model's completion.

## Examples

### Example 1

**Incomplete code:**

```python
def add(a, b):
    return a + b

def multiply(a, b):
    return a
```

**Expected:**

```python
def add(a, b):
    return a + b

def multiply(a, b):
    return a * b

if __name__ == "__main__":
    main()
```

### Example 2

```python
name = "Alice"
age = 25
greeting = f"Hello, my name is {name} and I am
```

**Corrected:**

```python
name = "Alice"
age = 25
greeting = f"Hello, my name is {name} and I am {age} years old."
```

### Example 3

```python
matrix = [
    [1, 2, 3],
    [4, 5, 6],
    [7, 8, 9]
]
for row in matrix:
    for element in row:
        print(element,
```

**Corrected:**

```python
matrix = [
    [1, 2, 3],
    [4, 5, 6],
    [7, 8, 9]
]
for row in matrix:
    for element in row:
        print(element, end=" ")
    print()
```

## Video Demo

Watch a demonstration of our code completion system in action:

<iframe width="560" height="315" src="https://github.com/Anushreel/llm_checker/blob/master/code.mp4" frameborder="0" allowfullscreen></iframe>


## Output

<img src="https://github.com/Anushreel/llm_checker/blob/master/Screenshot%202024-05-19%20012615.png" alt="Image Description" width="560" height="315">

<img src="https://github.com/Anushreel/llm_checker/blob/master/Screenshot%202024-05-19%20012615.png" alt="Image Description" width="560" height="315">

## Acknowledgements

This project utilizes the AI-Bloks LLMWare model and the Hugging Face transformers library. Special thanks to the developers and maintainers of these tools for their excellent work and contributions to the machine learning community.
