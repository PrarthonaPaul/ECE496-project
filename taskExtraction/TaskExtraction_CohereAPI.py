import os
from dotenv import load_dotenv
import cohere
import time
import spacy
import tiktoken

def filter_relevant_text(document_text):
    """
    Filters the document text using a pre-trained NER model and extracts relevant sections.
    """
    start_time = time.time()
    # Load SpaCy's NER model
    nlp = spacy.load(r"C:\Users\earns\OneDrive\Desktop\uoft\ECE496-project\taskExtraction\Ner")

    # Process the document text
    doc = nlp(document_text)

    # Collect relevant sentences (modify based on your needs)
    relevant_text = []
    with open('analysis.txt', 'a') as file:  # Open in append mode
        for ent in doc.ents:
            file.write(f"Text: {ent.text}, Label: {ent.label_}\n")  # Log every entity to the file
            if ent.label_ == "RELEVANT":  # Replace with your custom entity label if using a custom NER model
                relevant_text.append(ent.sent.text)  # Add the sentence containing the relevant entity

    # Join relevant sentences into a single string
    end_time = time.time()
    print('Filter relevant text: ', end_time-start_time)
    return " ".join(relevant_text)

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
    print('Process syllabus time: ', end_time-start_time)
    return syllabus_text
extraction_time = 0
def extract_info(document_text, cohere_client):
    """
    Extracts tasks, task percentages, descriptions, and deadlines from the provided document text.
    """
    # prompt = f"""
    # Extract all tasks, their percentages, descriptions, deadlines, milestones, and deliverables from the following document.

    # 1. Look for tasks explicitly mentioned in bullet points, tables, and paragraphs.
    # 2. For each task, ensure that you capture any related context or details mentioned, including milestones or deliverables associated with the task.
    # 3. If any information (like description, deadline, task percentage, milestones, or deliverables) is missing, write 'N/A' in that cell.
    # 4. If its a team project seperate the individual and team related tasks, i.e add Individual or Group in the Task Type column.
    
    # Format the output as follows:

    # Document: 
    # {document_text}

    # Format the output as follows:
    # | Task Type | Task | Task Percentage | Description | Deadline |
    # | --- | --- | --- | --- | --- |
    # | <Task Type> | <Task Name> | <Task Percentage> | <Description> | <Deadline> |
    # """
#     prompt = f"""
# Extract all tasks and their related details from the following document in a single pass, ensuring all available information is captured. 

# Please list each task with the following format:

# | Task Type | Task | Task Percentage | Description | Deadline | Milestone/Deliverable |
# | --- | --- | --- | --- | --- | --- |

# Instructions:
# 1. Identify each task only once, including details on individual tasks and team-based tasks if available.
# 2. Ensure 'N/A' is filled for any missing information so that no cell is left blank.
# 3. Specify if the task is for an 'Individual' or a 'Group' under 'Task Type'.
# 4. Capture all contextual information related to tasks, such as milestones or deliverables, and avoid listing repetitive entries.

# Document:
# {document_text}

#     """
    start_time = time.time()
    # relevant_text = filter_relevant_text(document_text)
    # print(relevant_text)
    # if not relevant_text.strip():
    #     return "No relevant information found."
    prompt = f"""
Extract tasks from the following document and classify them as either "Core" or "Support." Use the following criteria:

1. **Core Tasks**:
   - Core tasks include any deliverables, assignments, projects, exams, or graded components. These tasks should have specific goals, deadlines, and descriptions, and may include milestones or deliverables.
   
2. **Support Tasks**:
   - Support tasks are related to general course engagement, preparation, or participation, such as reading materials, using forums, or following communication guidelines. These are ongoing or preparatory activities without direct grading.

Format the output as follows:

| Task Type | Task | Task Percentage | Description | Deadline | Milestone/Deliverable |
| --- | --- | --- | --- | --- | --- |
| Core | <Core Task Name> | <Task Percentage> | <Description> | <Deadline> | <Milestone/Deliverable> |
| Support | <Support Task Name> | N/A | <Description> | N/A | N/A |

Document:
{document_text}

Make sure to:
1. Label each row with "Core" or "Support" in the Task Type column.
2. Include 'N/A' for any missing information (like Task Percentage, Deadline, or Milestone/Deliverable).
3. Only extract specific tasks; avoid listing general instructions or tips.
"""
    # Call the Cohere API to generate text
    response = cohere_client.generate(
        model='command',  
        prompt=prompt,
        max_tokens=2000,
        temperature=0.3
    )
    end_time = time.time()
    extraction_time = end_time-start_time
    print("Extract_info time: ", end_time-start_time)
    # Extract and return the generated response text
    return response.generations[0].text, extraction_time


