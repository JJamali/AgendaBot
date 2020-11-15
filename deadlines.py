import discord
from discord.ext import commands


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

    def delete_deadline(self, guild_id, department, course_num, name, due_date):
        self.cursor.execute("DELETE FROM deadlines WHERE "
                            "guild_id = %s AND department = %s AND course_num = %s AND name = %s AND due_date=%s",
                            (guild_id, department, course_num, name, due_date))

        self.db.commit()