import fitz  # PyMuPDF
import pandas as pd
import csv
import re

# Load your custom full names list
custom_names_df = pd.read_csv('names-data.csv')
custom_full_names = set(custom_names_df.iloc[:, 0].dropna().str.strip().str.lower())

# PDF path
pdf_path = '../SID_Dallas24_DigitalBook_r21.pdf'
pdf_document = fitz.open(pdf_path)

# Regex for name patterns
name_regex = re.compile(r'\b([A-Z][a-z]+(?:\s[A-Z][a-z]+){1,2})\b')

# Allowed roles
allowed_roles = {"Author", "Chair", "Director", "Faculty", "Moderator", "Presenter", "Speaker", "Participant"}

# CSV setup
with open('names_red_title_before.csv', mode='w', newline='', encoding='utf-8') as csv_file:
    csv_writer = csv.writer(csv_file)
    csv_writer.writerow(['First Name', 'Middle Name', 'Last Name', 'Affiliation', 'Presentation Type', 'Role', 'Title'])

    poster_presentation_found = False
    start_page = 19

    for page_number in range(start_page, len(pdf_document)):
        page = pdf_document.load_page(page_number)
        blocks = page.get_text("dict")["blocks"]

        lines = []  # [(text, is_red)]
        for block in blocks:
            if 'lines' not in block:
                continue
            for line in block['lines']:
                line_text = ''
                is_red = False
                for span in line['spans']:
                    color = span['color']
                    r = (color >> 16) & 0xFF
                    g = (color >> 8) & 0xFF
                    b = color & 0xFF
                    text = span['text'].strip()
                    if not text:
                        continue
                    if r > 150 and g < 100 and b < 100:
                        is_red = True
                    line_text += text + ' '
                lines.append((line_text.strip(), is_red))

        last_red_text = ""  # Store the most recent red text seen before a name
        i = 0
        while i < len(lines):
            line, is_red = lines[i]
            if not line:
                i += 1
                continue

            if is_red:
                last_red_text = line  # Store red title before name
                i += 1
                continue

            if line.startswith("Moderator:") or line.startswith("Chairs:"):
                role = line.split(":")[0].strip()
                name_line = lines[i + 1][0] if i + 1 < len(lines) else ''
                if name_line:
                    name_parts = name_line.split()
                    if len(name_parts) >= 2:
                        first = name_parts[0]
                        last = name_parts[-1]
                        middle = ' '.join(name_parts[1:-1]) if len(name_parts) > 2 else ''
                        csv_writer.writerow([first, middle, last, '', '', role, last_red_text])
                        last_red_text = ""  # Clear after using
                i += 2
                continue

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

                # Check for role/affiliation line after the name
                affiliation = ''
                if i + 1 < len(lines):
                    next_line = lines[i + 1][0]
                    if next_line in allowed_roles:
                        affiliation = next_line
                        i += 1

                presentation_type = 'Poster Presentation' if poster_presentation_found else 'Oral Presentation'

                if len(name_parts) == 2:
                    csv_writer.writerow([name_parts[0], '', name_parts[1], affiliation, presentation_type, '', last_red_text])
                elif len(name_parts) == 3:
                    csv_writer.writerow([name_parts[0], name_parts[1], name_parts[2], affiliation, presentation_type, '', last_red_text])

                last_red_text = ""  # Clear after assigning it

            i += 1

print("✅ Done! Output written to 'names_red_title_before.csv'")
