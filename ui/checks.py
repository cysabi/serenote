"""Contains checks used for filtering replies."""


def msg(mem, channel):
    """Check if the message is in the same channel, and is by the same author."""
    return lambda m: \
        m.channel.id == channel.id and m.author.id == mem.id and \
        not m.content.startswith("\\")  # User wants to escape the bot


def react(mem, message, valids=None):
    """Check if the reaction is on the correct message, and is by the same author."""
    return lambda r, u: \
        (r.message.id, u.id) == (message.id, mem.id) and \
        (r.emoji in valids if valids else r.emoji != '❌') and \
        (isinstance(r.emoji, str))


def member(mem):
    """Check if the member who joined or leaved is the same as the member specified."""
    return lambda m: m.id == mem.id
