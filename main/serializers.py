from rest_framework import serializers

class ApplicationSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField()
    resume = serializers.FileField()
    applicant__username = serializers.CharField()
    applied_on = serializers.DateTimeField()