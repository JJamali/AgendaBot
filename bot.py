import os
import discord
import MySQLdb
from discord.ext import commands

from deadlines import Deadlines
from events import Events

@commands.command()
async def help(ctx):
    embed=discord.Embed(color=0x1bd0b2)
    embed.add_field(name="newdeadline", value="adds a deadline with: `$newdeadline [course], [name], [date]`",
                    inline=False)
    embed.add_field(name="removedeadline", value="removes a deadline with: `$removedeadline[index]`", inline=False)
    embed.add_field(name="cleardeadlines", value="clears all deadlines", inline=False)
    embed.add_field(name="listdeadlines", value="lists all deadlines", inline=False)
    embed.add_field(name="newevent", value="adds an event with: `$newevent, [title], [description], [time]`",
                    inline=False)
    embed.add_field(name="removeevent", value="removes an event with: `$removeevent[index]`", inline=False)
    embed.add_field(name="clearevents", value="clears all events", inline=False)
    embed.add_field(name="listevents", value="lists all events", inline=False)
    await ctx.send(embed=embed)

class CalendarBot(commands.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.db = MySQLdb.connect(user=os.getenv('db_user'),
                                  password=os.getenv('db_password'),
                                  host='localhost',
                                  database='deadlinedb')
        self.cursor = self.db.cursor(MySQLdb.cursors.DictCursor)

        self.add_cog(Deadlines(self, self.db, self.cursor))
        self.add_cog(Events(self, self.db, self.cursor))
        self.remove_command('help')
        self.add_command(help)
    async def on_ready(self):
        print('We have logged in as {0.user}'.format(self))


if __name__ == '__main__':
    client = CalendarBot(command_prefix='$')
    TOKEN = os.getenv('DISCORD_TOKEN')
    if TOKEN is not None:
        client.run(TOKEN)
