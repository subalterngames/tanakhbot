import re
from json import dumps
from pathlib import Path
from requests import get
from tqdm import tqdm

"""
Scrape Sefaria for the Tanakh.

I used this to create `tanakhbot/data/tanakh.json`

You don't need to run this unless you want a different translation or if someone adds/removes a book in the Tanakh.

To run this, you may need to install requests: pip install requests
"""


class Bible:
    def __init__(self, name: str):
        self.name: str = name
        self.url_name: str = name.replace(" ", "_")


def remove_html(v) -> str:
    """
    Strip a verse of all HTML tags. They're only extant in the Dead Sea Scrolls anyway.

    :param v: The verse.

    :return: The edited verse.
    """

    v0 = v[:]
    # Remove a footnote asterisk.
    v = re.sub("<sup (.*?)>(.*?)</sup>", "", v)
    # Remove the footnote text. The JPS translation has a lot of these.
    v = re.sub('<i class="footnote">(.*?)</i>', "", v)
    # Replace br
    v = v.replace("<br>", "\n")
    v = re.sub(clean, "", v)
    assert "<" not in v, v0
    return v


api_prefix = "http://www.sefaria.org/api/"
clean = re.compile('<.*?>')
books = ["Genesis", "Exodus", "Leviticus", "Numbers", "Deuteronomy", "Joshua", "Judges", "I Samuel", "II Samuel",
         "I Kings", "II Kings", "Isaiah", "Jeremiah", "Ezekiel", "Hosea", "Joel", "Amos", "Obadiah", "Jonah", "Micah",
         "Nahum", "Habakkuk", "Zephaniah", "Haggai", "Zechariah", "Malachi", "Psalms", "Proverbs", "Job",
         "Song of Songs", "Ruth", "Lamentations", "Ecclesiastes", "Esther", "Daniel", "Ezra", "Nehemiah",
         "I Chronicles", "II Chronicles"]

# The translations. Change these to use a different translation. See the Sefaria API for how to find translation titles.
koren: Bible = Bible(name="The Koren Jerusalem Bible")
# There are multiple JPS versions. Different ones are used for different texts.
jps_versions = [Bible(name="THE JPS TANAKH: Gender-Sensitive Edition"),
                Bible(name="The Contemporary Torah, Jewish Publication Society, 2006"),
                Bible(name="Tanakh: The Holy Scriptures, published by JPS")]
tanakh = dict()
pbar = tqdm(total=len(books))
# Iterate through each book in the Tanakh,
for book in books:
    pbar.set_description(book)
    tanakh[book] = dict()
    # Get the book's index data.
    index = get(f"{api_prefix}index/{book}").json()
    # Get the number of chapters and verses.
    lengths = index["schema"]["lengths"]
    # Iterate through each chapter in the book.
    for chapter in range(lengths[0]):
        tanakh[book][chapter] = list()
        book_chapter = f"{api_prefix}texts/{book}.{chapter + 1}"
        # Get the translation text.
        chapter_koren = get(f"{book_chapter}/en/{koren.url_name}").json()["text"]
        # Try to find a valid JPS translation.
        jps_ok = False
        chapter_jps = list()
        jps_name = ""
        for jps in jps_versions:
            chapter_jps = get(f"{book_chapter}/en/{jps.url_name}").json()["text"]
            if len(chapter_jps) > 0:
                jps_name = jps.name
                jps_ok = True
                break
        # Get the Hebrew.
        chapter_he = get(f"{book_chapter}").json()["he"]
        # This seems to only happen with Isaiah 66.
        if jps_ok and len(chapter_jps) != len(chapter_he):
            chapter_he = chapter_he[:len(chapter_jps)]
        # Iterate through each verse in the chapter.
        for i in range(len(chapter_he)):
            # Get each verse and remove HTML.
            verse_koren = remove_html(chapter_koren[i])
            verse_jps = remove_html(chapter_jps[i]) if jps_ok else ""
            verse_he = remove_html(chapter_he[i])
            # Remember the verse.
            verse = {"koren": verse_koren,
                     "jps": verse_jps,
                     "jps_version": jps_name,
                     "jps_ok": jps_ok,
                     "he": verse_he}
            tanakh[book][chapter].append(verse)
    pbar.update(1)
# Write to disk.
Path("./tanakhbot/data/tanakh.json").resolve().write_text(dumps(tanakh))
