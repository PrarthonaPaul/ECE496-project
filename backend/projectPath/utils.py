import os
import cohere
from collections import defaultdict
from dotenv import load_dotenv
import fitz  # PyMuPDF

def pdf_to_text(pdf_path):
    try:
        # Open the PDF document
        doc = fitz.open(pdf_path)
        text = ''
        for page in doc:
            text += page.get_text()
        return text
    except Exception as e:
        print(f"Error processing file {pdf_path}: {e}")
        return None

def write_files(input_dir, output_path):
    # Check if the input directory exists
    if not os.path.isdir(input_dir):
        print(f"Input directory '{input_dir}' does not exist.")
        return
    
    # Ensure the output directory exists
    os.makedirs(output_path, exist_ok=True)

    for file in os.listdir(input_dir):
        input_file = os.path.join(input_dir, file)
        if os.path.isdir(input_file):
            print(f"skipping directory: {format(input_file)}")
            continue  # Skip directories

        pdf_text = pdf_to_text(input_file)
        if pdf_text is None:
            continue  # Skip if the PDF could not be read

        output_file = os.path.join(output_path, f"{os.path.splitext(file)[0]}.txt")
        with open(output_file, 'w') as f:
            f.write(pdf_text)

def get_cohere_api_key():
    """
    Retrieves the Cohere API key from an environment variable.
    """
    api_key = os.getenv('COHERE_API_KEY')
    if not api_key:
        raise EnvironmentError("COHERE_API_KEY environment variable not set.")
    return api_key


def process_syllabus(file_path):
    """
    Reads the syllabus text from the given file path.
    """
    with open(file_path, 'r') as file:
        syllabus_text = file.read()
    return syllabus_text

def extract_info(document_text, cohere_client):
    """
    Extracts tasks, task percentages, descriptions, and deadlines from the provided document text.
    """
    prompt = f"""
    Extract all tasks, task percentages, descriptions, and deadlines from the following document. 
    If any information (like description or deadline or task percentage) is missing, 
    write 'N/A' in that cell. Also, include any milestones or deliverables that are part of each task.

    Document: 
    {document_text}

    Format the output as follows:
    | Task | Task Percentage | Description | Deadline |
    | --- | --- | --- | --- |
    | <Task Name> | <Task Percentage> | <Description> | <Deadline> |
    """
    # Call the Cohere API to generate text
    response = cohere_client.generate(
        model='command-xlarge-nightly',  
        prompt=prompt,
        max_tokens=1500,
        temperature=0.7
    )

    # Extract and return the generated response text
    return response.generations[0].text

def extract_tasks(input_folder, output_folder, input_filename):
    # Get API key securely from environment variables
    load_dotenv()
    api_key = get_cohere_api_key()
    cohere_client = cohere.Client(api_key)

    # Create output folder if it does not exist
    os.makedirs(output_folder, exist_ok=True)

    # Process each file in the input folder
    for filename in os.listdir(input_folder):
        if filename != input_filename: 
            continue

        input_filepath = os.path.join(input_folder, filename)
        document_text = process_syllabus(input_filepath)
        
        output_text = extract_info(document_text, cohere_client)
        
        # Write the extracted information to an output file
        output_filepath = os.path.join(output_folder, f"{os.path.splitext(filename)[0]}_results.txt")
        with open(output_filepath, 'w') as result_file:
            result_file.write(output_text)
        
        print(f"Processed {filename} and saved output to {output_filepath}")