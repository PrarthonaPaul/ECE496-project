import spacy
from spacy.lookups import Lookups
from spacy.util import minibatch, compounding
from spacy.training import Example, offsets_to_biluo_tags
import re

TRAIN_DATA = [
    {
        "text": "March 15, 2020 Team Formation. 10%",
        "entities": [
            [0, 14, "DATE"],
            [15, 29, "DELIVERABLE"],
            [31, 33, "WEIGHT"]
        ]
    },
    {
        "text": "October 20, 2020 Preliminary Design Review. 15%",
        "entities": [
            [0, 16, "DATE"],
            [17, 42, "DELIVERABLE"],
            [44, 46, "WEIGHT"]
        ]
    }, 
    {
        "text": "November 25, 2020 Prototype Development and Testing. 20%",
        "entities": [
            [0, 17, "DATE"],
            [18, 51, "DELIVERABLE"],
            [53, 55, "WEIGHT"]
        ]
    }, 
    {
        "text": "Progress Reports. 20% due January 25, 2022.",
        "entities": [
            [0, 16, "DELIVERABLE"],
            [18, 20, "WEIGHT"],
            [26, 42, "DATE"]
        ]
    }, 
    {
        "text": "Final Project Report, 30%, December 8, 2022.",
        "entities": [
            [0, 20, "DELIVERABLE"],
            [22, 25, "WEIGHT"],
            [27, 43, "DATE"]
        ]
    }, 
    {
        "text": "June 15, 2024 Assignment 1. 15%",
        "entities": [
            [0, 13, "DATE"],
            [14, 26, "DELIVERABLE"],
            [38, 40, "WEIGHT"]
        ]
    },
    {
        "text": "Sept 23, 2022 Final presentation. 5%",
        "entities": [
            [0, 13, "DATE"],
            [14, 32, "DELIVERABLE"],
            [34, 35, "WEIGHT"]
        ]
    },
    {
        "text": "Sept 09, 2025 Milestone 6. 12%",
        "entities": [
            [0, 13, "DATE"],
            [14, 25, "DELIVERABLE"],
            [27, 30, "WEIGHT"]
        ]
    },
    {
        "text": "July 23, 2022 Milestone 2. 5%",
        "entities": [
            [0, 13, "DATE"],
            [14, 25, "DELIVERABLE"],
            [27, 29, "WEIGHT"]
        ]
    },
    {
        "text": "March 16, 2023 Proposal document. 20%",
        "entities": [
            [0, 14, "DATE"],
            [15, 32, "DELIVERABLE"],
            [34, 36, "WEIGHT"]
        ]
    },
    {
        "text": "Midterm Presentation and Design Progress Demonstration 20% November 8, 2025.", 
        "entities": [
            [0, 54, "DELIVERABLE"],
            [55, 58, "WEIGHT"],
            [59, 75, "DATE"]
        ]
    },
    {
        "text": "This is a random text",
        "entities": []
    }, 
    {
        "text": "The course deliverables are as follows:",
        "entities": []
    },
    {
        "text": "May 5, 2021 Literature Review. 15%",
        "entities": [
            [0, 11, "DATE"],
            [12, 29, "DELIVERABLE"],
            [31, 33, "WEIGHT"]
        ]
    },
    {
        "text": "June 30, 2021 Data Collection. 20%",
        "entities": [
            [0, 13, "DATE"],
            [14, 29, "DELIVERABLE"],
            [31, 33, "WEIGHT"]
        ]
    },
    {
        "text": "July 15, 2021 Analysis Report. 25%",
        "entities": [
            [0, 13, "DATE"],
            [14, 29, "DELIVERABLE"],
            [31, 33, "WEIGHT"]
        ]
    },
    {
        "text": "August 20, 2021 Final Presentation. 30%",
        "entities": [
            [0, 15, "DATE"],
            [16, 34, "DELIVERABLE"],
            [36, 38, "WEIGHT"]
        ]
    },
    {
        "text": "September 10, 2021 Peer Review. 5%",
        "entities": [
            [0, 18, "DATE"],
            [19, 30, "DELIVERABLE"],
            [31, 32, "WEIGHT"]
        ]
    },
    {
        "text": "October 5, 2021 Project Submission. 10%",
        "entities": [
            [0, 15, "DATE"],
            [16, 34, "DELIVERABLE"],
            [36, 38, "WEIGHT"]
        ]
    },
    {
        "text": "April 10, 2021 Initial Research. 10%",
        "entities": [
            [0, 14, "DATE"],
            [15, 31, "DELIVERABLE"],
            [33, 35, "WEIGHT"]
        ]
    }
]


# Load the base model
# nlp = spacy.load("en_core_web_sm")  
nlp = spacy.blank("en")
# lookups = Lookups()
# lookups.add_table("lexeme_norm", {"example": "example_normalized"})
# nlp.vocab.lookups.add_table("lexeme_norm", lookups.get_table("lexeme_norm"))
ner = nlp.add_pipe("ner")

# Add the labels (entities) you want to train
ner.add_label("DELIVERABLE")
ner.add_label("DATE")
ner.add_label("WEIGHT")

def check_alignment(train_data):
    for example in train_data:
        text = example["text"]
        entities = example["entities"]
        doc = nlp.make_doc(text)
        biluo_tags = offsets_to_biluo_tags(doc, entities)
        
        # If there are misaligned entities, biluo_tags will contain "-"
        if "-" in biluo_tags:
            print(f"Misalignment found in text: '{text}'")
            print(f"Entities: {entities}")
            print(f"BILUO Tags: {biluo_tags}")
            print("---------")

check_alignment(TRAIN_DATA)

# Training loop
optimizer = nlp.begin_training()
for i in range(1000):
    losses = {}
    batches = minibatch(TRAIN_DATA, size=compounding(4.0, 32.0, 1.001))
    # random.shuffle(TRAIN_DATA)

    # for text, annotations in TRAIN_DATA:
    #     example = Example.from_dict(nlp.make_doc(text), annotations)
    #     nlp.update([example], drop=0.5, losses=losses)
    # print(losses)
    

    for batch in batches:
        texts = [item["text"] for item in batch]
        annotations = [{"entities": item["entities"]} for item in batch]
        examples = []
        for text, annot in zip(texts, annotations):
            doc = nlp.make_doc(text)
            example = Example.from_dict(doc, annot)
            examples.append(example)

        # Update the model
        nlp.update(examples, drop=0.5, sgd=optimizer, losses=losses)


# Save the trained model
nlp.to_disk("./course_ner_model")

# Load the trained model
nlp = spacy.load("./course_ner_model")

# Test the model
# file = open('./train-data/MECH490.txt', 'r')
# lines = file.readlines()

lines = []
lines.append("Site Analysis Report: due September 15, 2022, weight 10%")
lines.append("March 16, 2023 Proposal document. 20%")
lines.append("This is a random text")

for line in lines:
    doc = nlp(line)
    for ent in doc.ents:
        if ent.label == 'WEIGHT' and not bool(re.search(r'\d', ent.text)):
            continue
        if ent.label == 'DATE' and not bool(re.search(r'\d', ent.text)):
            continue
        print(ent.text, ent.label_)
