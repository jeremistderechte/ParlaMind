import PyPDF2
import polars as pl
import re


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
