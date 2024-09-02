from django.shortcuts import render,redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login, authenticate
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
from .models import PDFUpload
import os
from django.http import HttpResponseRedirect




def home(request):
    return HttpResponseRedirect('http://localhost:3000/')

#api view for user login
@api_view(['POST'])
def login_view(request):
    if request.method == 'POST':
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return Response({"message": "Login successful"}, status=status.HTTP_200_OK)
        else:
            return Response({"message": "Invalid credentials"}, status=status.HTTP_400_BAD_REQUEST)

#Creating a view for the registration process
def register(request):
    #if block is for users who are already registered. This checks password and redirects to user-landing page
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request,user)
            return redirect('user_landing')
    #else block is for first time registration
    else:
        form = UserCreationForm()
    return render(request, 'register.html', {'form': form})

#creating a view to upload the pdf
def upload_pdf(request):
    if request.method == 'POST' and request.FILES['pdf']:
        pdf = request.FILES['pdf']
        upload = PDFUpload(user=request.user, file=pdf)
        upload.save()
        # Process the PDF and generate output (this would call your Python logic)
        output = process_pdf(os.path.join(settings.MEDIA_ROOT, upload.file.name))
        return render(request, 'user_landing.html', {'output': output})
    return render(request, 'user_landing.html')

#calling the function that acceots PDF as input and returns output
def process_pdf(pdf_path):
    return pdf_path

