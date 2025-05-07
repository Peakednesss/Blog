

# Create your models here.
# blog/models.py

from django.contrib.auth.models import AbstractUser
from django.db import models

from djangoProject import settings


class User(AbstractUser):

    avatar = models.ImageField(upload_to='', null=True, blank=True)
    bio = models.TextField(blank=True)

    class Meta:
        db_table = 'blog_user'

    # 添加 related_name 参数，避免冲突
    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name='groups',
        blank=True,
        help_text='The groups this user belongs to.',
        related_name="blog_user_set",  # 自定义反向访问器名称
        related_query_name="blog_user",  # 将user 修改为blog_user
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name='user permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        related_name="blog_user_set",  # 自定义反向访问器名称
        related_query_name="blog_user",  # 将user 修改为blog_user
    )


class Message(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='messages')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}: {self.content[:20]}"


class Article(models.Model):
    STATUS_CHOICES = [
        ('draft', '草稿'),
        ('published', '已发布'),
        ('deleted', '已删除'),
    ]
    title = models.CharField(max_length=255)
    content = models.TextField()
    summary = models.CharField(max_length=500, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    views = models.IntegerField(default=0)
    likes = models.IntegerField(default=0)
    top_flag = models.BooleanField(default=False)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='articles', verbose_name='作者')
    categories = models.ManyToManyField('Category', related_name='articles', blank=True)
    tags = models.ManyToManyField('Tag', related_name='articles', blank=True)

    def __str__(self):
        return self.title


class Category(models.Model):
    name = models.CharField(max_length=100)
    alias = models.SlugField(unique=True)  # 用于URL路径
    description = models.TextField(blank=True)
    parent = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='children'
    )

    def __str__(self):
        return self.name


class Tag(models.Model):
    name = models.CharField(max_length=100)
    alias = models.SlugField(unique=True)  # 用于URL路径
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


class Comment(models.Model):
    article = models.ForeignKey(
        Article,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True,
                                      verbose_name='创建时间'
                                      )
    parent = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='replies'
    )
    likes = models.IntegerField(default=0)
    STATUS_CHOICES = [
        ('pending', '待审核'),
        ('approved', '已通过'),
        ('deleted', '已删除'),
    ]
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )

    def __str__(self):
        return f"Comment by {self.user.username} on {self.article.title}"





