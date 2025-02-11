import PyPDF2
import polars as pl
import re
import os
import json
from io import StringIO
import polars as pl
import xml.etree.ElementTree as ET


def extract_text_from_pdf(pdf_path: str) -> str:
    """Extracts the text from a given pdf file

    Args:
        pdf_path (str): Path to the pdf-file

    Returns:
        str: Returns the content of the pdf as python str object
    """
    with open(pdf_path, "rb") as file:
        reader = PyPDF2.PdfReader(file)
        text = "\n".join(
            [page.extract_text() for page in reader.pages if page.extract_text()]
        )
    return text

def write_all_to_txt(folder_path):
    pdf_files = [f"{folder_path}\\{f}" for f in os.listdir(folder_path) if f.endswith('.pdf')]
    for f in pdf_files:
        try:
            with open(f"{f}.txt", "w") as txt:
                txt.write(extract_text_from_pdf(f))
        except:
            pass


def text_to_polars(plaintext: str) -> pl.DataFrame:
    """Converts a str into polars

    Args:
        plaintext (str): plaintext as str

    Returns:
        pl.DataFrame: Returns polars DataFrame structured as Name, Party, Speech
    """

    text_cleaned = re.sub(r"\(\s*(Zuruf|Beifall).*?\)", "", plaintext, flags=re.DOTALL)

    pattern = r"(?P<name>[A-Za-zÄÖÜäöüß\s-]+)(?: \((?P<party>[A-Za-zÄÖÜäöüß\s/-]+)\))?:\n(?P<speech>.*?)(?=\n[A-ZÄÖÜ][A-Za-zÄÖÜäöüß\s-]+(?: \([A-Za-zÄÖÜäöüß\s/-]+\))?:|\nPräsidentin|$)"

    matches = re.finditer(pattern, text_cleaned, re.DOTALL)

    data = [
        {
            "name": m.group("name"),
            "party": m.group("party"),
            "speech": m.group("speech").strip(),
        }
        for m in matches
    ]

    return pl.DataFrame(data).drop_nulls()

# Detailed implementation
def extract_pdf_data_and_export_to_json(folder_path, output_json_path):
    """Makes one long json out of all .pdf files in the given folder path.
    Args:   folder_path (input path),
            output_json_path (output path)
    
    """

    pdf_files = [f for f in os.listdir(folder_path) if f.endswith('.pdf')]
    
    data_list = []
    
    for pdf_file in pdf_files:
        # Extract data from filename
        match = re.match(r'(\d+)\. Sitzung, (\d+)\. Wahlperiode, (\d{2}\.\d{2}\.\d{4})\.pdf', pdf_file)
        if match:
            sitzung_num = match.group(1)
            wahlperiode_num = match.group(2)
            date = match.group(3)
            
            # Extract text from PDF
            pdf_path = os.path.join(folder_path, pdf_file)
            text = extract_text_from_pdf(pdf_path)
            
            try:
                # Create a dictionary from extracted data
                data_dict = {
                    "datum": date,
                    "sitzung": sitzung_num,
                    "wahlperiode": wahlperiode_num,
                    "text": text_to_json(text)
                }
                
                data_list.append(data_dict)
            except Exception as e:
                print(f"{sitzung_num}. Sitzung, Wahlperiode {wahlperiode_num}, datum {date}, error: {e}")
    
    # Write data list to a JSON file
    with open(output_json_path, 'w', encoding='utf-8') as json_file:
        json.dump(data_list, json_file, ensure_ascii=False, indent=4)


def text_to_json(text):

    #print(text[10000:50000])

    pattern = "Die Sitzung ist eröffnet."

    # Perform the search
    #matches = list(re.finditer(pattern, text))
    #match = matches[1]
    match = re.search(pattern, text)

    if match:
        # Get the start and end positions of the match
        start, end = match.span()
        
        # Get everything up to the match and everything after the match
        header_text = text[:start]
        rest_text = text[start:]

        pattern = "Die Sitzung ist geschlossen."

        # Perform the search
        match = re.search(pattern, rest_text)
        speech_array = []

        if match:
            # Get the start and end positions of the match
            start, end = match.span()

            body_text = rest_text[:start]
            footer_text = rest_text[end:]

            pattern = r"\n[A-ZÄÖÜ][a-zäöü]+\s[A-ZÄÖÜ][a-zäöü]+.*:\n"

            # Perform the search for all matches
            matches = list(re.finditer(pattern, body_text))

            if matches:
                # Initialize a cursor to keep track of the current position in the text
                cursor = 0
                last_speaker = ""

                for match in matches:

                    # Get the start and end positions of the current match
                    start, end = match.span()
                    
                    last_speaker = body_text[start:end-2]

                    last_speech = body_text[cursor:start]

                    # Update the cursor to the end of the current match
                    cursor = end+1

                    if last_speaker != "":
                        speech_dict = {
                            "Redner": last_speaker,
                            "Rede" : last_speech
                        }
                        speech_array.append(speech_dict)
                
                # Output everything after the last match
                after_last_match = body_text[cursor:]

        else:
            raise("Can't find document footer.")

    else:
        raise Exception("Can't find document header.")

    text_dict = {
        "header": header_text,
        "body" : speech_array,
        "footer": footer_text
    }
    return text_dict



def xml_to_polars(xml_string):
    """Parses XML of German Bundestag plenary protocols into a polars DataFrame."""

    tree = ET.parse(StringIO(xml_string))
    root = tree.getroot()

    data = []
    for rede in root.findall(".//rede"):
        
        redner = [a for a in rede.findall("p") if a.items() == [('klasse','redner')]][0]

        name = redner.find("redner").find("name")
        if name is not None:
            datum = root.attrib.get("sitzung-datum")
            wahlperioden_nr = int(root.attrib.get("wahlperiode"))
            sitzungs_nr = int(root.attrib.get("sitzung-nr"))
            fraktion = name.find("fraktion").text if name.find("fraktion") is not None else None
            titel = name.find("titel").text if name.find("titel") is not None else None
            vorname = name.find("vorname").text if name.find("vorname") is not None else None
            nachname = name.find("nachname").text if name.find("nachname") is not None else None

            rede_text = ""
            kommentare = []

            for element in rede:
                if element.tag == "p" and "klasse" in element.attrib:
                    rede_text += element.text if element.text is not None else ""
                elif element.tag == "kommentar":
                    kommentare.append(element.text)

            data.append({
                "Datum": datum,
                "WahlperiodenNr": wahlperioden_nr,
                "SitzungsNr": sitzungs_nr,
                "Fraktion": fraktion,
                "Titel": titel,
                "Vorname": vorname,
                "Nachname": nachname,
                "Rede": rede_text,
                "Kommentare": kommentare
            })

    df = pl.DataFrame(data)
    df = df.with_columns(pl.col("Datum").str.strptime(pl.Date, "%d.%m.%Y"))
    return df
