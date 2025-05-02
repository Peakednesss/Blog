# from django.shortcuts import render, HttpResponse
#
# # Create your views here.
#
# # blog/views.py
# from rest_framework import generics, permissions
# from .models import Article, UserInfo
# from .serializers import ArticleSerializer, UserInfoSerializer
# from rest_framework import viewsets
#
#
# class ArticleListCreateView(generics.ListCreateAPIView):
#     queryset = Article.objects.all()
#     serializer_class = ArticleSerializer
#     permission_classes = [permissions.IsAuthenticatedOrReadOnly]
#
#     def perform_create(self, serializer):
#         serializer.save(author=self.request.user)
#
#
# class UserViewSet(viewsets.ModelViewSet):
#     queryset = UserInfo.objects.all()
#     serializer_class = UserInfoSerializer
#
#
# # def index(request):
# #     return render(request, "index.html")
#
#
from rest_framework import generics, permissions, viewsets, status
from rest_framework.exceptions import ValidationError

from .models import Article, User, Category, Tag, Comment
from .serializers import ArticleSerializer, UserSerializer, CategorySerializer, TagSerializer, CommentSerializer

from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.core.files.storage import FileSystemStorage

from rest_framework.views import APIView

from rest_framework.permissions import AllowAny
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
import logging


# 文章列表和创建视图
class ArticleListCreateView(generics.ListCreateAPIView):
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        # 自动将当前登录用户设置为文章作者
        serializer.save(author=self.request.user)


# 预定义泛型视图，其实什么都不用配置（好像）
class ArticleDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer


class UserArticleListView(generics.ListAPIView):
    serializer_class = ArticleSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        user_id = self.kwargs['pk']
        return Article.objects.filter(author__id=user_id)


# 用户视图集
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAdminUser]  # 仅管理员可管理用户


# 分类视图集
class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


# 标签视图集
class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


# 评论视图集
class CommentViewSet(viewsets.ModelViewSet):
    # queryset = Comment.objects.select_related('article', 'user').all()
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        user_id = self.kwargs['pk']
        return Comment.objects.filter(article_id=user_id)

    def perform_create(self, serializer):
        article = serializer.validated_data['article']
        if not Article.objects.filter(id=article.id).exists():
            raise ValidationError("文章不存在")
        serializer.save(user=self.request.user,
                        article_id=self.request.data.get('article')
                        )

    # def get_permissions(self):
    #     if self.action in ['update', 'destroy']:
    #         return [IsCommentAuthor()]
    #     return super().get_permissions()


@api_view(['POST'])
@permission_classes([AllowAny])  # 新增权限豁免
def register(request):
    serializer = UserSerializer(data=request.data, context={'request': request})
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


logger = logging.getLogger(__name__)


# APIView是基础层视图，需要手动返回值
class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, format=None):
        username = request.data.get('username')
        password = request.data.get('password')

        logger.debug(f"Received login request for username: {username}, password: {password}")

        if not username or not password:
            logger.error("Username and password are required")
            return Response({'detail': 'Username and password are required'}, status=400)

        user = authenticate(username=username, password=password)
        if user is not None:
            logger.debug(f"认证用户真实ID: {user.id}")  # 输出到日志
            refresh = RefreshToken.for_user(user)
            user_data = UserSerializer(user).data
            # logger.info(f"Authentication successful for user: {username}")
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'user': user_data,
            }, status=200)
        else:
            logger.warning(f"Authentication failed for user: {username}")
            return Response({'detail': 'Invalid credentials'}, status=401)


