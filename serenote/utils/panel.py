import discord


class Panel(discord.Embed):

    @classmethod
    def from_embed(cls, embed):
        panel = Panel(
            type=embed._author['name'],
            type_icon=embed._author.get('icon_url'),
            title=embed.title,
            description=embed.description
        )
        if footer := getattr(embed, '_footer', None):
            panel.set_footer(text=footer['text'])
        return panel

    def __init__(self, type, type_icon=None, meta=None, *, title=None, description=None):
        super().__init__(color=0x2F3136, title=title, description=description)
        self.set_type(type, type_icon)
        if meta:
            self.set_meta(meta)

    def set_type(self, type, type_icon=None):
        self.set_author(name=type, **({"icon_url": type_icon} if type_icon else {}))

    def set_meta(self, meta):
        self.set_footer(text="\n".join([
            f"{key}: {self.parse_value(value)}"
            for key, value in meta.items()
        ]))
    
    @classmethod
    def parse_value(cls, value):
        if isinstance(value, (discord.User, discord.Member)):
            return '@' + value.name
        if isinstance(value, list):
            return ', '.join([cls.parse_value(v) for v in value])
        return value

    @staticmethod
    def icons(img):
        return f"https://raw.githubusercontent.com/LeptoFlare/serenote/main/static/{img}.png"
