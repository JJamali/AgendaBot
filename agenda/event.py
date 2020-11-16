class Event:
    def __init__(self, guild_id, name, description, start_date):
        self.guild_id = guild_id
        self.name = name
        self.description = description
        self.start_date = start_date

    def __str__(self):
        return f"{self.name} - {self.description}"

    def discord_format(self):
        return f"`{self.name}` {self.description} | `{self.start_date.strftime('%b %d %I:%M %p')}`"
