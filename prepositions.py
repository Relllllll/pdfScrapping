import fitz  # PyMuPDF

# Load prepositions from file
def load_prepositions(file_path="C:/Users/User1/PycharmProjects/new1/.venv/prepositions.txt"):
    with open(file_path, 'r') as f:
        return set(word.strip().lower() for word in f.readlines())

# Check and print lines containing prepositions
def scan_pdf_for_prepositions(pdf_path, prepositions):
    doc = fitz.open(pdf_path)

    for page_num, page in enumerate(doc, start=1):
        text = page.get_text("text")  # raw text from the page
        lines = text.split("\n")  # split into lines

        for line_num, line in enumerate(lines, start=1):
            words = line.lower().split()
            if any(word in prepositions for word in words):
                print(f"📄 Page {page_num}, 🧾 Line {line_num}: {line}")

    doc.close()

# Run the tool
if __name__ == "__main__":
    prepositions = load_prepositions("prepositions.txt")
    scan_pdf_for_prepositions("C:/Users/User1/PycharmProjects/new1/5th-edition-of-cardiology-world-conference-2024-program-3.pdf", prepositions)