def overlap_chunk_text(text, max_chunk_size=3500, overlap_size=500):
    """
    Splits text into chunks based on token count with overlap.
    """
    # Get tokenizer for Cohere's model
    tokenizer = tiktoken.get_encoding("gpt2")  # Approximate tokenization

    tokens = tokenizer.encode(text)
    chunks = []
    start = 0
    
    while start < len(tokens):
        # Determine the end of the current chunk
        end = start + max_chunk_size
        
        # Create the chunk and append it to the list
        chunk_tokens = tokens[start:end]
        chunk_text = tokenizer.decode(chunk_tokens)
        chunks.append(chunk_text)
        
        start += (max_chunk_size - overlap_size)
    
    return chunks


def main():
    # Get API key securely from environment variables
    load_dotenv()
    string_len = '''Extract tasks from the following document and classify them as either "Core" or "Support." Use the following criteria:

1. **Core Tasks**:
   - Core tasks include any deliverables, assignments, projects, exams, or graded components. These tasks should have specific goals, deadlines, and descriptions, and may include milestones or deliverables.
   
2. **Support Tasks**:
   - Support tasks are related to general course engagement, preparation, or participation, such as reading materials, using forums, or following communication guidelines. These are ongoing or preparatory activities without direct grading.

Format the output as follows:

| Task Type | Task | Task Percentage | Description | Deadline | Milestone/Deliverable |
| --- | --- | --- | --- | --- | --- |
| Core | <Core Task Name> | <Task Percentage> | <Description> | <Deadline> | <Milestone/Deliverable> |
| Support | <Support Task Name> | N/A | <Description> | N/A | N/A |

Document:
{document_text}

Make sure to:
1. Label each row with "Core" or "Support" in the Task Type column.
2. Include 'N/A' for any missing information (like Task Percentage, Deadline, or Milestone/Deliverable).
3. Only extract specific tasks; avoid listing general instructions or tips.
'''
    print(len(string_len))
    api_key = get_cohere_api_key()
    cohere_client = cohere.Client(api_key)

    # Get user input for folder paths
    input_folder = input("Enter the path to the folder with syllabus files: ")
    output_folder = input("Enter the path to the output folder for results: ")

    # Create output folder if it does not exist
    os.makedirs(output_folder, exist_ok=True)

    # Process each file in the input folder
    for filename in os.listdir(input_folder):
        if not os.path.exists(os.path.join(output_folder, f"{os.path.splitext(filename)[0]}_results.txt")):
            input_filepath = os.path.join(input_folder, filename)
            document_text = process_syllabus(input_filepath)
            relevant_text = filter_relevant_text(document_text)
            with open('relevant.txt', 'w') as file:
                file.write(relevant_text)
            chunks = overlap_chunk_text(relevant_text)
            results = []
            for i, chunk in enumerate(chunks):
                # print('chunk len:', len(chunk))
                result, _ = extract_info(chunk, cohere_client)
                # print(f'RES {i}:', result)
                results.append(result)
            
            # Combine outputs from all chunks
            combined_output = "\n".join(results)
            output_filepath = os.path.join(output_folder, f"{os.path.splitext(filename)[0]}_results.txt")
            with open(output_filepath, 'w') as result_file:
                result_file.write(combined_output)
            
            print(f"Processed {filename} and saved output to {output_filepath}")

if __name__ == "__main__":
    start_time = time.time()
    main()
    end_time = time.time()
    print('Main function took: ', end_time-start_time)
