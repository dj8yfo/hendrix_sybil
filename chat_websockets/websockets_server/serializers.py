from rest_framework import serializers
from .models import Message


class ChatMessageSerializer(serializers.ModelSerializer):
    room = serializers.SerializerMethodField()
    date_created = serializers.SerializerMethodField()
    seq = serializers.SerializerMethodField()

    class Meta:
        model = Message
        fields = ['content', 'from_nym', 'date_created', 'room', 'seq']

    def get_date_created(self, instance):
        return instance.date_created.timestamp()

    def get_room(self, instance):
        return instance.order_of.room.title

    def get_seq(self, instance):
        return instance.order_of.order
