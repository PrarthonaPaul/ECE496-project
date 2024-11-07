from datasets import load_dataset
from transformers import BartForConditionalGeneration, BartTokenizer
from transformers import Trainer, TrainingArguments
import json
import torch

if torch.backends.mps.is_available():
    device = torch.device("mps")
else:
    device = torch.device("cpu")

# Load the dataset
data_files = {'train': 'train_data.json', 'validation': 'validation.json'}
dataset = load_dataset('json', data_files=data_files)

# Load BART model and tokenizer
model = BartForConditionalGeneration.from_pretrained("facebook/bart-large")
tokenizer = BartTokenizer.from_pretrained("facebook/bart-large")

def preprocess_function(examples):
    inputs = examples['input']
    targets = examples['target']
    
    # Tokenize input and target
    model_inputs = tokenizer(inputs, max_length=512, padding=True, truncation=True)
    with tokenizer.as_target_tokenizer():
        labels = tokenizer(targets, max_length=512, padding=True, truncation=True)
    
    model_inputs['labels'] = labels['input_ids']
    return model_inputs

# Tokenize the dataset
tokenized_dataset = dataset.map(preprocess_function, batched=True)

# Set training arguments
training_args = TrainingArguments(
    output_dir='./results',
    eval_strategy="epoch",
    learning_rate=2e-5,
    per_device_train_batch_size=4,
    per_device_eval_batch_size=4,
    num_train_epochs=3,
    weight_decay=0.01,
    logging_dir='./logs',
)

# Define the trainer
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=tokenized_dataset['train'],
    eval_dataset=tokenized_dataset['validation'],
)

model = model.to(device)

# Train the model
trainer.train()

# Load a test example
test_input = "Detailed Design Plan: due October 15, 2022, weight 20%"

# Tokenize the input
inputs = tokenizer(test_input, return_tensors="pt", max_length=512, truncation=True)
# inputs = {key: value.to(device) for key, value in inputs.items()}

# Generate the output using the fine-tuned model
outputs = model.generate(**inputs, max_length=512)

# Decode the output
decoded_output = tokenizer.decode(outputs[0], skip_special_tokens=True)
print(decoded_output)

# Parse the model output as JSON
structured_output = json.loads(decoded_output)

# Access the deliverable, date, and weight
deliverable = structured_output['deliverable']
due_date = structured_output['due_date']
weight = structured_output['weight']
print(f"Deliverable: {deliverable}, Due Date: {due_date}, Weight: {weight}")