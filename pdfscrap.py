import fitz  # PyMuPDF
import csv
import re
from names_dataset import NameDataset
import unicodedata  # For normalization
import json
import medialpy  # For medical term validation
from nameparser import HumanName


event_ID = ""
last_updated = ""
first_name = ""
middle_name =  ""
last_name= ""
degrees = ""
email = ""
city =  ""
state = ""
country = ""
institution = ""
bio =  ""
role =  ""
presentation_type = ""
presentation_url_abstract =  ""
presentation_url_abstract_quality = ""
presentation_url = ""
presentation_url_quality = ""
oral_poster =  ""
session_title = ""
session_date = ""
session_start_time = ""
session_end_time = ""
title = ""
abstract = ""



# Function to load stop words from a JSON file
def load_stop_words(json_path):
    with open(json_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
    return set(data["stop_words"])

# Load the stop words
stop_words = load_stop_words('stop_words.json')

# Additional irrelevant phrases or keywords to skip
irrelevant_keywords = {"sponsors", "provided support", "educational", "meeting", "session", "attendees", "lecture"}

# Initialize the NameDataset
name_dataset = NameDataset()

# Function to check if a string is a valid name
def is_valid_name(name):
    # Parse the name using nameparser
    parsed_name = HumanName(name)

    # Check if we have a valid first name, last name, or both
    return bool(parsed_name.first and parsed_name.last)

# Function to normalize and title-case the names
def normalize_name(name):
    normalized_name = unicodedata.normalize('NFC', name)
    return normalized_name.strip().title()

# Function to check if a word is a medical term using medialpy
def is_medical_term(word):
    return medialpy.exists(word)

# Function to check if a name contains any stop words and skip the stop word with its preceding word
def skip_stop_words(name, stop_words):
    name_parts = name.lower().split()

    # Iterate through the name parts to detect stop words
    for i, part in enumerate(name_parts):
        if part in stop_words and i > 0:  # Ensure it's not the first word
            # Skip the stop word and the word before it
            name_parts[i - 1] = ""  # Clear the word before the stop word
            name_parts[i] = ""  # Clear the stop word
            break  # Only skip the first occurrence and stop further checks

    # Rebuild the name without the skipped words
    return " ".join(name_parts).strip()

# Function to check if the institution has more than 5 words
def is_institution_too_long(institution):
    # Check if the institution has more than 5 words or if it contains long, unrelated strings
    institution = institution.strip() if institution else ""
    if len(institution.split()) > 5 or len(institution) > 100:  # Also check length of the string
        return True
    return False

# Function to check if the institution is likely unrelated (e.g., contains medical terms or irrelevant phrases)
def is_unrelated_institution(institution):
    # Check if the institution contains medical terms or other irrelevant keywords
    if any(keyword.lower() in institution.lower() for keyword in irrelevant_keywords):
        return True
    # Check for medical terms using medialpy
    institution_words = institution.split()
    for word in institution_words:
        if is_medical_term(word):
            return True
    return False

# Function to check if the name parts (first, middle, last) contain only one word
def has_only_one_word(name):
    name_parts = name.split()
    return len(name_parts) == 1

# Function to extract and validate names
def extract_and_validate_name(name, institution):
    # Apply the skip stop words logic first
    name = skip_stop_words(name, stop_words)

    # Now, check if the name is a valid name using nameparser
    if is_valid_name(name) and has_only_one_word(name) and not is_institution_too_long(institution) and not is_unrelated_institution(institution):
        return name, institution
    else:
        return None, None

# Function to check for irrelevant phrases in the text
def contains_irrelevant_keywords(text, keywords):
    for keyword in keywords:
        if keyword.lower() in text.lower():
            return True
    return False

# Function to extract and validate names from PDF and write to CSV
def extract_and_parse_names_from_pdf(pdf_path, csv_path):
    # Open the PDF file
    doc = fitz.open(pdf_path)
    names_and_data = []

    # Regex to match names (including apostrophes, special characters, and titles) with optional qualifications and institutions in parentheses
    name_pattern = r'([A-Za-zÀ-ÿ\’]+(?: [A-Za-zÀ-ÿ\’]+)*)\s*(?:,?\s*([A-Za-z\., ]+))?\s*(?:\(([^)]+)\))?'

    for page_num, page in enumerate(doc, start=1):
        try:
            text = page.get_text("text")
            if not text:
                continue

            # Split the text into lines and filter out those with irrelevant keywords
            lines = text.split('\n')
            filtered_lines = [line for line in lines if not contains_irrelevant_keywords(line, irrelevant_keywords)]

            # Reconstruct the page text from the filtered lines
            filtered_text = "\n".join(filtered_lines)

            # Skip the page if it ends up being empty after filtering
            if not filtered_text.strip():
                print(f"Skipped page {page_num} due to irrelevant keywords.")
                continue

            # Debugging: Print the page text
            print(f"--- Page {page_num} ---")
            print(filtered_text)

            # Extract names with optional qualifications and institutions in parentheses
            name_matches = re.findall(name_pattern, filtered_text)

            # Debugging: Print matches
            print(f"Name Matches: {name_matches}")

            # Iterate through the matches and extract names and institutions
            for match in name_matches:
                name, qualifications, institution = match
                name = normalize_name(name)

                # Skip names that contain stop words or medical terms
                name = skip_stop_words(name, stop_words)
                if not name:  # If the name becomes empty after skipping
                    print(f"Skipped (stop word): {match}")
                    continue
                if is_medical_term(name):
                    print(f"Skipped (medical term): {name}")
                    continue

                # Skip if the institution is too long or irrelevant
                if is_institution_too_long(institution) or is_unrelated_institution(institution):
                    print(f"Skipped (institution too long or irrelevant): {institution}")
                    continue

                # Split the name into first, middle, and last names
                name_parts = name.split()
                first_name = name_parts[0]
                middle_name = " ".join(name_parts[1:-1]) if len(name_parts) > 2 else ""
                last_name = name_parts[-1]

                # Skip if the first and last names are the same
                if first_name.lower() == last_name.lower():
                    print(f"Skipped (first and last name identical): {name}")
                    continue

                # Ensure first, middle, and last name have only one word each
                if not has_only_one_word(first_name) or (middle_name and not has_only_one_word(middle_name)) or not has_only_one_word(last_name):
                    print(f"Skipped (name contains more than one word): {name}")
                    continue

                # Combine qualifications or institutions into their own column
                institution = institution if institution else qualifications
                if institution:
                    institution = institution.strip()

                # Collect the data
                names_and_data.append((event_ID,last_updated,first_name, middle_name, last_name,degrees,email,city,state,country,institution,bio,role,presentation_type,presentation_url_abstract,presentation_url_abstract_quality,presentation_url,presentation_url_quality,oral_poster,session_title,session_date,session_start_time,session_end_time,title,abstract))

        except Exception as e:
            print(f"Error on page {page_num}: {e}")

    # Write data to CSV
    with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["event_ID","last_updated","first_name","middle_name","last_name","degrees","email","city","state","country","institution","bio","role","presentation_type","presentation_url_abstract","presentation_url_abstract_quality","presentation_url","presentation_url_quality","oral_poster","session_title","session_date","session_start_time","session_end_time","title","abstract"])  # Header row

        for entry in names_and_data:
            writer.writerow(entry)

    print("CSV file with validated names and institutions created successfully.")

# Usage example
extract_and_parse_names_from_pdf("../SID_Dallas24_DigitalBook_r21-20.pdf", "OUTPUT.csv")
