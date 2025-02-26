import urllib.request
import json
from datetime import datetime
from tqdm import tqdm
import re
from config import settings

# Retrieve from https://dip.bundestag.de/%C3%BCber-dip/hilfe/api
API_KEY = settings.api_key


def download_data(format: str, start_year: int) -> None:
    """Downloads the plenarprotokolle via the API"""

    documents_per_json = 100  # limit from api

    today = datetime.today()
    current_year = today.year

    url = f"https://search.dip.bundestag.de/api/v1/plenarprotokoll?f.zuordnung=BT&f.datum.start={start_year}-01-01&f.datum.end={current_year}-12-31&apikey={API_KEY}"

    urllib.request.urlretrieve(url, "reden.json")

    with open("reden.json") as f:
        d = json.load(f)

    total_documents = d["numFound"]

    years_since_founding = current_year - start_year

    with tqdm(total=total_documents) as pbar:

        for i in range(years_since_founding + 1):
            url = f"https://search.dip.bundestag.de/api/v1/plenarprotokoll?f.zuordnung=BT&f.datum.start={start_year+i}-01-01&f.datum.end={start_year+i}-12-31&apikey={API_KEY}"

            urllib.request.urlretrieve(url, "reden.json")

            with open("reden.json") as f:
                d = json.load(f)

            for i in range(documents_per_json):
                try:
                    document = d["documents"][i]["fundstelle"]
                except IndexError:
                    break
                date = document["datum"]
                try:
                    url_pdf = document["pdf_url"]
                    url_xml = re.sub(".pdf", ".xml", url_pdf)
                except KeyError:
                    print(f"Skipped data from {date}")
                    pbar.update(1)
                    break
                try:
                    if format.upper() == "XML":
                        urllib.request.urlretrieve(url_xml, f"./data/speech-{date}.xml")
                    elif format.upper() == "PDF":
                        urllib.request.urlretrieve(url_pdf, f"./data/speech-{date}.pdf")
                except urllib.error.HTTPError:
                    print(f"Skipped data from {date}")
                pbar.update(1)


download_data()
