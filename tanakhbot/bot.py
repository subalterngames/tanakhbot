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
        self.summarize: bool = datetime.today().weekday() == 4
        super().__init__()

    async def on_ready(self):
        # Connect to the Discord channel.
        channel = await self.fetch_channel(self.channel)
        if self.summarize:
            text = "**Friday Round-Up**\n\n" \
                   "It's Friday! Here are all the verses we've seen this week. We invite you to engage with the round-up by responding in writing or in art to any of these prompts:\n\n" \
                   "- What resonances do you see among the verses?\n" \
                   "- Imagine these verses are meant to go together. What story would they tell?\n" \
                   "- What resonances do you see among the verses?\n\n" + self.get_summary()
        else:
            text = "**Pasuk A Day**\n\n" \
                   "Hi, I'm TanakhBot! Every day except Saturday I post one random verse from the Torah, Prophets, or Writings (Tanakh). On Friday I'll post all 5 verses from this week. We invite you to engage with each verse by responding in writing or in art to any of these prompts:\n\n" \
                   "- What surprises or calls out to you in this verse?\n" \
                   "- What questions do you have about this verse?\n" \
                   "- How is this verse making you feel today?\n\n" + self.get_verse()
        # Split the text into posts of <= 2000 characters.
        posts = [text[index: index + 2000] for index in range(0, len(text), 2000)]
        try:
            # Post.
            for post in posts:
                await channel.send(post)
                if self.logging:
                    self.log(post)
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
