import os
import fitz  # PyMuPDF
import editdistance
from collections import defaultdict


def pdf_to_text(pdf_path):
    try:
        # Open the PDF document
        doc = fitz.open(pdf_path)
        text = ""
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
            continue  # Skip directories

        pdf_text = pdf_to_text(input_file)
        if pdf_text is None:
            continue  # Skip if the PDF could not be read

        output_file = os.path.join(output_path, f"{os.path.splitext(file)[0]}.txt")
        with open(output_file, "w") as f:
            f.write(pdf_text)


def main():
    # Request input directory and output directory from user
    input_dir = input("Enter the PDF directory path: ")
    output_path = input("Enter the output directory path: ")

    write_files(input_dir, output_path)


if __name__ == "__main__":
    main()
