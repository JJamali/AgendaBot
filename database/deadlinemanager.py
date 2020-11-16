import datetime
from typing import List
from agenda.deadline import Deadline


class DeadlineManager:
    def __init__(self, db, cursor):
        self.db = db
        self.cursor = cursor

    def insert_deadline(self, d: Deadline):
        self.cursor.execute("INSERT INTO deadlines VALUES("
                            "%s, %s, %s, %s, %s"
                            ")", (d.guild_id, d.department, d.course_num, d.name, d.due_date))
        self.db.commit()

    def delete_deadline(self, d: Deadline):
        self.cursor.execute("DELETE FROM deadlines WHERE "
                            "guild_id = %s AND department = %s AND course_num = %s AND name = %s AND due_date=%s "
                            "LIMIT 1",
                            (d.guild_id, d.department, d.course_num, d.name, d.due_date))
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
        return Deadline(**result)

    def get_all_deadlines(self, guild_id) -> List[Deadline]:
        """Returns all upcoming deadlines"""
        self.cursor.execute("SELECT * FROM `deadlines` WHERE "
                            "`guild_id` = %s AND `due_date` > %s "
                            "ORDER BY `due_date` ASC",
                            (guild_id, datetime.datetime.now()))
        deadlines = [Deadline(**kwargs) for kwargs in self.cursor.fetchall()]
        return deadlines
