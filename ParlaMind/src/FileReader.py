import PyPDF2


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
