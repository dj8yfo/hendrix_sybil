from django.db import models

# Create your models here.

# msg1 = Message(content='message recorded', from_nym='fraa jad', room=room, order=room.messages_of.count())
# Room.objects.get_or_create(title='Boogy')[0].messages_of.count()
# Room.objects.get_or_create(title='Lobby')[0].messages_of.filter(order__lt=3).order_by('order')


class Room(models.Model):
    title = models.CharField(max_length=60, unique=True)


class Message(models.Model):
    content = models.TextField()
    from_nym = models.CharField(max_length=100)
    date_created = models.DateTimeField(auto_now_add=True)


class MessageOrder(models.Model):
    room = models.ForeignKey(Room, related_name='messages_of',
                             on_delete=models.CASCADE)
    message = models.OneToOneField(Message, related_name='order_of',
                                   on_delete=models.CASCADE)
    order = models.IntegerField(db_index=True, default=0)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['room', 'order'],
                                    name='unique_order_in_room')
        ]
