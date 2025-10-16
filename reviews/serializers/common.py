from rest_framework import serializers
from django.utils import timezone
from datetime import timedelta
from ..models import Review


class ReviewSerializer(serializers.ModelSerializer):
    # """Base serializer for review model"""
    # average_rating = serializers.SerializerMethodField()
    # is_recent = serializers.SerializerMethodField()
    # time_since_posted = serializers.SerializerMethodField()

    class Meta:
        model = Review
        fields = '__all__'
        # read_only_fields = ['created_at', 'average_rating']

    # def get_average_rating(self, obj):
    #     """Calculate the average of all rating fields"""
    #     ratings = [
    #         obj.service_rating,
    #         obj.product_rating,
    #         obj.packaging_rating,
    #         obj.shipping_rating,
    #         obj.overall_rating
    #     ]
    #     return round(sum(ratings) / len(ratings), 1)

    # def get_is_recent(self, obj):
    #     """Check if review was posted within the last 7 days"""
    #     return timezone.now() - obj.created_at < timedelta(days=7)

    # def get_time_since_posted(self, obj):
    #     """Return human-readable time since posting"""
    #     delta = timezone.now() - obj.created_at

    #     if delta.days == 0:
    #         hours = delta.seconds // 3600
    #         if hours == 0:
    #             minutes = delta.seconds // 60
    #             return f"{minutes} minute{'s' if minutes != 1 else ''} ago"
    #         return f"{hours} hour{'s' if hours != 1 else ''} ago"
    #     elif delta.days < 30:
    #         return f"{delta.days} day{'s' if delta.days != 1 else ''} ago"
    #     elif delta.days < 365:
    #         months = delta.days // 30
    #         return f"{months} month{'s' if months != 1 else ''} ago"
    #     else:
    #         years = delta.days // 365
    #         return f"{years} year{'s' if years != 1 else ''} ago"
