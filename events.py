import re
import asyncio

import discord
from discord.ext import commands, tasks
from discord.ext.commands import has_permissions
import dateutil.parser
import datetime

def format_event(event):
    return f"`{event['name']} {event['description']}`" \
    f"`{event['start_date'].strftime('%b %b %p')}`"

def parse_arguments(text):
    name, description, start_date = [arg.strip() for arg in text.split(',')]

    start_date = dateutil.parser.parse(start_date)
    start_date = str(start_date)

    return name, description, start_date


class Events(commands.Cog):
    def __init__(self, bot, db, cursor):
        self.bot = bot
        self.db = db
        self.cursor = cursor

        self.announce_channels = []
        #self.summarize.start()

    @has_permissions(administrator=True)
    @commands.command(name='newevent')
    async def new_event(self, ctx, *, text):
        name, description, start_date = parse_arguments(text)

        guild_id = ctx.message.guild.id

        self.insert_event(guild_id, name, description, start_date)
        await ctx.send("{} {} added to events :sunglasses:".format(name, start_date))

        print('done')

    @has_permissions(administrator=True)
    @commands.command(name='removeevent')
    async def remove_event(self, ctx, idx: int):
        if idx < 0:
            await ctx.send("Your index is out of range, please try again")
            return
        try:
            event = self.get_all_events(ctx.message.guild.id)[idx]
        except IndexError:
            await ctx.send("Your index is out of range, please try again")
            return

        self.delete_event(**event)
        await ctx.send("{} {} removed from events :triumph:".format(event["name"], event["start_date"]))
        print('delete done')

    @commands.command(name='clearevents')
    @has_permissions(administrator=True)
    async def clear_all_event(self, ctx):
        self.clear_event(ctx.guild.id)
        await ctx.send("Removed all events")

    def insert_event(self, guild_id, name, description, start_date):
        self.cursor.execute("INSERT INTO events (guild_id, name, Description, start_date) VALUES("
                            "%s, %s, %s, %s"
                            ")", (guild_id, name, description, start_date))
        self.db.commit()

    def delete_event(self, guild_id, name, description, start_date):
        self.cursor.execute("DELETE FROM events WHERE "
                            "guild_id = %s AND name = %s AND start_date = %s"
                            "LIMIT 1",
                            (guild_id, name, start_date))

        self.db.commit()

    def clear_event(self, guild_id):
        self.cursor.execute("DELETE FROM events WHERE `guild_id` = %s", (guild_id,))
        self.db.commit()

    @commands.command(name='listevents')
    async def list_all_events(self, ctx):
        events = self.get_all_events(ctx.message.guild.id)
        embed = discord.Embed(title='Upcoming Events', color=0xdc1e1e)
        if not events:
            embed.description = "There are no existing events"
        else:
            lines = []
            for idx, event in enumerate(events):
                lines.append(f'`{idx}.` {format_event(event)}')
            embed.description = '\n'.join(lines)
        await ctx.send(embed=embed)

    def get_all_events(self, guild_id):
        """Returns all upcoming events"""
        self.cursor.execute("SELECT * FROM `events` WHERE "
                            "`guild_id` = %s AND `start_date` > %s "
                            "ORDER BY `start_date` ASC",
                            (guild_id, datetime.datetime.now()))
        return self.cursor.fetchall()
