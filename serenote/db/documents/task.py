"""Contains Task database model."""

import mongoengine as me


class Task(me.Document):
    """Task database model."""

    message_id = me.IntField(required=True)
    channel_id = me.IntField(required=True)
    author_id = me.IntField(required=True)

    assignee_ids = me.ListField(me.IntField(), default=list)
    assigned_role_ids = me.ListField(me.IntField(), default=list)
