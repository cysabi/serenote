import mongoengine as me
me.connect('serenote', host='db')

from .documents.task import Task


def get_task(message_id):
    return Task.objects(message_id=message_id).first()
