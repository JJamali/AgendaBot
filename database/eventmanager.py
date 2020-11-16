import re
import asyncio

import discord
from discord.ext import commands, tasks
from discord.ext.commands import has_permissions
import dateutil.parser
import datetime

from agenda.event import Event


def format_event(event):
    return f"`{event['name']}` {event['description']} | " \
           f"`{event['start_date'].strftime('%b %d %I:%M %p')}`"


def parse_arguments(text):
    name, description, start_date = [arg.strip() for arg in text.split(',')]

    start_date = dateutil.parser.parse(start_date)
    start_date = str(start_date)

    return name, description, start_date


class EventManager:
    def __init__(self, db, cursor):
        self.db = db
        self.cursor = cursor

        self.announce_channels = []
        # self.summarize.start()

    def insert_event(self, e: Event):
        self.cursor.execute(
            "INSERT INTO events (guild_id, name, Description, start_date) VALUES("
            "%s, %s, %s, %s)",
            (e.guild_id, e.name, e.description, e.start_date))
        self.db.commit()

    def delete_event(self, e: Event):
        self.cursor.execute("DELETE FROM events WHERE "
                            "guild_id = %s AND name = %s AND start_date = %s"
                            "LIMIT 1",
                            (e.guild_id, e.name, e.start_date))

        self.db.commit()

    def clear_event(self, guild_id):
        self.cursor.execute("DELETE FROM events WHERE `guild_id` = %s",
                            (guild_id,))
        self.db.commit()

    def get_all_events(self, guild_id):
        """Returns all upcoming events"""
        self.cursor.execute("SELECT * FROM `events` WHERE "
                            "`guild_id` = %s AND `start_date` > %s "
                            "ORDER BY `start_date` ASC",
                            (guild_id, datetime.datetime.now()))
        return [Event(**kwargs) for kwargs in self.cursor.fetchall()]
