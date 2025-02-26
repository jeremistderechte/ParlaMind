import polars as pl
import pandas as pd
from ParlaMind.src import FileReader
from pathlib import Path


def __clean_string(el):
    if el is None:
        return None
    return el.replace(" ", "").replace("\n", "").replace("\t", "").upper()


def __clean_df(df_parla: pl.DataFrame) -> pl.DataFrame:
    df_parla = df_parla.with_columns(
        pl.col("speechContent")
        .map_elements(lambda x: x.strip(), return_dtype=pl.String)
        .alias("speechContent"),
    )

    return df_parla.filter(df_parla["speechContent"].str.len_chars() >= 40)


def get_open_discourse() -> pl.DataFrame:
    df_speeches = pl.read_csv("./data/raw/OpenDiscourse/speeches.csv")
    df_factions = pl.read_csv("./data/raw/OpenDiscourse/factions.csv")

    df_parla = df_speeches.join(
        df_factions, left_on="factionId", right_on="id", how="inner"
    )

    df_parla = df_parla.filter(pl.col("abbreviation") != "not found")

    return df_parla.select(
        "firstName", "lastName", "speechContent", "date", "abbreviation", "full_name"
    )


def concat_od_with_xml(df_parla: pl.dataframe, save: bool) -> pl.DataFrame:

    df_xml = FileReader.put_all_xmls_into_one_df("./data/raw/XML")
    df_xml = df_xml.drop(["WahlperiodenNr", "SitzungsNr", "Titel", "Kommentare"])

    df_xml_pd = df_xml.to_pandas()

    df_temp = df_xml_pd.loc[df_xml_pd["Fraktion"] == "SPDCDU/CSU"]
    df_temp["Vorname"] = "Alexander"
    df_temp["Nachname"] = "Föhr"
    df_temp["Fraktion"] = "CDU/CSU"

    df_xml_pd = df_xml_pd.loc[df_xml_pd["Fraktion"] != "SPDCDU/CSU"]

    df_parla_partys = set(list(df_parla["abbreviation"].value_counts()["abbreviation"]))
    df_xml_partys = set(list(df_xml_pd["Fraktion"].apply(lambda s: __clean_string(s))))

    party_translation = {
        "AFD": "AfD",
        "BSW": "BSW",  # No clear equivalent
        "BÜNDNIS\xa090/DIEGRÜNEN": "Grüne",
        "CDU/CSU": "CDU/CSU",
        "DIELINKE": "DIE LINKE.",
        "FDP": "FDP",
        "FRAKTIONSLOS": "Fraktionslos",
        None: None,  # Represents missing or unspecified data
        "SPD": "SPD",
    }

    df_xml_pd["Fraktion"] = df_xml_pd["Fraktion"].apply(lambda s: __clean_string(s))
    df_xml_pd["Fraktion"] = df_xml_pd["Fraktion"].apply(lambda s: party_translation[s])

    df_temp["Datum"] = pd.to_datetime(df_temp["Datum"], format="%d.%m.%Y").dt.strftime(
        "%Y-%m-%d"
    )

    df_xml_pd["Datum"] = pd.to_datetime(
        df_xml_pd["Datum"], format="%d.%m.%Y"
    ).dt.strftime("%Y-%m-%d")

    df_xml_pd = pd.concat([df_xml_pd, df_temp])
    df_xml = pl.from_pandas(df_xml_pd)

    try:
        df_xml = df_xml.drop(["__index_level_0__"])
    except:
        pass

    rename_dict = {
        "Datum": "date",
        "Fraktion": "abbreviation",
        "Vorname": "firstName",
        "Nachname": "lastName",
        "Rede": "speechContent",
    }

    # Rename the columns
    df_xml = df_xml.rename(rename_dict)

    try:
        df_parla = df_parla.drop(["full_name"])
        df_xml = df_xml.drop(["__index_level_0__"])
    except:
        pass

    # Sort columns alphabetically
    sorted_columns = sorted(df_xml.columns)  # Get sorted column names
    df_xml = df_xml.select(sorted_columns)  # Reorder columns in DataFrame

    # Sort columns alphabetically
    sorted_columns = sorted(df_parla.columns)  # Get sorted column names
    df_parla = df_parla.select(sorted_columns)  # Reorder columns in DataFrame

    df_parla = pl.concat([df_xml, df_parla]).unique()

    if save:
        Path("./data/formated/parquet/").mkdir(parents=True, exist_ok=True)
        df_parla.write_parquet("ParlaMind.parquet")

    df_parla = __clean_df(df_parla)

    return df_parla.sort("date")
