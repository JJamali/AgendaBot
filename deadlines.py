import re
import discord
from discord.ext import commands
import dateutil.parser


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

class Deadlines(commands.Cog):
    def __init__(self, db, cursor):
        self.db = db
        self.cursor = cursor

    @commands.command()
    async def hello(self, ctx):
        await ctx.send('Hello!')

    @commands.command(name='new')
    async def new_deadline(self, ctx, text):
        department, course_num, name, due_date = parse_arguments(text)

        guild_id = ctx.message.guild.id

        self.insert_deadline(guild_id, department, course_num, name, due_date)
        print('done')

    @commands.command(name='remove')
    async def remove_deadline(self, ctx, argument):
        department, course_num, name, due_date = argument.split(',')
        guild_id = ctx.message.guild.id

        self.delete_deadline(guild_id, department, course_num, name, due_date)
        print('delete done')

    def insert_deadline(self, guild_id, department, course_num, name, due_date):
        self.cursor.execute("INSERT INTO deadlines VALUES("
                            "%s, %s, %s, %s, %s"
                            ")", (guild_id, department, course_num, name, due_date))
        self.db.commit()

    @commands.command(name='get')
    async def get_before(self, ctx, date_str):
        date = dateutil.parser.parse(date_str)
        self.get_before_datetime(ctx.message.guild.id, date)

    def get_before_datetime(self, guild_id, date):
        self.cursor.execute("SELECT * FROM `deadlines` WHERE "
                            "`guild_id` = %s AND `due_date` < %s"
                            "ORDER BY `due_date` ASC",
                            (guild_id, date))
        result = self.cursor.fetchall()
        for r in result:
            print(r)
        return result

    def delete_deadline(self, guild_id, department, course_num, name, due_date):
        self.cursor.execute("DELETE FROM deadlines WHERE "
                            "guild_id = %s AND department = %s AND course_num = %s AND name = %s AND due_date=%s",
                            (guild_id, department, course_num, name, due_date))

        self.db.commit()