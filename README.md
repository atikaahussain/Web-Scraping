# YouTube Web Scraper

This Python script uses Selenium to automate searching on YouTube and scrape both main video results and their recommended videos.

## Features

- Automatically performs a YouTube search for a given keyword.
- Scrapes information about the top N main videos:
  - Title,Channel name,View count,Video age,Video URL
- For each main video, scrapes details of the right-hand side recommended videos.
- Stores recommended videos in a formatted text file (`recommended_videos.txt`).


## Requirements

- Python 3.x
- Google Chrome browser
- ChromeDriver (compatible with your version of Chrome)

## Installation

1. Clone this repository or download the `youtube_scraper.py` file.

2. Install required Python package:

```bash
pip install selenium
