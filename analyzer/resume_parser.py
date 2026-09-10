import os
import fitz
from docx import Document


def extract_text(file_path):

    extension = os.path.splitext(file_path)[1].lower()

    # PDF file
    if extension == ".pdf":

        document = fitz.open(file_path)

        text = ""

        for page in document:
            text += page.get_text()

        document.close()

        return text

    # DOCX file
    elif extension == ".docx":

        document = Document(file_path)

        text = ""

        for paragraph in document.paragraphs:
            text += paragraph.text + "\n"

        return text

    # Unsupported file
    else:

        raise ValueError(
            "Only PDF and DOCX files are supported."
        )