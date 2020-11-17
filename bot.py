import os
import discord
import MySQLdb
from discord.ext import commands

from agenda.agendacog import AgendaCog


class MyHelpCommand(commands.HelpCommand):
    def __init__(self, **options):
        super().__init__(**options)

    async def send_bot_help(self, mapping):
        dest = self.get_destination()
        ctx = self.context
        bot = ctx.bot

        help_filtered = (
            filter(lambda c: c.name != "help", bot.commands)
            if len(bot.commands) > 1
            else bot.commands
        )

        filtered = await self.filter_commands(help_filtered, sort=True)

        embed = discord.Embed(color=0x1bd0b2)
        for command in filtered:
            if isinstance(command, commands.Group):
                for subcommand in command.commands:
                    print(subcommand.short_doc)
                    text = subcommand.short_doc if subcommand.short_doc else "Nothing"
                    embed.add_field(name=subcommand.qualified_name, value=text, inline=False)

        await dest.send(embed=embed)


class CalendarBot(commands.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, help_command=MyHelpCommand(), **kwargs)
        self.db = MySQLdb.connect(user=os.getenv('db_user'),
                                  password=os.getenv('db_password'),
                                  host='localhost',
                                  database='deadlinedb')
        self.cursor = self.db.cursor(MySQLdb.cursors.DictCursor)

        self.add_cog(AgendaCog(self, self.db, self.cursor))

    async def on_ready(self):
        print('We have logged in as {0.user}'.format(self))


bot = CalendarBot(command_prefix='$')


TOKEN = os.getenv('DISCORD_TOKEN')
if TOKEN is not None:
    bot.run(TOKEN)
