import os
from dotenv import load_dotenv
import cohere
import time
import spacy
from spacy.training import Example
from spacy.util import minibatch
import random
import re
import ast
import nltk
import json
nltk.download('punkt_tab')
from nltk.tokenize import sent_tokenize

def get_cohere_api_key():
    """
    Retrieves the Cohere API key from an environment variable.
    """
    start_time = time.time()
    api_key = os.getenv('COHERE_API_KEY')
    if not api_key:
        raise EnvironmentError("COHERE_API_KEY environment variable not set.")
    end_time = time.time()
    print('Get api key: ', end_time-start_time)
    return api_key

# # Tokenize text into sentences
# def tokenize_sentences(text):
#     return sent_tokenize(text)

def tokenize_sentences(text):
    nlp = spacy.load("en_core_web_sm")  # Load SpaCy model
    doc = nlp(text)
    return [sent.text.strip() for sent in doc.sents]

def process_syllabus(file_path):
    """
    Reads the syllabus text from the given file path.
    """
    start_time = time.time()
    with open(file_path, 'r') as file:
        syllabus_text = file.read()
    end_time = time.time()
    # print('Process syllabus time: ', end_time-start_time)
    return syllabus_text
def extract_info(tokenized_sentences, cohere_client):
    """
    Classifies each token (sentence) as Relevant or Irrelevant using Cohere API.
    """
    start_time = time.time()
    relevant_tokens = []

    # Process each token (sentence) individually
    for sentence in tokenized_sentences:
        prompt = f"""
        Classify the following token (sentence) as either "Relevant" or "Irrelevant" based on the following criteria:

        1. **Relevant Tokens**:
           - Tokens describing tasks contributing to the course grade, such as deliverables, assignments, projects, exams, presentations or any other graded components which ensure a grade in the course. 
           These tasks should have specific goals, deadlines, deliverables, or evaluation criteria. Extract all the information provided about that task along with 
           its description, task percentage, deadline for the task and the deliverables. 

        2. **Irrelevant Tokens**:
           - Tokens discussing general course engagement, preparation, or participation, such as reading materials, communication guidelines, or preparatory activities without direct grading.

        **Token**:
        "{sentence}"

        Provide the output in following format:
        <Relevant/Irrelevant>
        ...
        Ensure each token is followed by its classification.

        examples:
        **Token**: "Course Policies\nGrades:\nMidterm 1 (including report to partner): 20%\nMidterm 2 (including report to partner): 20%\nPoster session: 10%\nFinal Presentation: 30%\nFinal Report: 10%\nPeer Assessment: 10%", Relevant
        **Token**: "Peer Assessment\n10% of the grade for each milestone will be self and peer evaluation.", Relevant
        
       
        """

        # Call Cohere API to classify the sentence
        response = cohere_client.generate(
            model='command-xlarge-nightly',
            prompt=prompt,
            max_tokens=50,
            temperature=0.3
        )

        # Extract the classification result
        classification = response.generations[0].text.strip()
        relevant_tokens.append((sentence, classification))
        # print(sentence, classification)
    end_time = time.time()
    print("Extract_info time: ", end_time - start_time)
    
    # Return classified tokens
    return relevant_tokens

# def extract_info(document_text, cohere_client):
#     start_time = time.time()
#     prompt = f"""
#     Extract all the headings from the provided document and classify each as either "Relevant" or "Irrelevant" based on the following criteria:

# 1. **Relevant Headings**:
#    - Include any heading where the paragraphs describe tasks that contribute to the course grade, such as deliverables, assignments, projects, exams, or other graded components. These tasks should have specific goals, deadlines, or deliverables, and may include milestones or evaluation criteria.

# 2. **Irrelevant Headings**:
#    - Include any heading where the paragraphs discuss general course engagement, preparation, or participation, such as reading materials, communication guidelines, or preparatory activities without direct grading.

# The output should be formatted as a list where each heading is labeled as "Relevant" or "Irrelevant," like so:
# 1. <Heading>: <Relevant/Irrelevant>
# 2. <Heading>: <Relevant/Irrelevant>
# 3. <Heading>: <Relevant/Irrelevant>

# **Example Input**:
# - "Course Information" contains details about general course logistics but no graded components. Classify as: "Irrelevant."
# - "Examinations" details graded exams and their weights in the final grade. Classify as: "Relevant."
# - "Project Information" describes a graded project with milestones. Classify as: "Relevant."

# **Example Output**:
# 1. Course Information: Irrelevant
# 2. Examination: Relevant
# 3. Project Information: Relevant

# **Document**:
# {document_text}


# """
#     # Call the Cohere API to generate text
#     response = cohere_client.generate(
#         model='command-xlarge-nightly',  
#         prompt=prompt,
#         max_tokens=2000,
#         temperature=0.3
#     )
#     end_time = time.time()
#     print("Extract_info time: ", end_time-start_time)
#     # Extract and return the generated response text
#     return response.generations[0].text
def cohere_to_spacy_format_v2(classified_segments, training_data):
    """
    Converts the list of classified segments (sentence, label) to SpaCy training format.
    """
    for segment, label in classified_segments:
        # Ensure label is uppercase and SpaCy-compatible
        label = "RELEVANT" if label.lower() == "relevant" else "IRRELEVANT"
        
        # Append to training data with entity covering the whole segment
        training_data.append((segment, {"entities": [(0, len(segment), label)]}))
    
    return training_data

