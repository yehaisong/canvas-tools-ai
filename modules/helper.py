import random
import string
import sys
import json
from colorama import Fore, Back, Style
from datetime import datetime
from pytz import timezone
import pandas as pd
import os
import fitz
from docx import Document


def print_random():
    """print a random punctuation symbol at the same place for loops"""
    print (" ^"+random.choice(string.punctuation)+"^", end="\r")

def html_escape(s)->str:
    """Returns a standard html code string.

    :param s: string to be escaped
    """
    return s.replace('&amp', '&').replace('&lt;', '<').replace('&gt;', '>').replace('&quot;', '"').replace("&#39;", '\'')

def html_decode(s)->str:
    """
    Returns the ASCII decoded version of the given HTML string. This does
    NOT remove normal HTML tags like <p>.

    :param s: string to be decoded
    """
    htmlCodes = (
            ("'", '&#39;'),
            ('"', '&quot;'),
            ('>', '&gt;'),
            ('<', '&lt;'),
            ('&', '&amp;')
        )
    for code in htmlCodes:
        s = s.replace(code[1], code[0])
    return s

def confirm_to_continue(msg:string):    
    """
    Print a message to console asking user's input. Press enter to continue and x to exit

    :param msg: The message to be displayed
    """
    input1 = input(f"{msg} (Press enter to continue, 'x' to exit):")
    if input1.lower() == "x":
        sys.exit()
    
def invalid_input_exit():
    """
    Print "Invalid input" and exit.
    """
    print (f"{Fore.RED}{Back.YELLOW}Invalid input.{Style.RESET_ALL}")
    sys.exit()

def print_reponse_status(status):
    """
    Print a http response code with color

    :param status: the http response code, e.g. 200, 404, etc.
    """
    if(status==200):
        print(f"{Fore.WHITE}{Back.GREEN}API Response: {status} {Style.RESET_ALL}")
    else:
        print(f"{Fore.WHITE}{Back.LIGHTMAGENTA_EX}API Response: {status} {Style.RESET_ALL}")

def to_local_time(utc:string, tz='US/Eastern'):
    """
    Concert a utc date time string value to a local time string value

    :param utc: A utc datetime string value, e.g., 2022-08-19T17:16:08Z
    :param timezone: A string value of a timezone, 
    """
    utc_dt = datetime.strptime(utc,"%Y-%m-%dT%H:%M:%SZ")
    #loc_dt = utc_dt.astimezone(timezone(tz))
    offset = timezone(tz).utcoffset(utc_dt).total_seconds()/3600
    return utc_dt+pd.DateOffset(hours = offset)

def search_json(json_obj, key:str, value):
    """Find a key-value pair in a json object and return the first found json object

    Args:
        json_obj (_type_): Target json object
        key (str): key to find
        value (_type_): value to find

    Returns:
        _type_: first found json object with the key-value pair
    """
    if isinstance(json_obj, dict):
        if key in json_obj and json_obj[key] == value:
            return json_obj
        else:
            for k in json_obj:
                result = search_json(json_obj[k], key, value)
                if result:
                    return result
    elif isinstance(json_obj, list):
        for item in json_obj:
            result = search_json(item, key, value)
            if result:
                return result
    return None

def load_search_group(file:str):
    """This function is for loading a search group from a json file and print the group name and id on screen.

    Args:
        file (str): search template file name

    Returns:
        _type_: The selected search group
    """
    preset_search_template = []
    with open("search_template.json","r") as tf:
        temp = json.load(tf)    
        for p in temp:
            preset_search_template.append(p)
    print ("Pick a exising search group:")

    for t in preset_search_template:
        print (f"{Fore.YELLOW}{t['id']}: {t['name']}{Style.RESET_ALL}")
    ## select a template
    sel = input(f"Choose a group by entering the group number {Fore.YELLOW}(0-{len(preset_search_template)-1}){Style.RESET_ALL}, x to exit:")
    if(sel.lower() == 'x'):
        sys.exit()
    if not sel.isdigit():
        invalid_input_exit()
    if int(sel)<0 or int(sel)>=len(preset_search_template):
        invalid_input_exit()
    t=preset_search_template[int(sel)]
    #if selected 0
    if(sel=="0"):
        search_key = input(f"Enter the searching keywaord: ")
        t["prefix"] = search_key
        t["params"] = {
            "search_term":search_key
        }
    return t


def check_path(path:str)->str:
    if not os.path.exists(path):
        os.makedirs(path)
    return path

def convert_docx_to_md(input_file:str, output_file:str)->str:
    try:
        # Read the .docx file
        doc = Document(input_file)
        extracted_text = []  # A list to hold extracted text
        # Iterate through the document's elements
        for element in doc.element.body.iterchildren():
            # Handle Paragraph
            if element.tag.endswith('p'):
                paragraph_text = ''.join(node.text for node in element.iterdescendants() if node.tag.endswith('t') and node.text)
                extracted_text.append(paragraph_text)
            # Handle Table
            elif element.tag.endswith('tbl'):
                for row in element.iterchildren():
                    cell_texts = []
                    for cell in row.iterchildren():
                        cell_text = ''.join(node.text for node in cell.iterdescendants() if node.tag.endswith('t') and node.text)
                        cell_texts.append(cell_text)
                    # Join cell texts with a delimiter (e.g., ", ") for readability, or modify as needed
                    extracted_text.append(', '.join(cell_texts))
        # Join all extracted texts into a single string with newline separation
        combined_text = "\n".join(extracted_text)        
        with open(output_file, "w", encoding="utf-8") as md_file:
            md_file.write(combined_text)
        return output_file
    except Exception as e:
        print(f"Error during conversion from docx to md: {e}")
        return None
               
def convert_pdf_to_md(input_file:str,output_file:str)->str:
    try:
        # Open the PDF file
        doc = fitz.open(input_file)
        markdown_content = ""
        # Loop through each page in the PDF
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            # Extract text from the page
            text = page.get_text()
            # Append this page's text to the markdown content
            # You might want to add your own Markdown formatting here
            markdown_content +=" "+ text + "\n\n"  # Adding a double newline as a simple separator between pages
        # Write the extracted text to a Markdown file
        with open(output_file, "w", encoding="utf-8") as md_file:
            md_file.write(markdown_content)
        return output_file
    except Exception as e:
        print(f"Error during conversion from docx to md: {e}")
        return None