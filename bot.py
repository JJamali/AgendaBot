import os
import discord
import MySQLdb
from discord.ext import commands

from deadlines import Deadlines


class CalendarBot(commands.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.db = MySQLdb.connect(user=os.getenv('db_user'),
                                  password=os.getenv('db_password'),
                                  host='localhost',
                                  database='deadlinedb')
        self.cursor = self.db.cursor(MySQLdb.cursors.DictCursor)

        self.add_cog(Deadlines(self, self.db, self.cursor))

    async def on_ready(self):
        print('We have logged in as {0.user}'.format(self))


if __name__ == '__main__':
    client = CalendarBot(command_prefix='$')
    TOKEN = os.getenv('DISCORD_TOKEN')
    if TOKEN is not None:
        client.run(TOKEN)