def save_extraction_results(results, output_file):
    """
    Save extracted results to a JSON file for backup or later use.
    """
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=4)

def process_all_files(input_folder, output_folder, cohere_client):
    # Process each file in the input folder
    for filename in os.listdir(input_folder):
            json_filename = f"{os.path.splitext(filename)[0]}.json"
            json_filepath = os.path.join(output_folder, json_filename)
            if os.path.exists(json_filepath):
                print(f"Skipping {filename}, training data already exists: {json_filename}")
                continue
            print('Starting to process: ', filename)
            result_file_path = os.path.join(output_folder, f"{os.path.splitext(filename)[0]}_results.txt")
            input_filepath = os.path.join(input_folder, filename)
            document_text = process_syllabus(input_filepath)
            text = tokenize_sentences(document_text)
            output_text = extract_info(text, cohere_client)
            # Save individual results to output folder (optional for audit)
            training_data = []
            training_data = cohere_to_spacy_format_v2(output_text, training_data)
            with open(json_filepath, 'w') as json_file:
                json.dump(training_data, json_file, indent=4)
            with open(result_file_path, 'w') as result_file:
                output_text_str = "\n".join([f"{token}: {label}" for token, label in output_text])
                result_file.write(output_text_str)

            print(f"Processed {filename} and saved training data to {json_filename}.")

    print("All files processed.")
    return training_data

def deduplicate_training_data(training_data):
    """
    Deduplicates the training data while preserving order.
    """
    seen = set()
    unique_data = []
    for text, annotations in training_data:
        # Create a unique identifier (hashable) for deduplication
        # text = clean_text(text)
        identifier = (text, tuple(annotations["entities"]))
        if identifier not in seen:
            seen.add(identifier)
            unique_data.append((text, annotations))
    return unique_data

def train_ner_model(training_data, output_model_path, epochs=10):
    """
    Trains an NER model, continuing from a previously saved model if available.
    """
    # Check if an existing model is available
    # if os.path.exists(output_model_path):
    #     print(f"Loading existing model from {output_model_path}")
    #     nlp = spacy.load(output_model_path)
    # else:
    print("No existing model found. Starting with 'en_core_web_sm'.")
    nlp = spacy.load("en_core_web_sm")

    # Get the NER pipeline
    ner = nlp.get_pipe("ner")
    
    # Add new labels if not already present
    ner.add_label("RELEVANT")
    ner.add_label("IRRELEVANT")
    
    # Deduplicate training data
    unique_data = deduplicate_training_data(training_data)
    examples = []
    for text, annotations in unique_data:
        doc = nlp.make_doc(text)
        example = Example.from_dict(doc, annotations)
        examples.append(example)

    # Resume training or initialize optimizer
    optimizer = nlp.resume_training() if hasattr(nlp, "resume_training") else nlp.create_optimizer()

    # Training loop
    for epoch in range(epochs):
        random.shuffle(examples)
        losses = {}
        batches = minibatch(examples, size=8)
        for batch in batches:
            nlp.update(batch, sgd=optimizer, drop=0.3, losses=losses)
        print(f"Epoch {epoch + 1}, Losses: {losses}")
    
    # Save the updated model
    nlp.to_disk(output_model_path)
    print(f"Model saved to {output_model_path}")

if __name__ == "__main__":
    start_time = time.time()
    # Get API key securely from environment variables
    load_dotenv()
    api_key = get_cohere_api_key()
    cohere_client = cohere.Client(api_key)

    # Get user input for folder paths
    input_folder = input("Enter the path to the folder with syllabus files: ")
    output_folder = input("Enter the path to the output folder for results: ")

    # Create output folder if it does not exist
    os.makedirs(output_folder, exist_ok=True)
    training_data = process_all_files(input_folder, output_folder, cohere_client)
    # print(training_data)
    # Train the model
    output_model_path = r"C:\Users\earns\OneDrive\Desktop\uoft\ECE496-project\taskExtraction\Ner"
    os.makedirs(output_model_path, exist_ok=True)
    # *****************************TESTING************************8
#     with open(r"C:\Users\earns\OneDrive\Desktop\uoft\ECE496-project\taskExtraction\train_data.txt", "r") as f:
#         file_content = f.read()  # Read the entire content of the file

# # Convert the string into a Python list
#     training_data = ast.literal_eval(file_content)  # Safely parse the string into a Python object

    # Verify the structure
    # unique_data = deduplicate_training_data(training_data)
    # print(training_data)
    # with open(r"C:\Users\earns\OneDrive\Desktop\uoft\ECE496-project\taskExtraction\train_data.txt", 'w') as file:
    #     file.write(str(unique_data))
    # *****************************TESTING************************8
    
    train_ner_model(training_data, output_model_path, 30)
    
    # Test the model
    nlp = spacy.load(output_model_path)
    doc = nlp("Group Project and Required Subtasks")
    print("Entities:")
    for ent in doc.ents:
        print(f"Text: {ent.text}, Label: {ent.label_}")
    
    end_time = time.time()
    print('Training and testing took: ', end_time - start_time)