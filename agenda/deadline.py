class Deadline:
    def __init__(self, guild_id, department, course_num, name, due_date):
        self.guild_id = guild_id
        self.department = department
        self.course_num = course_num
        self.name = name
        self.due_date = due_date

    def __str__(self):
        return f'{self.department}{self.course_num} - {self.name}'

    def discord_format(self):
        return f"`{self.department}{self.course_num}` {self.name} | " \
               f"`{self.due_date.strftime('%b %d %I:%M %p')}`"
