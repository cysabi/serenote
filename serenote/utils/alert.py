import discord


class Alert(discord.Embed):

    alert_types = {
        "error": "<:error:807799799721230347>",
    }

    def __init__(self, alert_type, title: str, description: str = discord.Embed.Empty):
        super().__init__(
            color=discord.Color.blurple(),
            title=self.process_title(alert_type, title),
            description=description
        )

    @classmethod
    def process_title(cls, alert_type, title):
        return f"{cls.alert_types[alert_type]} {alert_type.capitalize()}: **{title}**"
