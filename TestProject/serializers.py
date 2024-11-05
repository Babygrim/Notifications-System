from math import floor
from django.utils.timezone import now
from rest_framework import serializers

class CustomDateTimeField(serializers.DateTimeField):
    def to_representation(self, value):
        current_datetime = now()
        object_added_datetime = value
        time_difference = current_datetime - object_added_datetime
        minutes = floor(time_difference.total_seconds() / 60)
        hours = floor(minutes / 60)
        days = floor(hours / 24)
        years = floor(days / 365)
        
        return f'{years} year(s) ago' if years > 0 else f'{days} day(s) ago' if days > 0 else f'{hours} hour(s) ago' if hours > 0 else f'{minutes} minute(s) ago' if minutes > 0 else 'Just now'
