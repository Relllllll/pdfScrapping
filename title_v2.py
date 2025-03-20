import fitz  # PyMuPDF
import csv

# Define the function to extract text after "Title:"
def extract_titles_from_pdf(pdf_path):
    titles = []

    # Open the PDF file
    with fitz.open(pdf_path) as doc:
        for page in doc:
            text = page.get_text()
            lines = text.split('\n')

            # Search for lines that contain "Title:"
            for line in lines:
                if "Title:" in line:
                    title = line.split("Title:")[1].strip()
                    if title:
                        titles.append([title])

    return titles

# Define the function to save titles to a CSV file
def save_titles_to_csv(titles, output_csv):
    with open(output_csv, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(["Title"])
        writer.writerows(titles)

# Path to the input PDF file and the output CSV file
pdf_path = '../5th-edition-of-cardiology-world-conference-2024-program-3.pdf'
output_csv = 'extracted_titles.csv'

# Extract titles and save them to the CSV file
titles = extract_titles_from_pdf(pdf_path)
save_titles_to_csv(titles, output_csv)

print(f"Extraction completed. Titles saved to {output_csv}.")
