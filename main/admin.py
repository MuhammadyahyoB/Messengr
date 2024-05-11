from django.contrib import admin
from . import models

admin.site.register(models.User)
admin.site.register(models.Group)
admin.site.register(models.GroupUsers)
admin.site.register(models.UserImage)
admin.site.register(models.Message)
admin.site.register(models.MessageFiles)
admin.site.register(models.GroupJoinedRequest)