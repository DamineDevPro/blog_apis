from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Post, Comment
from .validation import validate_unique_email


# this serializer for user model 
class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)  
    email = serializers.EmailField(required=True)
    username = serializers.CharField(required=True)
    
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password')


    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email'),
            password=validated_data['password']
        )
        return user


# this serializer for Comment model 
class CommentSerializer(serializers.ModelSerializer):
    author = serializers.ReadOnlyField(source='author.username')
    post = serializers.PrimaryKeyRelatedField(queryset=Post.objects.all(), write_only=True)

    class Meta:
        model = Comment
        fields = ('id', 'post', 'author', 'content', 'created_at')

    def create(self, validated_data):
        post = validated_data.get('post')  
        content = validated_data.get('content')  
        author = self.context['request'].user  

        comment = Comment.objects.create(post=post, content=content, author=author)
        return comment


# this serializer for post model 
class PostSerializer(serializers.ModelSerializer):
    author = serializers.ReadOnlyField(source='author.username')
    comments = CommentSerializer(many=True, read_only=True)

    class Meta:
        model = Post
        fields = ('id', 'title', 'content', 'author', 'created_at', 'updated_at', 'comments')

        

    def create(self, validated_data):
        post = Post.objects.create(title=validated_data['title'],
            content=validated_data.get('content'),
            author=self.context['request'].user,
            )
        return post