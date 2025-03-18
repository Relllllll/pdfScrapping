import pymupdf  # PyMuPDF
from names_dataset import NameDataset
import csv
import re

# Initialize the NameDataset library
nd = NameDataset()

# Path to the uploaded PDF
pdf_path = '../SID_Dallas24_DigitalBook_r21-20.pdf'

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

    for page_number in range(len(pdf_document)):
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
                title = line.replace("Title:", "").strip()  # Extract title
                if last_row and not last_row[-1]:  # Check if last_row exists and has an empty Title column
                    last_row[-1] = title  # Attach title to the previous entry
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
                    continue  # Skip if the first word isn't a valid name

                # Extract affiliation from the **next** line
                affiliation = ""
                next_index = i + 1
                if next_index < len(lines):
                    next_line = lines[next_index].strip()

                    # If next line is an allowed role, use it
                    if next_line in allowed_roles:
                        affiliation = next_line
                        i += 1  # Skip this line as it's an affiliation

                # Ensure institutions are NOT detected as names
                if len(name_parts) > 3:
                    i += 1
                    continue  # Skip long non-human names

                # Determine Presentation Type
                presentation_type = "Poster Presentation" if poster_presentation_found else "Oral Presentation"

                # Default role assignment if no valid affiliation is found
                if not affiliation:
                    affiliation = "Speaker" if presentation_type == "Oral Presentation" else "Presenter"

                # Prepare the row for writing to CSV
                if len(name_parts) == 2:
                    last_row = [name_parts[0], '', name_parts[1], affiliation, presentation_type, '', '']
                elif len(name_parts) == 3:
                    last_row = [name_parts[0], name_parts[1], name_parts[2], affiliation, presentation_type, '', '']

            # Write the previous row to CSV if no title was added
            if last_row is not None and (i + 1 >= len(lines) or not lines[i + 1].startswith("Title:")):
                csv_writer.writerow(last_row)
                last_row = None  # Clear the last_row variable

            i += 1  # Move to next line

print("✅ CSV file has been written successfully!")
