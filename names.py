import fitz  # PyMuPDF
from names_dataset import NameDataset

nd = NameDataset()

def scan_pdf_and_get_next_word_after_first_name(pdf_path):
    doc = fitz.open(pdf_path)

    for page_num, page in enumerate(doc, start=1):
        lines = page.get_text("text").split("\n")

        for line_num, line in enumerate(lines, start=1):
            words = line.strip().split()

            for i in range(len(words) - 1):
                word = words[i].strip(",.():;").capitalize()
                next_word = words[i + 1].strip(",.():;")

                name_info = nd.search(word)
                if (
                    name_info and
                    'first_name' in name_info and
                    name_info['first_name'] is not None and
                    name_info['first_name'].get('country')
                ):
                    print(f"📄 Page {page_num}, 🧾 Line {line_num}: {word} {next_word}")

    doc.close()

# Example usage (make sure the path is correct)
scan_pdf_and_get_next_word_after_first_name("../5th-edition-of-cardiology-world-conference-2024-program-3.pdf")
