import os
from django.shortcuts import render, redirect
from .forms import PDFForm
from .models import PDF
from .settings import MEDIA_ROOT
from .utils import extract_tasks, write_files

def upload_pdf(request):
    if request.method == 'POST':
        form = PDFForm(request.POST, request.FILES)
        if form.is_valid():
            pdf_instance = form.save()

            input_dir = os.path.join(MEDIA_ROOT, 'pdfs')
            os.makedirs(input_dir, exist_ok=True)
            input_file_path = os.path.join(MEDIA_ROOT, pdf_instance.pdf.name)

            with open(input_file_path, 'wb+') as destination:
                for chunk in request.FILES['pdf'].chunks():
                    destination.write(chunk)

            output_dir = os.path.join(MEDIA_ROOT, 'parsed_pdfs')
            os.makedirs(output_dir, exist_ok=True)

            # Extract the course name
            _, file_name = os.path.split(pdf_instance.pdf.name)
            course_name, _ = os.path.splitext(file_name)

            # Call the write_files function
            write_files(input_dir, output_dir)
            extracted_tasks_output_dir = os.path.join(MEDIA_ROOT, 'extracted_tasks')
            extract_tasks(output_dir, extracted_tasks_output_dir, course_name + '.txt')

            return redirect('pdf_list')
    else:
        form = PDFForm()
    return render(request, 'projectPath/upload_pdf.html', {'form': form})

def pdf_list(request):
    pdfs = PDF.objects.all()
    return render(request, 'projectPath/pdf_list.html', {'pdfs': pdfs})
