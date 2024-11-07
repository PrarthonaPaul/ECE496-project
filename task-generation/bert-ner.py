from transformers import AutoTokenizer, AutoModelForTokenClassification
from transformers import pipeline
import re

# Load the BERT-based NER model
tokenizer = AutoTokenizer.from_pretrained("dslim/bert-base-NER")
model = AutoModelForTokenClassification.from_pretrained("dslim/bert-base-NER")

# Initialize the NER pipeline
nlp = pipeline("ner", model=model, tokenizer=tokenizer)

# Example sentence
example = "Site Analysis Report: due September 15th, 2022, weight 10%"

# Apply NER to the example sentence
ner_results = nlp(example)

# Print NER results (for debugging)
print("NER Results:", ner_results)

# Initialize variables to store extracted data
deliverable_name = ""
due_date = ""
weight = ""

# Regex patterns for due date and weight extraction
date_pattern = r"\b(?:[A-Z][a-z]+\s\d{1,2},\s\d{4})\b"  # Matches dates like "September 15, 2022"
weight_pattern = r"\b\d{1,3}%\b"  # Matches percentages like "10%"

# Extract deliverable name based on NER tags
for entity in ner_results:
    if entity['entity'] == 'B-ORG' or entity['entity'] == 'I-ORG':  # Assuming deliverable names are tagged as organizations
        deliverable_name += entity['word'] + " "

# Clean up the deliverable name
deliverable_name = deliverable_name.strip()

# Extract due date using regex
due_date_match = re.search(date_pattern, example)
if due_date_match:
    due_date = due_date_match.group(0)

# Extract weight using regex
weight_match = re.search(weight_pattern, example)
if weight_match:
    weight = weight_match.group(0)

# Print extracted information
print(f"Deliverable: {deliverable_name}")
print(f"Due Date: {due_date}")
print(f"Weight: {weight}")
