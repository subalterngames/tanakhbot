from pathlib import Path
from os import getcwd
from datetime import datetime
import discord
from tanakhbot.verse import Verse


class Bot(discord.Client):
    """
    Post a random Tanakh verse every day.
    """

    SUMMARY_PATH = Path("./summary.txt")

    def __init__(self, channel: int, logging: bool = True, ):
        """
        :param channel: The ID of the channel.
        :param logging: If True, log messages.
        """

        self.channel: int = int(channel)
        self.logging: bool = logging
        self.summarize: bool = datetime.today().weekday() == 6
        super().__init__()

    async def on_ready(self):
        # Connect to the Discord channel.
        channel = self.get_channel(self.channel)
        text = self.get_summary() if self.summarize else self.get_verse()
        # Split the text into posts of <= 2000 characters.
        posts = [text[index: index + 2000] for index in range(0, len(text), 2000)]
        try:
            # Post.
            for post in posts:
                await channel.send(post)
            # Quit.
            await self.close()
        except Exception as e:
            self.log(str(e))

    def log(self, message: str) -> None:
        """
        Log a message.

        :param message: The message.
        """

        if self.logging:
            with Path(getcwd()).joinpath("log.txt").open("at") as f:
                f.write(message + "\n")

    def get_summary(self) -> str:
        """
        :return: The summary text.
        """

        today = datetime.today()
        self.log(f"{today}: summary")
        summary = Bot.SUMMARY_PATH.read_text(encoding="utf-8").strip()
        # Clear the summary.
        Bot.SUMMARY_PATH.write_text("")
        return summary

    def get_verse(self) -> str:
        """
        :return: A random Tanakh verse.
        """

        # Get the Tanakh.
        verse: Verse = Verse()
        # Write the log.
        self.log(message=verse.log)
        # Write the summary.
        with Bot.SUMMARY_PATH.open("at") as f:
            f.write(verse.summary)
        return verse.text
