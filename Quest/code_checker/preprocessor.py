import os
import json
import pandas as pd

def load_jsonl(file_path):
    data = []
    with open(file_path, 'r') as file:
        for line in file:
            data.append(json.loads(line))
    return pd.DataFrame(data)

def preprocess_datasets():
    train_data = load_jsonl('C://Users//anush//Documents//code_checker//data//python_train_0.jsonl')
    valid_data = load_jsonl('C://Users//anush//Documents//code_checker//data//python_valid_0.jsonl')
    test_data = load_jsonl('C://Users//anush//Documents//code_checker//data//python_test_0.jsonl')

    return train_data, valid_data, test_data

if __name__ == "__main__":
    train_data, valid_data, test_data = preprocess_datasets()
    print(train_data.head())
