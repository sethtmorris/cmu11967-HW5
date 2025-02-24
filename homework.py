import argparse
import re
import requests
import json
from utils import  read_warc_file, retrieve_bad_words
from datasets import load_dataset
from typing import Set, Dict
from bs4 import BeautifulSoup
# you might need to import other modules depending on your implementation

def retrieve_bad_words() -> set[str]:
    """Helper function - that reads a list of bad words from a file and returns them as a set.
    Returns:
        Set[str]: A set containing lowercase bad words.
    """
    with open('./bad_word_list.txt', 'r') as file:
        records = file.read().strip().split('\n')
        bad_words = [record.lower() for record in records]
        return set(bad_words)

def html_to_text(html: str) -> str:
    """Converts HTML content to plain text..
    Args:
        html (bytes): HTML content as bytes.
    Returns:
        str: Plain text extracted from HTML.
    """
    soup = BeautifulSoup(html, 'html.parser')
    return soup

def replace_pii(text: str) -> str:
    """Masks personally identifiable information (PII) from text with the specified masking formats.
    Args: 
        text (str): Candidate text.
    Returns:
        str: Text with PII obfuscated.
    """
    cleaned_of_ssn = re.sub('\d\d\d-\d\d-\d\d\d\d', 'XXX-XX-XXXX', text)
    cleaned_of_phone_number = re.sub('\+1 ?\d{10}', '+1 XXXXXXXXXX', cleaned_of_ssn)
    print(cleaned_of_phone_number)
    return cleaned_of_phone_number

def clean_text(text: str) -> str:
    """Removes substrings identified as low-quality according to alphanumeric, whitespace and valid document checks.  
    Args:
        text (str): document to process.
    Returns:
        str: cleaned document
    """

    new_text = ""
    for paragraph in text.splitlines():
        # print(paragraph)
        if not re.search(r"\.|\?|!", paragraph):
            pass
        elif (len(paragraph) > 100) and (' ' not in paragraph):
            pass
        else:
            if new_text != "":
               new_text += '\n'
            new_text += paragraph

    # print(new_text)
    return new_text

def heuristic_quality_filter(text: str) -> bool:
    """Rejects documents based on the rules.
    Args:
        text (str): document to check
    Returns:
        bool: returns True if the document passes the four filters, False otherwise.
    """
    bad_word_set = retrieve_bad_words()
    bad_word_pattern = '|'.join(re.escape(s) for s in bad_word_set)
    if re.search(r"\S", text):
        if re.search(r"\.|\?|!", text):
            if len(re.findall(r"[a-zA-Z]|\d|\.|\?|!|\s", text)) >= 0.8 * len(text):
                if not bool(re.search(bad_word_pattern, text.lower())):
                    return True
    return False

if __name__ == '__main__' :
    parser = argparse.ArgumentParser()
    parser.add_argument('--fname', type = str,  default = '', help = 'Specify the path for your warc file.')
    parser.add_argument('--num_records', type = int,  default=30, help = 'Specify the number of records you want to parse (only used for debugging with smaller sets)')
    args = parser.parse_args()

    if args.fname:
        for url, html_text in read_warc_file(args.fname, args.num_records):
            text = html_to_text(html_text)
            cleaned_text = clean_text(text)
            cleaned_nopii_text = replace_pii(cleaned_text)
            passes_check = heuristic_quality_filter(cleaned_nopii_text)
            
            print(url)
            print("Passes heuristic quality filter:", passes_check)
            print(cleaned_nopii_text)
            print("\n\n\n")
    else:
        print("Usage: python homework.py --fname data.warc")
        
