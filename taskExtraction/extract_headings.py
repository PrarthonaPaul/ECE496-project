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

def extract_info(document_text, cohere_client):
    start_time = time.time()
    prompt = f"""
    Extract all the headings from the provided document and classify each as either "Relevant" or "Irrelevant" based on the following criteria:

1. **Relevant Headings**:
   - Include any heading where the paragraphs describe tasks that contribute to the course grade, such as deliverables, assignments, projects, exams, or other graded components. These tasks should have specific goals, deadlines, or deliverables, and may include milestones or evaluation criteria.

2. **Irrelevant Headings**:
   - Include any heading where the paragraphs discuss general course engagement, preparation, or participation, such as reading materials, communication guidelines, or preparatory activities without direct grading.

The output should be formatted as a list where each heading is labeled as "Relevant" or "Irrelevant," like so:
1. <Heading>: <Relevant/Irrelevant>
2. <Heading>: <Relevant/Irrelevant>
3. <Heading>: <Relevant/Irrelevant>

**Example Input**:
- "Course Information" contains details about general course logistics but no graded components. Classify as: "Irrelevant."
- "Examinations" details graded exams and their weights in the final grade. Classify as: "Relevant."
- "Project Information" describes a graded project with milestones. Classify as: "Relevant."

**Example Output**:
1. Course Information: Irrelevant
2. Examination: Relevant
3. Project Information: Relevant

**Document**:
{document_text}


"""
    # Call the Cohere API to generate text
    response = cohere_client.generate(
        model='command-xlarge-nightly',  
        prompt=prompt,
        max_tokens=2000,
        temperature=0.3
    )
    end_time = time.time()
    print("Extract_info time: ", end_time-start_time)
    # Extract and return the generated response text
    return response.generations[0].text
def cohere_to_spacy_format(cohere_output, training_data):
    for line in cohere_output.strip().split("\n"):
        if ":" in line:
            heading, label = map(str.strip, line.split(":", 1))
            # print('Heading:', heading)
            # print('label: ', label)
            label = "RELEVANT" if label == "Relevant" else "IRRELEVANT"
            # if label == "RELEVANT":
            training_data.append((heading, {"entities": [(0, len(heading), label)]}))
    return training_data
def main():
    # Get API key securely from environment variables
    load_dotenv()
    api_key = get_cohere_api_key()
    cohere_client = cohere.Client(api_key)

    # Get user input for folder paths
    input_folder = input("Enter the path to the folder with syllabus files: ")
    output_folder = input("Enter the path to the output folder for results: ")

    # Create output folder if it does not exist
    os.makedirs(output_folder, exist_ok=True)

    # Process each file in the input folder
    # for filename in os.listdir(input_folder):
    #     if not os.path.exists(os.path.join(output_folder, f"{os.path.splitext(filename)[0]}_results.txt")):
    #         input_filepath = os.path.join(input_folder, filename)
    #         document_text = process_syllabus(input_filepath)
            
    #         output_text = extract_info(document_text, cohere_client)
            
    #         # Write the extracted information to an output file
    #         output_filepath = os.path.join(output_folder, f"{os.path.splitext(filename)[0]}_results.txt")
    #         with open(output_filepath, 'w') as result_file:
    #             result_file.write(output_text)
            
    #         print(f"Processed {filename} and saved output to {output_filepath}")
    training_data = []
    for output_heading in os.listdir(output_folder):
        out_filepath = os.path.join(output_folder, output_heading)
        heading_labelled = process_syllabus(out_filepath)
        training_data = cohere_to_spacy_format(heading_labelled, training_data)
    return training_data

# def clean_text(text):
#     return re.sub(r'^\d+\.\s*', '', text)

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

# Deduplicate training data


def train_ner_model(training_data, output_model_path, epochs=10):
    # Load a pre-trained model
    nlp = spacy.load("en_core_web_sm")
    ner = nlp.get_pipe("ner")
    
    ner.add_label("RELEVANT")
    ner.add_label("IRRELEVANT")
    
    unique_data = deduplicate_training_data(training_data)
    examples = []
    for text, annotations in unique_data:
        doc = nlp.make_doc(text)  # Create a doc from the text
        example = Example.from_dict(doc, annotations)  # Create an Example
        examples.append(example)  # Append to the list of examples
    optimizer = nlp.resume_training()

# Training loop
    epochs = 10
    for epoch in range(epochs):
        random.shuffle(examples)  # Shuffle training examples for each epoch
        losses = {}  # Reset losses for the epoch
        # Create mini-batches
        batches = minibatch(examples, size=8)
        # Update model with each batch
        for batch in batches:
            nlp.update(batch, sgd=optimizer, drop=0.3, losses=losses)
        # Print loss after each epoch
        print(f"Epoch {epoch + 1}, Losses: {losses}")
    # Save the trained model
    nlp.to_disk(output_model_path)
    print(f"Model saved to {output_model_path}")

if __name__ == "__main__":
    start_time = time.time()
    training_data = main()
    print(training_data)
    # Train the model
    output_model_path = r"C:\Users\earns\OneDrive\Desktop\uoft\ECE496-project\taskExtraction"
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
    
    train_ner_model(training_data, output_model_path)
    
    # Test the model
    nlp = spacy.load(output_model_path)
    doc = nlp("Group Project and Required Subtasks")
    print("Entities:")
    for ent in doc.ents:
        print(f"Text: {ent.text}, Label: {ent.label_}")
    
    end_time = time.time()
    print('Training and testing took: ', end_time - start_time)