from ParlaMind.src import FileReader

if __name__ == "__main__":
    """text = FileReader.extract_text_from_pdf("./ParlaMind/src/20211.pdf")
    with open("textdump.txt", "w") as file:
        file.write(text)
    df = FileReader.text_to_polars(text)
    df.write_csv("temp.csv")
    print(df.select("speech").head(1))"""

    # Set paths for the PDF folder and the output JSON file
    folder_path = r"C:\Users\I569776\Desktop\uni\NLP\GIT\ParlaMind\XML Files"
    output_json_path = "extracted_data.json"

    # FileReader.write_all_to_txt(folder_path)

    # Run the extraction and export process
    # FileReader.extract_pdf_data_and_export_to_json(folder_path, output_json_path)

    # with open("./xml.xml", "r", encoding="utf-8") as f:  # Encoding is important
    #    xml_string = f.read()

    # df = FileReader.xml_to_polars(xml_string)

    df = FileReader.put_all_xmls_into_one_df(folder_path)
    print(df)
