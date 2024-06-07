from rest_framework import serializers


class UserActivitySerializer(serializers.Serializer):
    user_id = serializers.CharField(max_length=100)
    activity_type = serializers.CharField(max_length=100)
    timestamp = serializers.DateTimeField()

