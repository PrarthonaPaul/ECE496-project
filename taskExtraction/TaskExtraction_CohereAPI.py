import os
from dotenv import load_dotenv
import cohere


def get_cohere_api_key():
    """
    Retrieves the Cohere API key from an environment variable.
    """
    api_key = os.getenv("COHERE_API_KEY")
    if not api_key:
        raise EnvironmentError("COHERE_API_KEY environment variable not set.")
    return api_key


def process_syllabus(file_path):
    """
    Reads the syllabus text from the given file path.
    """
    with open(file_path, "r") as file:
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
        model="command-xlarge-nightly", prompt=prompt, max_tokens=1500, temperature=0.7
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
        input_filepath = os.path.join(input_folder, filename)
        document_text = process_syllabus(input_filepath)

        output_text = extract_info(document_text, cohere_client)

        # Write the extracted information to an output file
        output_filepath = os.path.join(
            output_folder, f"{os.path.splitext(filename)[0]}_results.txt"
        )
        with open(output_filepath, "w") as result_file:
            result_file.write(output_text)

        print(f"Processed {filename} and saved output to {output_filepath}")


if __name__ == "__main__":
    main()
