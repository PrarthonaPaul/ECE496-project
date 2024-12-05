import os

# import cv2
# import matplotlib.pyplot as plt
# import numpy as np
# from PIL import Image as im
# from scipy.ndimage import interpolation as inter
# import skimage.filters as filters
# import pytesseract
import pdf2image
from pdf2image import convert_from_path
import editdistance
import pandas as pd
import time
from collections import defaultdict
import codecs
import re

# import fastwer
import tabulate
from tabulate import tabulate
import transformers

output = r"C:\Users\earns\OneDrive\Desktop\ECE496-project\pymupdf"
os.makedirs(output, exist_ok=True)
pdfs = r"C:\Users\earns\OneDrive\Desktop\ECE496-project\syllabus\tables\pdf"
# from transformers import AutoModelForCausalLM, AutoProcessor
import fitz


def pdf_to_text(pdf_path):
    doc = fitz.open(pdf_path)
    text = ""
    for page in doc:
        text += page.get_text()
    return text


# model = AutoModelForCausalLM.from_pretrained("microsoft/Florence-2-large-ft",
#                                              cache_dir=r"C:\Users\earns\OneDrive\Desktop\ECE496-project\my_models",
#                                             #  device_map="cuda",
#                                              trust_remote_code=True)


# processor = AutoProcessor.from_pretrained("microsoft/Florence-2-large-ft",
#  cache_dir=r"C:\Users\earns\OneDrive\Desktop\ECE496-project\my_models",
# #  device_map="cuda",
#  trust_remote_code=True)
def run_ocr(image):
    pages = convert_from_path(image, 350)
    i = 1
    for page in pages:
        image_name = "Page_" + str(i) + ".jpg"
        page.save(image_name, "JPEG")
        i = i + 1
    full_text = ""
    # full_text = florence(pages, full_text)
    return full_text


def write_files(dir):
    for file in os.listdir(dir):
        input_file = os.path.join(dir, file)
        if os.path.isdir(input_file):
            continue
        pdf = os.path.join(dir, file)
        text = pdf_to_text(pdf)
        output_file = os.path.join(output, f"{os.path.splitext(file)[0]}.txt")
        with open(output_file, "w") as f:
            f.write(text)


# def directory(dir, func, output):
#     for img in os.listdir(dir):
#         input_file = os.path.join(dir, img)
#         if os.path.isdir(input_file):
#             continue
#         img_name = img
#         img_thresh = cv2.imread(input_file)
#         cv2.imwrite(os.path.join(output, img_name), func(img_thresh))

# pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
write_files(pdfs)
# prompt = '<OCR_WITH_REGION>'

# def pymupdf(pages):
#     for i, page in enumerate(pages):

# def florence(pages, full_text):
#   total_time = 0
#   num_files = len(pages)

#   for i, page in enumerate(pages):
#       # img_path = os.path.join(folder, image_filename)
#       # print(img_path)
#       image = page.convert("RGB")

#       # image = Image.open(page).convert("RGB")
#       # Record the start time for this image
#       image_start_time = time.time()
#       inputs = processor(text=prompt, images=image, return_tensors="pt")
#       generated_ids = model.generate(
#             input_ids=inputs["input_ids"],
#             pixel_values=inputs["pixel_values"],
#             max_new_tokens=4096,
#             num_beams=3
#           )
#       generated_text = processor.batch_decode(generated_ids, skip_special_tokens=False)[0]
#       parsed_answer = processor.post_process_generation(generated_text, task=prompt, image_size=(image.width, image.height))


#       # output_file = os.path.join(output_dir, os.path.splitext(image_filename)[0] + ".txt")

#       # with open(output_file, "w", encoding="utf-8") as f:
#           # print(parsed_answer['<OCR>'])
#       string_list = parsed_answer['<OCR_WITH_REGION>']['labels']
#       written_text = ' '.join(string_list)
#       written_text = written_text.replace('</s>', ' ')
#       # print(written_text)
#       full_text += f"{written_text}\n"
#       # f.write(written_text)

#       image_end_time = time.time()
#       total_time += (image_end_time - image_start_time)


#   # Calculate the average time per image
#   average_time_per_image = total_time / num_files
#   return full_text
def bag_of_characters_error_rate(output_text, ref_text):
    output_freq = defaultdict(int)
    ref_freq = defaultdict(int)

    for char in output_text:
        output_freq[char] += 1

    for char in ref_text:
        ref_freq[char] += 1

    total_chars = sum(ref_freq.values())
    # print(output_freq, ref_freq)
    # print(set(output_text + ref_text))
    incorrect_chars = 0
    for char in set(output_text + ref_text):
        incorrect_chars += abs(output_freq[char] - ref_freq[char])

    cer = incorrect_chars / total_chars
    return cer * 100


