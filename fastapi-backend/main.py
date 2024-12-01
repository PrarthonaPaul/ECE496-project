import os
from fastapi import FastAPI, UploadFile, Form, Request, Depends
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse, HTMLResponse
from pydantic import BaseModel
from typing import List
from sqlalchemy.orm import Session
from datetime import datetime
from database import SessionLocal, engine, Base
from models import PDF
from forms import PDFForm
from utils import extract_tasks, write_files

# Initialize FastAPI app
app = FastAPI()

# Set up Jinja2 templates
templates = Jinja2Templates(directory="templates")

# Define media root and directories
MEDIA_ROOT = "media"
PDF_UPLOAD_DIR = os.path.join(MEDIA_ROOT, "pdfs")
PARSED_PDF_DIR = os.path.join(MEDIA_ROOT, "parsed_pdfs")
EXTRACTED_TASKS_DIR = os.path.join(MEDIA_ROOT, "extracted_tasks")

# Ensure directories exist
os.makedirs(PDF_UPLOAD_DIR, exist_ok=True)
os.makedirs(PARSED_PDF_DIR, exist_ok=True)
os.makedirs(EXTRACTED_TASKS_DIR, exist_ok=True)

# Initialize database
Base.metadata.create_all(bind=engine)

# Pydantic schema for PDF data
class PDFSchema(BaseModel):
    title: str
    file_path: str

# Dependency for database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/", response_class=HTMLResponse)
async def upload_form(request: Request):
    return templates.TemplateResponse("upload_pdf.html", {"request": request})


@app.post("/upload/")
async def upload_pdf(
    title: str = Form(...), 
    pdf: UploadFile = UploadFile(...)
    # db: Session = Depends(get_db)  # Use Depends for the database session
):
    db = next(get_db())
    input_dir = os.path.join(MEDIA_ROOT, 'pdfs')
    os.makedirs(input_dir, exist_ok=True)
    input_file_path = os.path.join(PDF_UPLOAD_DIR, pdf.filename)

    with open(input_file_path, "wb") as f:
        f.write(await pdf.read())

    output_dir = os.path.join(MEDIA_ROOT, 'parsed_pdfs')
    os.makedirs(output_dir, exist_ok=True)

    # Extract the course name
    _, file_name = os.path.split(pdf.filename)
    course_name, _ = os.path.splitext(file_name)

        # Save PDF metadata to the database
    pdf_instance = PDF(
        title=title,
        pdf=str(input_file_path),
        uploaded_at=datetime.utcnow()
    )
    db.add(pdf_instance)
    db.commit()
    db.refresh(pdf_instance)

    # Call the write_files function
    write_files(input_dir, output_dir)
    extracted_tasks_output_dir = os.path.join(MEDIA_ROOT, 'extracted_tasks')
    extract_tasks(output_dir, extracted_tasks_output_dir, course_name + '.txt')

    output_filepath = os.path.join(extracted_tasks_output_dir, f"{course_name}_results.txt")
    extrcted_tasks = []

    with open(output_filepath, "r") as f:
        for line in f:
            extrcted_tasks.append(line)

    # Redirect to the list view
    # return RedirectResponse(url="/pdfs/", status_code=303)
    return {"extract_tasks": extrcted_tasks}

# Route to display the list of uploaded PDFs
@app.get("/pdfs/", response_class=HTMLResponse)
async def pdf_list(request: Request):
    db = next(get_db())
    pdfs = db.query(PDF).all()
    return templates.TemplateResponse("pdf_list.html", {"request": request, "pdfs": pdfs})

@app.post("/clear-database/")
async def clear_database_endpoint():
    db = next(get_db())
    for table in reversed(Base.metadata.sorted_tables):
        db.execute(table.delete())
    db.commit()
    return {"message": "Database cleared!"}