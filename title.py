import fitz  # PyMuPDF
import csv


def extract_red_text_from_pdf(file_path):
    red_texts = []
    with fitz.open(file_path) as doc:
        for page in doc:
            blocks = page.get_text("dict")['blocks']
            for block in blocks:
                if 'lines' not in block:  # Check if 'lines' key exists
                    continue
                for line in block['lines']:
                    for span in line['spans']:
                        # Extract RGB values from the color integer
                        color = span['color']
                        r = (color >> 16) & 0xFF
                        g = (color >> 8) & 0xFF
                        b = color & 0xFF

                        # Check if the color is close to red
                        if r > 150 and g < 100 and b < 100:  # Roughly detecting reddish text
                            red_texts.append(span['text'])
    return red_texts

def save_to_csv(data, output_file):
    with open(output_file, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(["Extracted Red Text"])
        for item in data:
            writer.writerow([item])

def main():
    pdf_path = '../SID_Dallas24_DigitalBook_r21-20.pdf'
    csv_output_path = 'extracted_red_text.csv'

    # Extract red text from the PDF
    red_text_content = extract_red_text_from_pdf(pdf_path)

    # Save extracted red text to a CSV file
    save_to_csv(red_text_content, csv_output_path)

    print(f"Extraction complete! CSV saved to {csv_output_path}")


if __name__ == "__main__":
    main()
