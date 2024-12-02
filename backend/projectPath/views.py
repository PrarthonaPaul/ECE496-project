import os
from django.shortcuts import render, redirect
from .forms import PDFForm
from .models import PDF
from .settings import MEDIA_ROOT
from .utils import extract_tasks, write_files
import json
from django.http import JsonResponse

# def upload_pdf(request):
#     if request.method == 'POST':
#         form = PDFForm(request.POST, request.FILES)
#         if form.is_valid():
#             pdf_instance = form.save()

#             # Additional processing (if needed) before returning the updated list

#             # Fetch updated PDF list
#             pdfs = PDF.objects.all().values('id', 'title', 'pdf', 'uploaded_at')
#             pdf_list = list(pdfs)
#             return JsonResponse({'data': pdf_list}, status=201)  # 201 for successful creation
#     return JsonResponse({'error': 'Invalid form submission'}, status=400)

def upload_pdf(request):
    if request.method == 'POST':
        form = PDFForm(request.POST, request.FILES)
        if form.is_valid():
            pdf_instance = form.save()

            # Set up directories for processing
            input_dir = os.path.join(MEDIA_ROOT, 'pdfs')
            os.makedirs(input_dir, exist_ok=True)
            input_file_path = os.path.join(MEDIA_ROOT, pdf_instance.pdf.name)

            # Save the uploaded file to the media directory
            with open(input_file_path, 'wb+') as destination:
                for chunk in request.FILES['pdf'].chunks():
                    destination.write(chunk)

            # Set up output directories
            output_dir = os.path.join(MEDIA_ROOT, 'parsed_pdfs')
            os.makedirs(output_dir, exist_ok=True)

            # Extract the course name from the file name
            _, file_name = os.path.split(pdf_instance.pdf.name)
            course_name, _ = os.path.splitext(file_name)

            # Run the additional processing scripts
            write_files(input_dir, output_dir)
            extracted_tasks_output_dir = os.path.join(MEDIA_ROOT, 'extracted_tasks')
            extract_tasks(output_dir, extracted_tasks_output_dir, course_name + '.txt')

            # Fetch the updated list of PDFs
            pdfs = PDF.objects.all().values('id', 'title', 'pdf', 'uploaded_at')
            pdf_list = list(pdfs)

            # Return the updated list as JSON
            return JsonResponse({'data': pdf_list}, status=201)  # 201 for successful creation

    return JsonResponse({'error': 'Invalid form submission'}, status=400)

# def pdf_list(request):
#     pdfs = PDF.objects.all()
#     return render(request, 'projectPath/pdf_list.html', {'pdfs': pdfs})
# def pdf_list(request):
#     try:
#         # Fetch PDF records
#         pdfs = PDF.objects.all().values('id', 'pdf', 'uploaded_at')  # Adjust fields as needed
#         pdf_list = list(pdfs)
#         return JsonResponse({'data': pdf_list})
#     except Exception as e:
#         # Return an error response in JSON format if something goes wrong
#         return JsonResponse({'error': str(e)}, status=500)