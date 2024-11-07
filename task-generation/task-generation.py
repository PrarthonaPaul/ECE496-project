import torch
from transformers import pipeline

device = 0 if torch.cuda.is_available() else -1

classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli", device=device, clean_up_tokenization_spaces=True)

file_path = "/Users/prarthonapaul/Documents/capstone/ECE496-project/task-generation/ART322.txt"
text_content = None

with open(file_path, 'r') as file:
    text_content = file.read()

labels = ["deliverable", "due date", "worth"]
# results = classifier(text_content, candidate_labels=labels)

# # Print the results
# for label, score in zip(results["labels"], results["scores"]):
#     print(f"{label}: {score:.4f}")

for sentence in text_content:
    results = classifier(sentence, candidate_labels=labels)
    print(f"Text: {sentence}")
    for label, score in zip(results["labels"], results["scores"]):
        print(f"  {label}: {score:.4f}")

