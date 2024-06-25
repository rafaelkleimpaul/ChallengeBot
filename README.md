# Web Scraper Bot

This is a web scraping bot developed to automate the extraction of data from the LATIMES website using Selenium and RPA (Robotic Process Automation). The bot opens the website, performs a search based on provided terms, selects specific topics, sorts the results by the newest, extracts relevant information, and saves the data in an Excel file.

## Project Structure

- `scraper.py`: Main bot code.
- `properties.json`: Configuration file containing URL, search term, topics, number of months for the search, and delay between actions.
- `output/`: Directory where logs, images, and results will be saved.

## Requirements

- Python 3.7+
- Python libraries listed in `requirements.txt`

## Installation

1. Clone the repository:
    ```bash
    git clone https://github.com/rafaelkleimpaul/RPAFreshNews
    cd RPAFreshNews
    ```

2. Install the dependencies:
    ```bash
    pip install -r requirements.txt
    ```

## Configuration

Edit the `properties.json` file to adjust the parameters according to your needs:

```json
{
    "URL": "https://www.latimes.com/",
    "SEARCH_PHRASE": "your search term",
    "TOPIC": ["topic1", "topic2"],
    "NUMBER_OF_MONTHS": 3,
    "DELAY": 2
}
```
## Usage

To run the bot, use the following command:

```
python scraper.py

```
The bot will:

1 - Open the specified URL.
2 - Perform a search with the provided term.
3 - Select the specified topics.
4 - Sort the results by "newest".
5 - Extract data (date, title, description, image name, count of search terms, whether the title contains monetary amounts, whether the description contains monetary amounts).
6 - Save the results in an Excel file in the output/ folder.

## LOGS
Activity logs of the bot will be saved in output/LATIMES_*.log.

## Directory Structure
Ensure your directory structure is organized as follows:
```
RPAFreshNews/
│
├── output/
│   └── (logs, images, and Excel files will be saved here)
│
├── scraper.py
├── properties.json
├── requirements.txt
└── README.md
```
