import os
from dotenv import load_dotenv
import cohere

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
        model='command-xlarge-nightly',  
        prompt=prompt,
        max_tokens=2000,
        temperature=0.3
    )

    # Extract and return the generated response text
    return response.generations[0].text

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
    for filename in os.listdir(input_folder):
        if not os.path.exists(os.path.join(output_folder, f"{os.path.splitext(filename)[0]}_results.txt")):
            input_filepath = os.path.join(input_folder, filename)
            document_text = process_syllabus(input_filepath)
            
            output_text = extract_info(document_text, cohere_client)
            
            # Write the extracted information to an output file
            output_filepath = os.path.join(output_folder, f"{os.path.splitext(filename)[0]}_results.txt")
            with open(output_filepath, 'w') as result_file:
                result_file.write(output_text)
            
            print(f"Processed {filename} and saved output to {output_filepath}")

if __name__ == "__main__":
    main()
