from pypdf import PdfReader

reader = PdfReader("../Problem_statement/EcoSphere ESG Management Platform.pdf")
text_content = []

for i, page in enumerate(reader.pages):
    text_content.append(f"--- PAGE {i+1} ---")
    text_content.append(page.extract_text())

with open("../Problem_statement/extracted_text.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(text_content))

print("Successfully extracted PDF text!")
