import os
import discord
from discord.ext import commands

from deadlines import Deadlines


class CalendarBot(commands.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.add_cog(Deadlines())

    async def on_ready(self):
        print('We have logged in as {0.user}'.format(self))


if __name__ == '__main__':
    client = CalendarBot(command_prefix='$')
    TOKEN = os.getenv('DISCORD_TOKEN')
    if TOKEN is not None:
        client.run(TOKEN)
