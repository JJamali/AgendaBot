import discord
from discord.ext import commands
import datetime


def get_weekday(due_date):
    weekdays = ("Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday")
    return weekdays[due_date.weekday()]


class Deadlines(commands.Cog):
    def __init__(self, db, cursor):
        self.db = db
        self.cursor = cursor

    @commands.command()
    async def hello(self, ctx):
        await ctx.send('Hello!')

    @commands.command(name='new')
    async def new_deadline(self, ctx, argument):
        print(argument)
        department, course_num, name, due_date = argument.split(',')
        guild_id = ctx.message.guild.id

        self.insert_deadline(guild_id, department, course_num, name, due_date)
        print('done')

    def insert_deadline(self, guild_id, department, course_num, name, due_date):
        self.cursor.execute("INSERT INTO deadlines VALUES("
                            "%s, %s, %s, %s, %s"
                            ")", (guild_id, department, course_num, name, due_date))
        self.db.commit()


    @commands.command(name='test')
    async def test(self, ctx):
        dates = [datetime.datetime(2020,11,16), datetime.datetime(2020,11,17),datetime.datetime(2020,11,17)]
        deadlines = [{"department":"dep", "course_num":i, "name":i*i, "due_date":date} for i, date in enumerate(dates)]
        await self.send_calendar(ctx, deadlines)



    async def send_calendar(self, ctx, deadlines):
        guild = ctx.message.guild.name
        message = []
        current_day = None

        message.append("**{0} important dates** :calendar_spiral:\n".format(guild))
        for idx, deadline in enumerate(deadlines):
            new_day = deadline["due_date"]
            if current_day != new_day:
                message.append('__')
                message.append(get_weekday(deadline["due_date"]))
                message.append('__')
                current_day = new_day

            generalMsg = "> {}{} — {:<10}\t\t\t ".format(deadline["department"], deadline["course_num"], deadline["name"], deadline["due_date"])
            due = "    *Due:{}*".format(deadline["due_date"])

            message.append(generalMsg)
            message.append((30 - len(generalMsg)) * " " + due)
        await ctx.send('\n'.join(message))