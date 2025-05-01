from django.contrib import admin
from .models import User, Article, Comment

admin.site.register(User)
admin.site.register(Article)
admin.site.register(Comment)

