from datasets import load_dataset

dataset = load_dataset("vicgalle/alpaca-gpt4", split="train")
print(dataset.column_names)