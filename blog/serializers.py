from django.core.files.storage import FileSystemStorage
from rest_framework import serializers
from .models import User, Article, Category, Tag, Comment


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = [
            'id', 'username', 'first_name', 'last_name', 'email', 'password', 'avatar', 'bio'
        ]
        read_only_fields = []

    def create(self, validated_data):
        # Remove the password from validated_data and set it separately
        password = validated_data.pop('password')
        user = super().create(validated_data)
        user.set_password(password)
        user.is_active = True

        # Handle file upload
        if 'avatar' in self.context['request'].FILES:
            avatar_file = self.context['request'].FILES['avatar']
            # fs = FileSystemStorage(location='avatars/')
            # filename = fs.save(avatar_file.name, avatar_file)
            # uploaded_file_url = fs.url(filename)
            user.avatar = avatar_file
        user.save()

        return user


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'alias', 'description']


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name', 'alias', 'description']


class ArticleSerializer(serializers.ModelSerializer):
    # author = serializers.StringRelatedField()  # 显示用户名
    author = UserSerializer(read_only=True)
    categories = CategorySerializer(many=True, read_only=True)
    tags = TagSerializer(many=True, read_only=True)

    class Meta:
        model = Article
        fields = [
            'id', 'title', 'content', 'summary', 'created_at', 'updated_at',
            'published_at', 'status', 'views', 'likes', 'top_flag', 'author',
            'categories', 'tags'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'views', 'likes']


class RecursiveField(serializers.Serializer):
    """递归字段，用于嵌套评论"""
    def to_representation(self, value):
        serializer = self.parent.parent.__class__(value, context=self.context)
        return serializer.data


class CommentSerializer(serializers.ModelSerializer):
    # user = serializers.StringRelatedField()  # 显示用户名
    user = UserSerializer(read_only=True)
    replies = RecursiveField(many=True, read_only=True)

    parent = serializers.PrimaryKeyRelatedField(
        queryset=Comment.objects.all(),
        required=False,
        allow_null=True
    )

    class Meta:
        model = Comment
        fields = [
            'id', 'article', 'user', 'content', 'created_at', 'parent',
            'likes', 'replies'
        ]
        read_only_fields = ['id', 'created_at', 'likes', 'status']

    # def get_replies(self, obj):
    #     return CommentSerializer(
    #         obj.replies.all(),
    #         many=True,
    #         context=self.context
    #     ).data

