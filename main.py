import pymupdf  # PyMuPDF
from names_dataset import NameDataset
import csv
import re

# Initialize the NameDataset library
nd = NameDataset()

# Path to the uploaded PDF
pdf_path = '..//SID_Dallas24_DigitalBook_r21-20-130.pdf'

# Open the PDF using PyMuPDF
pdf_document = pymupdf.open(pdf_path)

# Regex for detecting names (allowing middle names)
name_regex = re.compile(r'\b([A-Z][a-z]+(?:\s[A-Z][a-z]+)*)\b')

# Allowed roles
allowed_roles = {"Author", "Chair", "Director", "Faculty", "Moderator", "Presenter", "Speaker", "Participant"}

# Open CSV file
with open('names_with_presentation.csv', mode='w', newline='', encoding='utf-8') as csv_file:
    csv_writer = csv.writer(csv_file)
    csv_writer.writerow(['First Name', 'Middle Name', 'Last Name', 'Affiliation', 'Presentation Type', 'Role', 'Title'])

    poster_presentation_found = False  # Flag for poster presentations
    last_row = None  # Store the last row before writing to CSV
    start_page = 19  # Start processing from page 19

    for page_number in range(start_page, len(pdf_document)):
        page = pdf_document.load_page(page_number)
        text = page.get_text("text")  # Extract as raw text

        # Check if "Poster Presentations" is on the page
        if re.search(r'POSTER PRESENTATIONS|Poster Presentations|poster presentations', text):
            poster_presentation_found = True

        lines = text.split("\n")  # Split into lines

        i = 0
        while i < len(lines):
            line = lines[i].strip()
            if not line:
                i += 1
                continue

            # Check for Moderator and Chair lines
            if line.startswith("Moderator:") or line.startswith("Chairs:"):
                role = line.split(":")[0].strip()
                name_line = lines[i + 1].strip() if i + 1 < len(lines) else ''

                if name_line:
                    name_parts = name_line.split()

                    if len(name_parts) >= 2:  # At least a first and last name
                        first_name = name_parts[0]
                        last_name = name_parts[-1]
                        middle_name = ' '.join(name_parts[1:-1]) if len(name_parts) > 2 else ''

                        csv_writer.writerow([first_name, middle_name, last_name, '', '', role, ''])

                i += 2  # Skip the next line (already processed)
                continue

            # Check for Title lines
            if line.startswith("Title:"):
                title = line.replace("Title:", "").strip()
                if last_row and not last_row[-1]:  # Check if Title column is empty
                    last_row[-1] = title  # Add title to the last row
                i += 1
                continue

            # Match potential names in the line
            match = name_regex.match(line)
            if match:
                full_name = match.group(1)
                name_parts = full_name.split()

                # Ensure first word is a valid first name
                if not nd.search(name_parts[0]):
                    i += 1
                    continue

                # Extract affiliation from the next line
                affiliation = ""
                next_index = i + 1
                if next_index < len(lines):
                    next_line = lines[next_index].strip()

                    if next_line in allowed_roles:
                        affiliation = next_line
                        i += 1  # Skip the line

                # Avoid overly long names (likely not human)
                if len(name_parts) > 3:
                    i += 1
                    continue

                # Determine presentation type
                presentation_type = "Poster Presentation" if poster_presentation_found else "Oral Presentation"

                # Prepare row
                if len(name_parts) == 2:
                    last_row = [name_parts[0], '', name_parts[1], affiliation, presentation_type, '', '']
                elif len(name_parts) == 3:
                    last_row = [name_parts[0], name_parts[1], name_parts[2], affiliation, presentation_type, '', '']

            # Write last_row to CSV if no upcoming title
            if last_row is not None and (i + 1 >= len(lines) or not lines[i + 1].startswith("Title:")):
                csv_writer.writerow(last_row)
                last_row = None

            i += 1

print("✅ CSV file has been written successfully!")
