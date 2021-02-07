import discord


class Panel(discord.Embed):

    @classmethod
    def from_embed(cls, embed):
        """Convert embed into panel embed."""
        # Create a new panel embed
        panel = Panel(
            type=embed._author['name'],
            title=embed.title,
            description=embed.description
        )
        # Re-set footer of panel embed
        if footer := getattr(embed, '_footer', None):
            panel.set_footer(text=footer['text'])
        return panel

    def __init__(self, type, meta=None, *, title=None, description=None):
        super().__init__(color=0x2F3136, title=title, description=description)
        self.set_type(type)
        if meta:
            self.set_meta(meta)

    def set_meta(self, meta):
        self.set_footer(text="\n".join([
            f"{key}: {self.parse_value(value)}"
            for key, value in meta.items()
        ]))

    def set_type(self, type):
        self.set_author(name=type, icon_url=self.get_icon(type))

    def get_type(self):
        return self._author['name']

    @classmethod
    def parse_value(cls, value):
        if isinstance(value, (discord.User, discord.Member)):
            return '@' + value.name
        if isinstance(value, list):
            return ', '.join([cls.parse_value(v) for v in value])
        return value

    @staticmethod
    def get_icon(type):
        return f"https://raw.githubusercontent.com/LeptoFlare/serenote/main/static/types/{type.lower()}.png"
