import pandas as pd
import torch
from datasets import Dataset
from transformers import RobertaTokenizer, RobertaForSequenceClassification, Trainer, TrainingArguments
from evaluate import load

class ModelPipeline:
    def __init__(self, data_path, model_name="roberta-base", max_length=128):
        self.data_path = data_path
        self.model_name = model_name
        self.max_length = max_length
        self.model = None
        self.tokenizer = RobertaTokenizer.from_pretrained(self.model_name)
        self.dataset = None
        self.train_dataset = None
        self.val_dataset = None
        self.test_dataset = None
        self.trainer = None
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    def load_and_preprocess_data(self):
        """Load and preprocess the dataset."""
        df = pd.read_csv(self.data_path)
        df = df.drop(columns=['Unnamed: 0'], errors='ignore')  # Remove unwanted column
        df = df.drop(0).reset_index(drop=True)  # Drop first row
        df.columns = ['pdf', 'tasks', 'class']
        df['pdf'] = df['pdf'].fillna(method='ffill')
        df = df.dropna(subset=['tasks', 'class'])  # Ensure no missing values in relevant columns
        
        # Convert to HuggingFace dataset
        self.dataset = Dataset.from_pandas(df)
        self.dataset = self.dataset.class_encode_column("class")

        # Tokenize the dataset
        self.tokenized_datasets = self.dataset.map(self.tokenize_function, batched=True)
        self.tokenized_datasets = self.tokenized_datasets.map(lambda x: {'labels': x['class']})

        # Split the dataset into train, validation, and test
        train_val_split = self.tokenized_datasets.train_test_split(test_size=0.2)
        test_valid_split = train_val_split['test'].train_test_split(test_size=0.5)

        self.tokenized_datasets = {
            'train': train_val_split['train'],
            'test': test_valid_split['test'],
            'validation': test_valid_split['train']
        }

        self.train_dataset = self.tokenized_datasets['train']
        self.val_dataset = self.tokenized_datasets['validation']
        self.test_dataset = self.tokenized_datasets['test']

    def tokenize_function(self, examples):
        """Tokenize the text column."""
        return self.tokenizer(examples["tasks"], padding="max_length", truncation=True, max_length=self.max_length)

    def train_model(self):
        """Train the RoBERTa model."""
        num_labels = self.dataset.features["class"].num_classes
        self.model = RobertaForSequenceClassification.from_pretrained(self.model_name, num_labels=num_labels)
        self.model.to(self.device)

        training_args = TrainingArguments(
            output_dir="./results",
            evaluation_strategy="epoch",
            learning_rate=2e-5,
            per_device_train_batch_size=8,
            per_device_eval_batch_size=8,
            num_train_epochs=3,
            weight_decay=0.01,
        )

        accuracy_metric = load("accuracy")
        precision_metric = load("precision")
        f1_metric = load("f1")

        def compute_metrics(pred):
            labels = pred.label_ids
            preds = pred.predictions.argmax(-1)
            accuracy = accuracy_metric.compute(predictions=preds, references=labels)["accuracy"]
            precision = precision_metric.compute(predictions=preds, references=labels, average="weighted")["precision"]
            f1 = f1_metric.compute(predictions=preds, references=labels, average="weighted")["f1"]
            return {
                "accuracy": accuracy,
                "precision": precision,
                "f1": f1
            }

        self.trainer = Trainer(
            model=self.model,
            args=training_args,
            train_dataset=self.train_dataset,
            eval_dataset=self.val_dataset,
            compute_metrics=compute_metrics,
        )

        self.trainer.train()

    def evaluate_model(self):
        """Evaluate the trained model on the test dataset."""
        test_results = self.trainer.evaluate(self.test_dataset)
        print("Test Set Results:")
        print(f"Accuracy: {test_results['eval_accuracy']:.4f}")
        print(f"Precision: {test_results['eval_precision']:.4f}")
        print(f"F1 Score: {test_results['eval_f1']:.4f}")

    def classify_tasks(self, tasks):
        """Classify tasks using the trained RoBERTa model."""
        inputs = self.tokenizer(tasks, padding=True, truncation=True, max_length=self.max_length, return_tensors="pt")
        inputs = {key: value.to(self.device) for key, value in inputs.items()}

        self.model.eval()  
        with torch.no_grad():
            outputs = self.model(**inputs)
            predictions = torch.argmax(outputs.logits, dim=-1)

        class_labels = self.dataset.features["class"].names
        predicted_labels = [class_labels[pred] for pred in predictions]

        return predicted_labels

    def save_model(self, filename):
        """Save the trained model to a file."""
        import pickle
        with open(filename, 'wb') as f:
            pickle.dump(self.model, f)
        print(f"Model saved to {filename}")

    def load_model(self, filename):
        """Load a trained model from a file."""
        import pickle
        with open(filename, 'rb') as f:
            self.model = pickle.load(f)
        self.model.to(self.device)
        print(f"Model loaded from {filename}")