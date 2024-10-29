from django.shortcuts import render, redirect
from .forms import PDFForm
from .models import PDF

def upload_pdf(request):
    if request.method == 'POST':
        form = PDFForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('pdf_list')
    else:
        form = PDFForm()
    return render(request, 'projectPath/upload_pdf.html', {'form': form})

def pdf_list(request):
    pdfs = PDF.objects.all()
    return render(request, 'projectPath/pdf_list.html', {'pdfs': pdfs})