def read_and_normalize(file_path):
    with codecs.open(file_path, "r", encoding="utf-8", errors="ignore") as file:
        lines = [normalize_text(line) for line in file.readlines() if line.strip()]
        return " ".join(lines)


def normalize_text(text):
    for char in text:
        if char == "\n":
            char = " "
    text = "".join(char for char in text if char.isalnum() or char.isspace())
    # text = text.replace(" ", "")
    return text.lower().strip()


def calculate_wer(output_text, ref_text):
    output_words = normalize_text(output_text).split()
    ref_words = normalize_text(ref_text).split()
    # Levenshtein distance (edit distance) for alignment
    distance = editdistance.eval(output_words, ref_words)

    # Compute WER
    wer = distance / len(ref_words) if len(ref_words) > 0 else 0.0
    return wer * 100


# def extract_number(filename):
#     print(filename)
#     match = re.match(r'(\d+)', filename)
#     if match:
#         return int(match.group(0))
#     return filename
def extract_number(filename):
    # Extract numbers from the filename
    numbers = re.findall(r"\d+", filename)
    return int(numbers[0]) if numbers else float("inf")


# ref_folder = r"C:\Users\earns\OneDrive\Desktop\ECE496-project\syllabus\tables\text_doc"
# output_folder = r"C:\Users\earns\OneDrive\Desktop\ECE496-project\tesseract_table"#"/content/drive/MyDrive/ncert_qs/easyocr_results"

# ref_files = os.listdir(ref_folder)
# output_files = os.listdir(output_folder)

# ref_files = sorted(ref_files, key=extract_number)
# # output_files = sorted(output_files)
# output_files = sorted(output_files, key=extract_number)
# print(ref_files)
# print(output_files)
# table_headers = ["File", "Reference File", "Output File", "CER Score", "WER Score"]
# table_data = []
# total_cer = 0.0
# total_wer = 0.0
# num_pairs = 0
# # Calculate scores for each pair of corresponding files
# # raw_bad_imgs = ['4.txt', '5.txt','6.txt','7.txt', '9.txt', '10.txt',  '13.txt', '14.txt', '15.txt', '16.txt', '17.txt', '20.txt', '21.txt', '22.txt']
# # skew_fix = ['4.txt', '5.txt','6.txt', '7.txt', '9.txt', '13.txt', '20.txt', '21.txt', '22.txt']
# # v7_bad_imgs = ['4.txt', '5.txt','6.txt','7.txt', '9.txt', '10.txt',  '13.txt', '20.txt', '21.txt', '22.txt']
# # v7_good_imgs = ['0.txt', '1.txt', '2.txt', '3.txt', '8.txt', '11.txt', '12.txt', '14.txt', '15.txt', '16.txt', '17.txt', '18.txt', '19.txt', '23.txt', '24.txt', '26.txt', '27.txt']
# for ref_file, output_file in zip(ref_files, output_files):
#   # print(ref_file, output_file)
#   # if ref_file not in bad_imgs:
# #    if ref_file in v7_good_imgs:
#     ref_path = os.path.join(ref_folder, ref_file)
#     output_path = os.path.join(output_folder, output_file)

#     # Read and normalize reference and output texts
#     ref_text = read_and_normalize(ref_path)
#     output_text = read_and_normalize(output_path)

#     # Calculate CER score
#     score = bag_of_characters_error_rate(output_text, ref_text)
#     # score = fastwer.score_sent(output_text, ref_text, char_level=True)

#     # word_score = fastwer.score_sent(output_text, ref_text, char_level=False)
#     # word_score = fastwer.score_sent(output_text, ref_text)#calculate_wer(output_text, ref_text)
#     word_score = calculate_wer(output_text, ref_text)
#     total_cer += score
#     total_wer += word_score
#     num_pairs += 1

#     table_data.append([ref_file, ref_text, output_text, score, word_score])

# table_data_dict = []
# for ref_file, ref_text, output_text, cer_score, wer_score in table_data:
#     table_data_dict.append({
#         "File": ref_file,
#         "Reference File": ref_text,
#         "Output File": output_text,
#         "CER Score": cer_score,
#         "WER Score": wer_score
#     })

# df = pd.DataFrame(table_data_dict)

# excel_file = r"C:\Users\earns\OneDrive\Desktop\ECE496-project\tesseractTable_scores.xlsx"

# with pd.ExcelWriter(excel_file) as writer:
#     df.to_excel(writer, sheet_name='Scores', index=False)

# print(f"Results saved to Excel file: {excel_file}")
# # print(tabulate(table_data, headers=table_headers, tablefmt="grid"))
# if num_pairs > 0:
#     overall_cer = total_cer / num_pairs
#     overall_wer = total_wer / num_pairs
# else:
#     overall_cer = 0.0
#     overall_wer = 0.0

# print(f"\nOverall CER and WER for {num_pairs} pairs: {overall_cer:.4f}, {overall_wer:.4f}")
