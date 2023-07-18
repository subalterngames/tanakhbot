from json import loads
from typing import List
from datetime import datetime
from random import randint
from pathlib import Path
from pkg_resources import resource_filename

jps_abbrvs = {"THE JPS TANAKH: Gender-Sensitive Edition": "Gender-Sensitive Edition",
              "Tanakh: The Holy Scriptures, published by JPS": "The Holy Scriptures",
              "The Contemporary Torah, Jewish Publication Society, 2006": "The Contemporary Torah"}


class Verse:
    def __init__(self):
        # Get the Tanakh.
        tanakh: dict = loads(Path(resource_filename(__name__, "data/tanakh.json")).read_text())
        # Get today.
        today = datetime.today()
        # Get a random book.
        books: List[str] = list(tanakh.keys())
        book: str = books[randint(0, len(books) - 1)]
        # Get a random chapter.
        chapters: List[str] = list(tanakh[book].keys())
        chapter: str = chapters[randint(0, len(chapters) - 1)]
        # Get a random verse.
        verses = tanakh[book][chapter]
        verse_number = randint(0, len(verses) - 1)
        verse = verses[verse_number]
        citation = f"**{book} {chapter}:{verse_number}**"
        # Log the citation.
        self.log: str = f"{today}: {citation}"
        # Get the URL.
        url: str = f"https://www.sefaria.org/{book}.{chapter}.{verse_number}?lang=bi&aliyot=0".replace(" ", "_")
        # Get the summary.
        jps = verse['jps']
        koren = verse['koren']
        self.summary: str = f"{citation}: {jps}\n"
        # Assemble the text.
        self.text: str = f"{citation}\n\n{verse['he']}\n\n**Koren:** {koren}\n\n**JPS:** *({jps_abbrvs[verse['jps_version']]})* {verse['jps']}\n\n{url}"


if __name__ == "__main__":
    for i in range(100):
        v = Verse()
        print(v.log)
        print(v.summary)
        print(v.text)
        print("####")
