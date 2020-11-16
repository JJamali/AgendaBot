import re
import asyncio
import datetime
from typing import List

import discord
from discord.ext import commands, tasks
from discord.ext.commands import has_permissions
import dateutil.parser

from agenda.deadline import Deadline
from agenda.event import Event
from database import eventmanager, deadlinemanager


def format_deadline(deadline):
    return f"`{deadline['department']}{deadline['course_num']}` {deadline['name']} | " \
           f"`{deadline['due_date'].strftime('%b %d %I:%M %p')}`"


def parse_course_code(course_code):
    """Separates the course department and number"""
    pattern = r"([A-Za-z]+)[\s\-\_]?(\w+)"
    match = re.search(pattern, course_code)
    return match.group(1).upper(), match.group(2)


def parse_arguments(text):
    course_code, name, due_date = [arg.strip() for arg in text.split(',')]

    department, course_num = parse_course_code(course_code)

    due_date = dateutil.parser.parse(due_date)
    due_date = str(due_date)

    return department, course_num, name, due_date


def get_weekday(due_date):
    weekdays = ("Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday")
    return weekdays[due_date.weekday()]


class AgendaCog(commands.Cog):
    def __init__(self, bot, db, cursor):
        self.bot = bot
        self.db = db
        self.cursor = cursor

        self.d_manager = deadlinemanager.DeadlineManager(db, cursor)
        self.e_manager = eventmanager.EventManager(db, cursor)

        self.announce_channels = []
        self.summarize.start()

    @commands.group()
    async def new(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send('Invalid new command passed...')

    @commands.group()
    async def remove(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send('Invalid remove command passed...')

    @commands.group()
    async def clear(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send('Invalid clear command passed...')

    @commands.group()
    async def list(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send('Invalid list command passed...')

    # ------- Deadline commands -------
    @has_permissions(administrator=True)
    @new.command(name='deadline')
    async def new_deadline(self, ctx, *, text):
        department, course_num, name, due_date = parse_arguments(text)
        guild_id = ctx.message.guild.id

        deadline = Deadline(guild_id, department, course_num, name, due_date)

        self.d_manager.insert_deadline(deadline)
        await ctx.send(f"{deadline} added to deadlines :sunglasses:")

    @new_deadline.error
    async def new_deadline_error(self, ctx, error):
        print(error)
        await ctx.send("Error creating deadline")

    @has_permissions(administrator=True)
    @remove.command(name='deadline')
    async def remove_deadline(self, ctx, idx: int):
        if idx < 0:
            raise IndexError
        deadline = self.d_manager.get_all_deadlines(ctx.message.guild.id)[idx]
        self.d_manager.delete_deadline(deadline)
        await ctx.send(f"{deadline} removed from deadlines :triumph:")

    @remove_deadline.error
    async def remove_deadline_error(self, ctx, error):
        print(error)
        await ctx.send("Error removing deadline")

    @has_permissions(administrator=True)
    @clear.command(name='deadlines')
    async def clear_all_deadlines(self, ctx):
        self.d_manager.clear_deadline(ctx.guild.id)
        await ctx.send("Removed All Deadlines")

    @list.command(name='deadlines')
    async def list_all_deadlines(self, ctx):
        deadlines = self.d_manager.get_all_deadlines(ctx.message.guild.id)
        embed = discord.Embed(title='Upcoming Due Dates', color=0xdc1e1e)
        if not deadlines:
            embed.description = "There are no existing due dates :smile:"
        else:
            lines = []
            for idx, deadline in enumerate(deadlines):
                lines.append(f"`{idx}.` {deadline.discord_format()}")
            embed.description = '\n'.join(lines)
        await ctx.send(embed=embed)

    # ------- Event commands -------
    @has_permissions(administrator=True)
    @new.command(name='event')
    async def new_event(self, ctx, *, text):
        name, description, start_date = eventmanager.parse_arguments(text)
        guild_id = ctx.message.guild.id

        event = Event(guild_id, name, description, start_date)

        self.e_manager.insert_event(event)
        await ctx.send(f"{event} added to events :sunglasses:")

    @new_event.error
    async def new_event_error(self, ctx, error):
        print(error)
        await ctx.send("Error creating event")

    @has_permissions(administrator=True)
    @remove.command(name='event')
    async def remove_event(self, ctx, idx: int):
        if idx < 0:
            raise IndexError()
        event = self.e_manager.get_all_events(ctx.message.guild.id)[idx]

        self.e_manager.delete_event(event)
        await ctx.send(
            f"{event} removed from events :triumph:")

    @remove_event.error
    async def remove_event_error(self, ctx, error):
        await ctx.send("Error removing event")

    @clear.command(name='events')
    @has_permissions(administrator=True)
    async def clear_all_event(self, ctx):
        self.e_manager.clear_event(ctx.guild.id)
        await ctx.send("Removed all events")

    @list.command(name='events')
    async def list_all_events(self, ctx):
        events = self.e_manager.get_all_events(ctx.message.guild.id)
        embed = discord.Embed(title='Upcoming Events', color=0xdc1e1e)
        if not events:
            embed.description = "There are no existing events"
        else:
            lines = []
            for idx, event in enumerate(events):
                lines.append(f'`{idx}.` {event.discord_format()}')
            embed.description = '\n'.join(lines)
        await ctx.send(embed=embed)

    async def send_calendar(self, ctx, guild, deadlines: List[Deadline]):
        embed = discord.Embed(title=f':calendar_spiral: {guild}\'s upcoming due dates:', color=0xdc1e1e)
        fields = []
        current_day = None

        for idx, deadline in enumerate(deadlines):
            new_day = deadline.due_date
            if current_day != new_day:
                fields.append({"name": get_weekday(deadline.due_date), "value": []})
                current_day = new_day

            desc = deadline.discord_format()
            fields[-1]["value"].append(desc)

        for f in fields:
            embed.add_field(name=f["name"], value='\n'.join(f["value"]), inline=False)
        await ctx.send(embed=embed)

    @tasks.loop(hours=24)
    async def summarize(self):
        """Print upcoming events each day"""
        self.announce_channels = [discord.utils.get(guild.channels, name='announcements')
                                  for guild in self.bot.guilds]

        for channel in self.announce_channels:
            if channel is not None:
                guild_id = channel.guild.id
                deadlines = self.d_manager.get_all_deadlines(guild_id)
                await self.send_calendar(channel, channel.guild, deadlines)

    @summarize.before_loop
    async def before_summarize(self):
        """Wait until midnight to begin summarize loop"""
        await self.bot.wait_until_ready()

        # calculate seconds to midnight
        t = datetime.datetime.today()
        future = datetime.datetime(t.year, t.month, t.day, 7, 0)
        if future <= t:
            future += datetime.timedelta(days=1)
        seconds_to_midnight = (future - t).total_seconds()

        print(f'waiting {seconds_to_midnight} seconds until starting summary loop')
        await asyncio.sleep(seconds_to_midnight)
