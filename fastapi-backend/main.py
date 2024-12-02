import os
import json
import pyrebase
from fastapi import FastAPI, HTTPException, UploadFile, Form, Request, status
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from firebase_admin import auth
from pydantic import BaseModel
from datetime import datetime
from database import SessionLocal, engine, Base
from models import PDF
from utils import extract_tasks, write_files

# Initialize FastAPI app
app = FastAPI()

# Set up Jinja2 templates
templates = Jinja2Templates(directory="templates")

# Authentication set up 
with open("config.json") as config_file:
    firebaseConfig = json.load(config_file)
pyre = pyrebase.initialize_app(firebaseConfig)

pyreAuth = pyre.auth()
authDB = pyre.database()

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


@app.post("/login")
async def login_user(email: str = Form(...), password: str = Form(...)):
    try:
        # Attempt to sign in with provided email and password
        user = pyreAuth.sign_in_with_email_and_password(email, password)
        id_token = user["idToken"]  # Retrieve the ID token assigned by Firebase
        # emailVerified = False
        # try:
        #     emailVerified = auth.get_user(user["localId"]).email_verified
        # except Exception as e:
        #     emailVerified = user["email_verified"]
        return {
            "message": "Login successful",
            "user_id": user["localId"],
            "id_token": id_token,
            # "email_verified": emailVerified,
        }
    except Exception as e:
        # Log the error and raise a 401 Unauthorized exception
        print("Login error:", e)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password"
        )


@app.post("/signup")
async def signup(email: str = Form(...), password: str = Form(...)):
    if not email.endswith("utoronto.ca"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email must be a utoronto.ca email",
        )

    try:
        # Create a new user with the provided email and password
        user = pyreAuth.create_user_with_email_and_password(email, password)
        user_id = user["localId"]  # Retrieve the unique ID assigned by Firebase
        id_token = user["idToken"]  # Retrieve the ID token assigned by Firebase

        # Attempt to store additional user data in the Realtime Database
        try:
            authDB.child("users").child(user_id).set(
                {"email": email, "password": password}
            )
        except Exception as db_error:
            # Check if the error is due to a 404 Not Found error
            if "Not Found for url" in str(db_error):
                print("Warning: url not found error raised, but signup was successful")
                try:
                    pyreAuth.send_email_verification(user["idToken"])
                except Exception as e:
                    print("Error sending email verification:", e)
            else:
                # If it's another type of error, raise it
                print("Error saving user data to database:", db_error)
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Error saving user data to database",
                )

        # Return success message if signup (and optional database write) succeed
        return {
            "message": "User created successfully",
            "user_id": user_id,
            "id_token": id_token,
        }

    except Exception as e:
        # Catch and print signup errors, raise a 400 Bad Request exception with error details
        print("Signup error:", e)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


class IdToken(BaseModel):
    id_token: str  # id_token of the user whose profile is being updated
    

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