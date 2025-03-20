import fitz  # PyMuPDF
import csv
import re


def extract_text_from_pdf(file_path):
    with fitz.open(file_path) as doc:
        text = ""
        for page in doc:
            text += page.get_text()
    return text


def extract_parentheses_content(text):
    # Find all text inside parentheses using regex
    matches = re.findall(r'\((.*?)\)', text)
    cleaned_matches = []
    for content in matches:
        # Remove time indications (e.g., '5 MIN', '10 MIN', '3 MIN')
        cleaned_content = re.sub(r'\b\d+\s?MIN\b', '', content).strip()
        if cleaned_content:  # Only add non-empty cleaned content
            cleaned_matches.append(cleaned_content)
    return cleaned_matches


def save_to_csv(data, output_file):
    with open(output_file, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        # Write a header
        writer.writerow(["Address"])
        # Write each extracted text as a new row
        for item in data:
            writer.writerow([item])


def main():
    pdf_path = '../SID_Dallas24_DigitalBook_r21-20.pdf'
    csv_output_path = 'extracted_parentheses_content.csv'

    # Extract text from the PDF
    text_content = extract_text_from_pdf(pdf_path)

    # Extract content within parentheses
    extracted_content = extract_parentheses_content(text_content)

    # Save extracted content to a CSV file
    save_to_csv(extracted_content, csv_output_path)

    print(f"Extraction complete! CSV saved to {csv_output_path}")


if __name__ == "__main__":
    main()
