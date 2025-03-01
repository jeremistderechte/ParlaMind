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

    df_parla = __clean_df(df_parla)

    df_politician = get_politician_df()

    df_parla = df_parla.join(
        df_politician,
        left_on=["firstName", "lastName"],
        right_on=["first_name", "last_name"],
        how="left",
    )

    df_parla = df_parla.with_columns(
        pl.when(pl.col("abbreviation").is_null())
        .then(pl.col("Partei"))
        .otherwise(pl.col("abbreviation"))
        .alias("partei_aktualisiert")
    )

    df_parla = df_parla.drop(["abbreviation", "Name", "Partei"])

    df_parla = df_parla.rename({"partei_aktualisiert": "abbreviation"})

    df_parla = df_parla.sort("date")

    if save:
        Path("./data/formated/parquet/").mkdir(parents=True, exist_ok=True)
        df_parla.write_parquet("./data/formated/parquet/ParlaMind.parquet")

    return df_parla


def get_politician_df():
    politiker_liste = politiker = [
        "Johann Saathoff (SPD)",
        "Caren Marks (SPD)",
        "Andreas Scheuer (CSU)",
        "Carsten Schneider (SPD)",
        "Marco Buschmann (FDP)",
        "Klaus Holetschek (CSU)",
        "Thomas Strobl (CDU)",
        "Sven Schulze (CDU)",
        "Boris Pistorius (SPD)",
        "Anne Spiegel (Grüne)",
        "Christian Lange (SPD)",
        "Eva Högl (SPD)",
        "Stephan Weil (SPD)",
        "Andreas Bovenschulte (SPD)",
        "Florian Pronold (SPD)",
        "Siemtje Möller (SPD)",
        "Thomas Schmidt (CDU)",
        "Horst Seehofer (CSU)",
        "Günter Krings (CDU)",
        "Benjamin Strasser (FDP)",
        "Dieter Janecek (Grüne)",
        "Reiner Haseloff (CDU)",
        "Helge Braun (CDU)",
        "Nancy Faeser (SPD)",
        "Olaf Scholz (SPD)",
        "Peter Tauber (CDU)",
        "Anna Lührmann (Grüne)",
        "Dorothee Bär (CSU)",
        "Anna Christmann (Grüne)",
        "Rita Hagl-Kehl (SPD)",
        "Wolfgang Schmidt (SPD)",
        "Armin Schuster (CDU)",
        "Steffen Bilger (CDU)",
        "Kerstin Griese (SPD)",
        "Luise Amtsberg (Grüne)",
        "Jan-Niclas Gesenhues (Grüne)",
        "Hubertus Heil (SPD)",
        "Stephan Mayer (CSU)",
        "Oliver Krischer (Grüne)",
        "Cem Özdemir (Grüne)",
        "Annette Widmann-Mauz (CDU)",
        "Enak Ferlemann (CDU)",
        "Daniela Behrens (SPD)",
        "Bettina Hoffmann (Grüne)",
        "Bettina Stark-Watzinger (FDP)",
        "Julia Klöckner (CDU)",
        "Karl Lauterbach (SPD)",
        "Franziska Giffey (SPD)",
        "Tobias Lindner (Grüne)",
        "Judith Gerlach (CSU)",
        "Claudia Müller (Grüne)",
        "Anke Rehlinger (SPD)",
        "Angela Merkel (CDU)",
        "Ekin Deligöz (Grüne)",
        "Michelle Müntefering (SPD)",
        "Mahmut Özdemir (SPD)",
        "Christian Lindner (FDP)",
        "Joachim Stamp (FDP)",
        "Jens Spahn (CDU)",
        "Burkhard Blienert (SPD)",
        "Thomas Hitschler (SPD)",
        "Pascal Kober (FDP)",
        "Robert Habeck (Grüne)",
        "Heiko Maas (SPD)",
        "Michael Müller (SPD)",
        "Steffi Lemke (Grüne)",
        "Florian Toncar (FDP)",
        "Franziska Brantner (Grüne)",
        "Armin Laschet (CDU)",
        "Katja Kipping (Die Linke)",
        "Bettina Jarasch (Grüne)",
        "Peter Altmaier (CDU)",
        "Markus Söder (CSU)",
        "Cansel Kiziltepe (SPD)",
        "Christine Lambrecht (SPD)",
        "Sören Bartol (SPD)",
        "Roman Poseck (CDU)",
        "Felix Klein (parteilos)",
        "Katja Hessel (FDP)",
        "Mario Brandenburg (FDP)",
        "Edgar Franke (SPD)",
        "Thomas Gebhart (CDU)",
        "Lena Kreck (Die Linke)",
        "Gerd Müller (CSU)",
        "Reem Alabali-Radovan (SPD)",
        "Bodo Ramelow (Die Linke)",
        "Michael Kellner (Grüne)",
        "Jörg Steinbach (SPD)",
        "Sven Lehmann (Grüne)",
        "Annegret Kramp-Karrenbauer (CDU)",
        "Daniela Kluckert (FDP)",
        "Marion Gentges (CDU)",
        "Mehmet Daimagüler (parteilos)",
        "Oliver Luksic (FDP)",
        "Felor Badenberg (parteilos)",
        "Bärbel Kofler (SPD)",
        "Claudia Roth (Grüne)",
        "Rita Schwarzelühr-Sutter (SPD)",
        "Peter Beuth (CDU)",
        "Volker Wissing (FDP)",
        "Jörg Kukies (SPD)",
        "Christian Pegel (SPD)",
        "Peter Tschentscher (SPD)",
        "Alexander Schweitzer (SPD)",
        "Maria Flachsbarth (CDU)",
        "Malu Dreyer (SPD)",
        "Sarah Ryglewski (SPD)",
        "Anja Karliczek (CDU)",
        "Annalena Baerbock (Grüne)",
        "Sabine Dittmar (SPD)",
        "Christian Kühn (Grüne)",
        "Ophelia Nick (Grüne)",
        "Katja Keul (Grüne)",
        "Elisabeth Winkelmeier-Becker (CDU)",
        "Kristina Sinemus (parteilos)",
        "Natalie Pawlik (SPD)",
        "Karl-Josef Laumann (CDU)",
        "Thomas Silberhorn (CSU)",
        "Klara Geywitz (SPD)",
        "Boris Rhein (CDU)",
        "Elisabeth Kaiser (SPD)",
        "Lisa Paus (Grüne)",
        "Thomas Bareiß (CDU)",
        "Bettina Hagedorn (SPD)",
        "Niels Annen (SPD)",
        "Michael Roth (SPD)",
        "Dietmar Woidke (SPD)",
        "Anette Kramme (SPD)",
        "Andreas Pinkwart (FDP)",
        "Uli Grötsch (SPD)",
        "Michael Theurer (FDP)",
        "Svenja Schulze (SPD)",
        "Monika Grütters (CDU)",
        "Jens Brandenburg (FDP)",
        "Ingmar Jung (CDU)",
    ]

    namen = []
    first_names = []
    last_names = []
    parteien = []

    party_translation = {
        "AFD": "AfD",
        "BSW": "BSW",  # No clear equivalent
        "BÜNDNIS\xa090/DIEGRÜNEN": "Grüne",
        "Grüne": "Grüne",
        "CDU/CSU": "CDU/CSU",
        "CSU": "CDU/CSU",
        "CDU": "CDU/CSU",
        "DIELINKE": "DIE LINKE.",
        "Linke": "DIE LINKE.",
        "FDP": "FDP",
        "FRAKTIONSLOS": "Fraktionslos",
        "parteilos": "Fraktionslos",
        None: None,  # Represents missing or unspecified data
        "SPD": "SPD",
    }
    for politiker in politiker_liste:
        teile = politiker.strip().rsplit(" ", 1)
        name = teile[0]
        first_name = name.split()[0]
        last_name = name.split()[1]
        partei = party_translation[teile[1].strip("()")]

        namen.append(name)
        parteien.append(partei)
        first_names.append(first_name)
        last_names.append(last_name)

    return pl.DataFrame(
        {
            "Name": namen,
            "first_name": first_names,
            "last_name": last_names,
            "Partei": parteien,
        }
    )
