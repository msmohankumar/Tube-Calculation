# pdf_reader.py
import PyPDF2

def extract_text(pdf_path):
    text = ""
    with open(pdf_path, "rb") as f:
        reader = PyPDF2.PdfReader(f)
        for page in reader.pages:
            text += page.extract_text()
    return text

# Example
text = extract_text("pdfs/Bend_manual.pdf")
print(text[:500])  # print first 500 characters
