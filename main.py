from ParlaMind.src import FileReader

if __name__ == "__main__":
    text = FileReader.extract_text_from_pdf("./ParlaMind/src/20211.pdf")
    df = FileReader.text_to_polars(text)
    print(df)
