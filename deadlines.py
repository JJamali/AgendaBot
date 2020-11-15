import re
import asyncio

import discord
from discord.ext import commands, tasks
from discord.ext.commands import has_permissions
import dateutil.parser
import datetime


def format_deadline(deadline):
    return f"{deadline['department']}-{deadline['course_num']} {deadline['name']}\t\t" \
           f"due" \
           f" {deadline['due_date'].strftime('%b %d %I:%M %p')}"


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


class Deadlines(commands.Cog):
    def __init__(self, bot, db, cursor):
        self.bot = bot
        self.db = db
        self.cursor = cursor

        self.announce_channels = []
        self.summarize.start()

    @has_permissions(administrator=True)
    @commands.command(name='new')
    async def new_deadline(self, ctx, text):
        department, course_num, name, due_date = parse_arguments(text)

        guild_id = ctx.message.guild.id

        self.insert_deadline(guild_id, department, course_num, name, due_date)
        await ctx.send("{} {} {} added to deadlines :sunglasses:".format(department, course_num, name))

        print('done')

    @has_permissions(administrator=True)
    @commands.command(name='remove')
    async def remove_deadline(self, ctx, idx: int):
        if idx < 0:
            await ctx.send("Your index is out of range, please try again")
            return
        try:
            deadline = self.get_all_deadlines(ctx.message.guild.id)[idx]
        except IndexError:
            await ctx.send("Your index is out of range, please try again")
            return

        self.delete_deadline(**deadline)
        await ctx.send("{} {} {} removed from deadlines :triumph:".format(deadline["department"], deadline["course_num"], deadline["name"]))
        print('delete done')

    @commands.command(name='clear')
    @has_permissions(administrator=True)
    async def clear_all_deadlines(self, ctx):
        self.clear_deadline(ctx.guild.id)
        await ctx.send("Removed All Deadlines")

    def insert_deadline(self, guild_id, department, course_num, name, due_date):
        self.cursor.execute("INSERT INTO deadlines VALUES("
                            "%s, %s, %s, %s, %s"
                            ")", (guild_id, department, course_num, name, due_date))
        self.db.commit()

    def delete_deadline(self, guild_id, department, course_num, name, due_date):
        self.cursor.execute("DELETE FROM deadlines WHERE "
                            "guild_id = %s AND department = %s AND course_num = %s AND name = %s AND due_date=%s "
                            "LIMIT 1",
                            (guild_id, department, course_num, name, due_date))

        self.db.commit()

    def clear_deadline(self, guild_id):
        self.cursor.execute("DELETE FROM deadlines WHERE `guild_id` = %s", (guild_id,))
        self.db.commit()

    def get_before_datetime(self, guild_id, date):
        self.cursor.execute("SELECT * FROM `deadlines` WHERE "
                            "`guild_id` = %s AND `due_date` < %s AND $s < `due_date` "
                            "ORDER BY `due_date` ASC",
                            (guild_id, date, datetime.datetime.now()))
        result = self.cursor.fetchall()
        return result

    @commands.command(name='list')
    async def list_all_deadlines(self, ctx):
        deadlines = self.get_all_deadlines(ctx.message.guild.id)
        message = []
        for idx, deadline in enumerate(deadlines):
            message.append(f"{idx} - {format_deadline(deadline)}")

        if message:
            await ctx.send('\n'.join(message))
        else:
            await ctx.send("There are no Deadlines")

    def get_all_deadlines(self, guild_id):
        """Returns all upcoming deadlines"""
        self.cursor.execute("SELECT * FROM `deadlines` WHERE " 
                            "`guild_id` = %s AND `due_date` > %s "
                            "ORDER BY `due_date` ASC",
                            (guild_id, datetime.datetime.now()))
        return self.cursor.fetchall()

    async def send_calendar(self, ctx, guild, deadlines):
        message = []
        current_day = None

        message.append("**{0} important dates** :calendar_spiral:".format(guild))
        for idx, deadline in enumerate(deadlines):
            new_day = deadline["due_date"]
            if current_day != new_day:
                message.append(f'\n__{get_weekday(deadline["due_date"])}__')
                current_day = new_day

            """
            generalMsg = "> {}{} — {:<10}\t\t\t ".format(deadline["department"], deadline["course_num"], deadline["name"], deadline["due_date"])
            due = "    *Due:{}*".format(deadline["due_date"])

            message.append(generalMsg)
            message.append((30 - len(generalMsg)) * " " + due)
            """
            generalMsg = format_deadline(deadline)
            message.append(generalMsg)
        await ctx.send('\n'.join(message))

    async def send_events(self, ctx, deadlines):
        guild = ctx.message.guild.name
        message = []
        message.append("**{0} events** :rocket: \n".format(guild))
        message.append("{}: {} - {}".format())

    @tasks.loop(hours=24)
    async def summarize(self):
        """Print upcoming events each day"""
        self.announce_channels = [discord.utils.get(guild.channels, name='announcements')
                                  for guild in self.bot.guilds]

        for channel in self.announce_channels:
            guild_id = channel.guild.id
            deadlines = self.get_all_deadlines(guild_id)
            await self.send_calendar(channel, channel.guild, deadlines)

    @summarize.before_loop
    async def before_summarize(self):
        """Wait until midnight to begin summarize loop"""
        await self.bot.wait_until_ready()

        # calculate seconds to midnight
        t = datetime.datetime.today()
        future = datetime.datetime(t.year, t.month, t.day, 8, 0)
        if future <= t:
            future += datetime.timedelta(days=1)
        seconds_to_midnight = (future - t).total_seconds()

        print(f'waiting {seconds_to_midnight} seconds until starting summary loop')
        await asyncio.sleep(seconds_to_midnight)
