# # blog/urls.py
from django.conf.urls.static import static
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from djangoProject import settings
from .views import (
    ArticleListCreateView,
    UserViewSet,
    CategoryViewSet,
    TagViewSet,
    CommentViewSet,
    register,
    LoginView,
    ArticleDetailView,
    UserArticleListView
)

# 创建一个路由器实例
router = DefaultRouter()

# 注册视图集到路由器
router.register(r'users', UserViewSet)           # 用户相关 API
router.register(r'categories', CategoryViewSet)  # 分类相关 API
router.register(r'tags', TagViewSet)            # 标签相关 API
# router.register(r'comments', CommentViewSet, basename='comment')

# 配置 URL 模式
urlpatterns = [
    path("articles/", ArticleListCreateView.as_view(), name="article-list-create"),  # 文章列表和创建接口

    path('articles/<int:pk>/', ArticleDetailView.as_view(), name='article-detail'),

    path('users/<int:pk>/articles/', UserArticleListView.as_view(), name='user-article-list'),  # 新增的路由

    path('comments/<int:pk>/', CommentViewSet.as_view({'get': 'list'}), name='comment'),

    path('comments/', CommentViewSet.as_view({'post': 'create'}), name='comment'),

    # path('users/<string:pk>/', UserViewSet.as_view({'get': 'retrieve'}), name='user-list'),


    path("register/", register, name="register"),
    path("login/", LoginView.as_view(), name="login"),
    path('', include(router.urls)),  # 包含 DRF 自动生成的路由


]
# if settings.DEBUG:
#     # 将 /media/ 开头的请求映射到 avatars 目录
#     urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)  # [1,6](@ref)


