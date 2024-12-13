from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView
from . import views

urlpatterns = [
    path('register/', views.Register.as_view(), name='register'), # manage new user registration
    path('login/', TokenObtainPairView.as_view(), name='login'), # login user and get token 
    path('posts/', views.PostList.as_view(), name='post-list'), # all posts and handles new post creation
    path('posts/<int:pk>/', views.PostDetail.as_view(), name='post-detail'), # retrieving, updating, and deleting specific post
    path('posts/<int:pk>/comments/', views.CommentList.as_view(), name='comment-list'), # manage comments for a specific post
]