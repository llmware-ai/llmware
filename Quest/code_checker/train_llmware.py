import os
import json
import pandas as pd
import torch
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    Trainer,
    TrainingArguments,
    DataCollatorWithPadding
)
from datasets import Dataset
from torch.nn import CrossEntropyLoss


def load_jsonl(file_path):
    data = []
    with open(file_path, 'r') as file:
        for line in file:
            data.append(json.loads(line))
    return pd.DataFrame(data)


def preprocess_datasets():
    print("Loading datasets...")
    train_data = load_jsonl('C://Users//anush//Documents//code_checker//data//python_train_0.jsonl')
    valid_data = load_jsonl('C://Users//anush//Documents//code_checker//data//python_valid_0.jsonl')
    test_data = load_jsonl('C://Users//anush//Documents//code_checker//data//python_test_0.jsonl')
    print("Datasets loaded.")
    return train_data, valid_data, test_data


def tokenize_code(tokenizer, code):
    return tokenizer(code, padding="max_length", truncation=True, return_tensors="pt", max_length=512)


def main():
    # Load pre-trained model and tokenizer
    model_name = "llmware/bling-tiny-llama-v0"
    print("Loading model...")
    model = AutoModelForCausalLM.from_pretrained(model_name)
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    
    # Add padding token if missing
    if tokenizer.pad_token is None:
        tokenizer.add_special_tokens({'pad_token': tokenizer.eos_token})
        model.resize_token_embeddings(len(tokenizer))
        
    print("Model and tokenizer loaded.")

    # Preprocess datasets
    train_data, valid_data, test_data = preprocess_datasets()

    # Tokenize datasets with padding
    subset_size = 1 # Adjust the subset size as needed
    print(f"Tokenizing a subset of {subset_size} samples...")
    train_data_subset = train_data[:subset_size]
    valid_data_subset = valid_data[:subset_size]
    test_data_subset = test_data[:subset_size]

    train_data_subset['input_ids'] = train_data_subset['code'].apply(lambda x: tokenize_code(tokenizer, x)['input_ids'].squeeze().tolist())
    train_data_subset['attention_mask'] = train_data_subset['code'].apply(lambda x: tokenize_code(tokenizer, x)['attention_mask'].squeeze().tolist())
    valid_data_subset['input_ids'] = valid_data_subset['code'].apply(lambda x: tokenize_code(tokenizer, x)['input_ids'].squeeze().tolist())
    valid_data_subset['attention_mask'] = valid_data_subset['code'].apply(lambda x: tokenize_code(tokenizer, x)['attention_mask'].squeeze().tolist())
    test_data_subset['input_ids'] = test_data_subset['code'].apply(lambda x: tokenize_code(tokenizer, x)['input_ids'].squeeze().tolist())
    test_data_subset['attention_mask'] = test_data_subset['code'].apply(lambda x: tokenize_code(tokenizer, x)['attention_mask'].squeeze().tolist())

    print("Subset tokenized.")

    # Convert to Hugging Face Datasets format
    def convert_to_dataset(df):
        return Dataset.from_pandas(df[['input_ids', 'attention_mask']])

    print("Converting datasets to Hugging Face format...")
    train_dataset = convert_to_dataset(train_data_subset)
    valid_dataset = convert_to_dataset(valid_data_subset)
    test_dataset = convert_to_dataset(test_data_subset)
    print("Datasets converted.")

    # Add labels for training
    train_dataset = train_dataset.map(lambda examples: {'labels': examples['input_ids']})
    valid_dataset = valid_dataset.map(lambda examples: {'labels': examples['input_ids']})

    # Define data collator
    data_collator = DataCollatorWithPadding(tokenizer=tokenizer)

    # Define training arguments
    training_args = TrainingArguments(
        output_dir="./results",
        eval_strategy="epoch",
        learning_rate=2e-5,
        per_device_train_batch_size=1,
        per_device_eval_batch_size=1,
        num_train_epochs=3,
        weight_decay=0.01
    )

    # Define a custom Trainer class to handle model outputs correctly
    # class CustomTrainer(Trainer):
    #     def compute_loss(self, model, inputs):
    #         outputs = model(**inputs)
    #         loss_fct = CrossEntropyLoss()
            
    #         # Check if lm_labels is None
    #         lm_labels = inputs.get("labels")
    #         if lm_labels is None:
    #             raise ValueError("Labels (lm_labels) are missing in the inputs.")

    #         # Compute the loss
    #         loss = loss_fct(outputs.logits.view(-1, outputs.logits.size(-1)), lm_labels.view(-1))
    #         return loss

    class CustomTrainer(Trainer):
        def compute_loss(self, model, inputs, return_outputs=False):
            outputs = model(**inputs)
            loss_fct = CrossEntropyLoss()
            
            # Check if lm_labels is None
            lm_labels = inputs.get("labels")
            if lm_labels is None:
                raise ValueError("Labels (lm_labels) are missing in the inputs.")

            # Compute the loss
            loss = loss_fct(outputs.logits.view(-1, outputs.logits.size(-1)), lm_labels.view(-1))
            return (loss, outputs) if return_outputs else loss

    # Initialize the custom trainer
    trainer = CustomTrainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=valid_dataset,
        data_collator=data_collator
    )

    # Train the model using the custom trainer
    print("Training...")
    trainer.train()
    print("Training completed.")


if __name__ == "__main__":
    main()
