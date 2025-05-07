import fitz  # PyMuPDF
import pandas as pd
import csv
import re

# Load your custom full names list (first column should contain full names)
custom_names_df = pd.read_csv('names-data.csv')
custom_full_names = set(custom_names_df.iloc[:, 0].dropna().str.strip().str.lower())

# Path to your PDF file
pdf_path = '..//SID_Dallas24_DigitalBook_r21.pdf'

# Open the PDF
pdf_document = fitz.open(pdf_path)

# Regex to detect full name-like patterns (e.g., "John A Smith")
name_regex = re.compile(r'\b([A-Z][a-z]+(?:\s[A-Z][a-z]+){1,2})\b')

# Recognized presentation roles
allowed_roles = {"Author", "Chair", "Director", "Faculty", "Moderator", "Presenter", "Speaker", "Participant"}

# Output CSV
with open('names_own-db.csv', mode='w', newline='', encoding='utf-8') as csv_file:
    csv_writer = csv.writer(csv_file)
    csv_writer.writerow(['First Name', 'Middle Name', 'Last Name', 'Affiliation', 'Presentation Type', 'Role', 'Title'])

    poster_presentation_found = False
    last_row = None
    start_page = 19  # Adjust if needed

    for page_number in range(start_page, len(pdf_document)):
        page = pdf_document.load_page(page_number)
        text = page.get_text("text")

        if re.search(r'POSTER PRESENTATIONS', text, re.IGNORECASE):
            poster_presentation_found = True

        lines = text.split("\n")
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            if not line:
                i += 1
                continue

            # Handle Moderator/Chair
            if line.startswith("Moderator:") or line.startswith("Chairs:"):
                role = line.split(":")[0].strip()
                name_line = lines[i + 1].strip() if i + 1 < len(lines) else ''
                if name_line:
                    name_parts = name_line.split()
                    if len(name_parts) >= 2:
                        first = name_parts[0]
                        last = name_parts[-1]
                        middle = ' '.join(name_parts[1:-1]) if len(name_parts) > 2 else ''
                        csv_writer.writerow([first, middle, last, '', '', role, ''])
                i += 2
                continue

            # Handle Title
            if line.startswith("Title:"):
                title = line.replace("Title:", "").strip()
                if last_row and not last_row[-1]:
                    last_row[-1] = title
                i += 1
                continue

            # Check for names
            match = name_regex.match(line)
            if match:
                full_name = match.group(1)
                name_lower = full_name.lower().strip()
                if name_lower not in custom_full_names:
                    i += 1
                    continue

                name_parts = full_name.split()
                if len(name_parts) > 3:
                    i += 1
                    continue

                affiliation = ''
                if i + 1 < len(lines):
                    next_line = lines[i + 1].strip()
                    if next_line in allowed_roles:
                        affiliation = next_line
                        i += 1

                presentation_type = 'Poster Presentation' if poster_presentation_found else 'Oral Presentation'

                if len(name_parts) == 2:
                    last_row = [name_parts[0], '', name_parts[1], affiliation, presentation_type, '', '']
                elif len(name_parts) == 3:
                    last_row = [name_parts[0], name_parts[1], name_parts[2], affiliation, presentation_type, '', '']

            if last_row and (i + 1 >= len(lines) or not lines[i + 1].startswith("Title:")):
                csv_writer.writerow(last_row)
                last_row = None

            i += 1

print("✅ Done! Output written to 'names_own-db.csv'")
