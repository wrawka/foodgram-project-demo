from django.contrib import admin
from django.db.models import fields
from .models import Follow


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    fields = (('user', 'following'),)
