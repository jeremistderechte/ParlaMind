# ParlaMind

ParlaMind is a project that analyzes speeches from the German Bundestag from **1949 to 2025**. It applies advanced **Natural Language Processing (NLP)** techniques to extract insights from political discourse, including **sentiment analysis, topic modeling, and speaker classification** using **BERT**.

<img src="https://media2.giphy.com/media/v1.Y2lkPTc5MGI3NjExYmxiYWszc2Z5YXRndmhrejMzMHV6MThhNHNsNGV2YnBkNnZtcmo1dSZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/bsx3TKhzktWhB8Ivjf/giphy.gif" width="300"/>

## To-do
- Distanz von Parteien ueber Zeit (timon)
- Beginn mit 2005 bei textgen und classification (jeremy)
- topic model (timon)

## Features
- **Sentiment Analysis**: Determines the sentiment (positive, neutral, or negative) of speeches.
- **Topic Modeling**: Identifies key themes and trends over time.
- **Speaker Classification**: Uses **BERT** to classify and attribute speeches to specific politicians.
- **Historical Insights**: Tracks linguistic and ideological changes across decades.

## Technologies Used
- **Python** (Core language)
- **PyTorch & Hugging Face Transformers** (For BERT-based NLP tasks)
- **Polars & Pandas** (For data processing)
- **Poetry** (For dependency management)

## Installation
```sh
poetry install
```

## Usage
### Running Analysis
To analyze speeches, run:
```sh
poetry run python main.py --task sentiment
```
Other tasks:
- `--task topic-modeling`
- `--task speaker-classification`

### Dataset
The dataset consists of Bundestag speeches from 1949–2025, preprocessed and stored in parquet format.
