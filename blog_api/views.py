from rest_framework import permissions,status
from django.contrib.auth.models import User
from .models import Post, Comment
from .serializers import UserSerializer, PostSerializer, CommentSerializer
from .permissions import IsAuthorOrReadOnly
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.views import APIView
from .response_helper import ResponseHelper
from django.http import JsonResponse
import sys
from datetime import datetime
from rest_framework.pagination import PageNumberPagination
import pytz

##### creating objects of helper files #####
ResponseHelper = ResponseHelper()


class PostPagination(PageNumberPagination):
    page_size = 5 
    page_size_query_param = 'page_size' 
    max_page_size = 100

class Register(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        '''
            user registration.
        '''
        try:
            required_fields = ['username', 'email', 'password']
            missing_fields = []

            # Check for missing required fields
            for field in required_fields:
                if field not in request.data:
                    missing_fields.append(field)

            if missing_fields:
                message = {
                    "message": f"Required fields missing: {', '.join(missing_fields)}",
                }
                return JsonResponse(message, safe=False, status=400)
            

            email = request.data.get('email')
            username = request.data.get('username')

            if User.objects.filter(email=email).exists():
                return JsonResponse({"message": "Email is already exists."}, status=400)

            if User.objects.filter(username=username).exists():
                return JsonResponse({"message": "Username is already exists."}, status=400)
            
            serializer = UserSerializer(data=request.data)
            
            if serializer.is_valid():
                serializer.save()
                return ResponseHelper.get_status_201("User registered successfully")
            
            return ResponseHelper.get_status_400(serializer.errors)
        
        except Exception as ex:
            template = "An exception of type {0} occurred. Arguments:\n{1!r}"
            message = template.format(type(ex).__name__, ex.args)
            print("Error on line {}".format(sys.exc_info()[-1].tb_lineno), type(ex).__name__, ex)
            error = {"data": [], "message": message}
            return JsonResponse(error, safe=False, status=500)


def get_time_ago(date_time):
    # Ensure the datetime is timezone aware
    if isinstance(date_time, str):
        # If it's a string, convert it to a datetime object
        date_time = datetime.fromisoformat(date_time.replace("Z", "+00:00"))
    
    now = datetime.now(pytz.UTC)  # Ensure the current time is in UTC for consistency
    delta = now - date_time  # Get the time difference

    if delta.days > 0:
        return f"{delta.days} days ago"
    elif delta.seconds >= 3600:
        return f"{delta.seconds // 3600} hours ago"
    elif delta.seconds >= 60:
        return f"{delta.seconds // 60} minutes ago"
    else:
        return f"{delta.seconds} seconds ago"
class PostList(APIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    authentication_classes = [JWTAuthentication]


    def get(self, request):
        '''
        get all posts from db.
        '''
        try:
            posts = Post.objects.all().order_by('-created_at')

            # Check if no posts are available
            if not posts.exists():
                return ResponseHelper.get_status_404("No post found.")
            
            paginator = PostPagination()
            result_page = paginator.paginate_queryset(posts, request)
            
            serializer = PostSerializer(result_page, many=True)

            for post in serializer.data:
                post['created_at'] = get_time_ago(post['created_at'])
                post['updated_at'] = get_time_ago(post['updated_at'])
            
            response_data = {
                "count": len(posts),
                "posts": serializer.data
            }
            return ResponseHelper.get_status_200(response_data)  
        except Exception as ex:
            template = "An exception of type {0} occurred. Arguments:\n{1!r}"
            message = template.format(type(ex).__name__, ex.args)
            print("Error on line {}".format(sys.exc_info()[-1].tb_lineno), type(ex).__name__, ex)
            error = {"data": [], "message": message}
            return JsonResponse(error, safe=False, status=500)

    def post(self, request):
        '''
        Create a new post
        '''
        try:
            # Check if the user is authenticated
            if not request.user.is_authenticated:
                return ResponseHelper.get_status_401("You are not authorized.")
            
            data = request.data

            required_fields = ['title', 'content']
            missing_fields = []

            # Assign the user as the author
            data['author'] = request.user.id  

            # Check for missing required fields
            for field in required_fields:
                if field not in data:
                    missing_fields.append(field)

            if missing_fields:
                message = {
                    "message": "Missing required fields",
                    "missing_fields": missing_fields
                }
                return JsonResponse(message, safe=False, status=400)

            # Validate and create the post with comments
            serializer = PostSerializer(data=data, context={'request': request})

            if serializer.is_valid():
                serializer.save() 
                return ResponseHelper.get_status_201("Post successfully created.")
            else:
                return ResponseHelper.get_status_400(serializer.errors)
        except Exception as ex:
            template = "An exception of type {0} occurred. Arguments:\n{1!r}"
            message = template.format(type(ex).__name__, ex.args)
            print("Error on line {}".format(sys.exc_info()[-1].tb_lineno), type(ex).__name__, ex)
            error = {"data": [], "message": message}
            return JsonResponse(error, safe=False, status=500)
        
class PostDetail(APIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get(self, request, pk):
        '''
        Fetch a specific post by id.
        '''
        try:
            try:
                post = Post.objects.get(id=pk)
            except Post.DoesNotExist:
                return ResponseHelper.get_status_404("No post found with the provided ID.")

            serializer = PostSerializer(post)

            post_data = serializer.data
            post_data['created_at'] = get_time_ago(post_data['created_at'])
            post_data['updated_at'] = get_time_ago(post_data['updated_at'])

            response_data = {
                "message": "Data Found",
                "data": post_data
            }
            return JsonResponse(response_data, safe=False, status=200)

        except Exception as ex:
            template = "An exception of type {0} occurred. Arguments:\n{1!r}"
            message = template.format(type(ex).__name__, ex.args)
            print("Error on line {}".format(sys.exc_info()[-1].tb_lineno), type(ex).__name__, ex)
            error = {"data": [], "message": message}
            return JsonResponse(error, safe=False, status=500)

    def put(self, request, pk):
        '''
        Update an existing post by id.
        '''
        try:
            try:
                post = Post.objects.get(id=pk)
            except Post.DoesNotExist:
                return ResponseHelper.get_status_404("No post found with the provided ID.")
            

            if not request.user.is_authenticated:
                return ResponseHelper.get_status_401("You are not authorized.")
            

            if post.author != request.user:
                return ResponseHelper.get_status_401("You are not the author of this post.")
            

            serializer = PostSerializer(post, data=request.data)

            if serializer.is_valid():
                serializer.save()
                return ResponseHelper.get_status_200("Post successfully updated.!")
            else:
                return ResponseHelper.get_status_400(serializer.errors)

        except Exception as ex:
            template = "An exception of type {0} occurred. Arguments:\n{1!r}"
            message = template.format(type(ex).__name__, ex.args)
            print("Error on line {}".format(sys.exc_info()[-1].tb_lineno), type(ex).__name__, ex)
            error = {"data": [], "message": message}
            return JsonResponse(error, safe=False, status=500)

    def delete(self, request, pk):
        '''
        Delete a specific post by id.
        '''
        try:
            try:
                post = Post.objects.get(id=pk)
            except Post.DoesNotExist:
                return ResponseHelper.get_status_404("No post found with the provided ID.")

            if not request.user.is_authenticated:
                return ResponseHelper.get_status_401("You are not authorized.")

            if post.author != request.user:
                return ResponseHelper.get_status_401("You are not the author of this post.")
            
            post.delete()
            return ResponseHelper.get_status_200("Post successfully deleted.")
        
        except Exception as ex:
            template = "An exception of type {0} occurred. Arguments:\n{1!r}"
            message = template.format(type(ex).__name__, ex.args)
            print("Error on line {}".format(sys.exc_info()[-1].tb_lineno), type(ex).__name__, ex)
            error = {"data": [], "message": message}
            return JsonResponse(error, safe=False, status=500)

class CommentList(APIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get(self, request, pk):
        '''
        Fetch all comments for a specific post
        '''
        try:
            try:
                post = Post.objects.get(id=pk)
            except Post.DoesNotExist:
                return ResponseHelper.get_status_404("No post found with the provided ID.")
            
            # Get all comments related to this post
            comments = post.comments.all()

            # Serialize the comments
            serializer = CommentSerializer(comments, many=True)
            return ResponseHelper.get_status_200(serializer.data)

        except Exception as ex:
            template = "An exception of type {0} occurred. Arguments:\n{1!r}"
            message = template.format(type(ex).__name__, ex.args)
            print("Error on line {}".format(sys.exc_info()[-1].tb_lineno), type(ex).__name__, ex)
            error = {"data": [], "message": message}
            return JsonResponse(error, safe=False, status=500)

    def post(self, request, pk):
        '''
        Create a new comment for a specific post
        '''
        try:
            try:
                post = Post.objects.get(id=pk)
            except Post.DoesNotExist:
                return ResponseHelper.get_status_404("No post found with the provided ID.")

            # Ensure the user is authenticated
            if not request.user.is_authenticated:
                return ResponseHelper.get_status_401("You are not authorized.")

            # Add the post ID and author ID to the request data
            data = request.data
            data['post'] = post.id
            data['author'] = request.user.id    

            # Validate and create the comment
            serializer = CommentSerializer(data=data, context={'request': request})
            if serializer.is_valid():
                serializer.save()  # Save the new comment in the database
                return ResponseHelper.get_status_201("Comment successfully created!")
            else:
                return ResponseHelper.get_status_400(serializer.errors)
        except Exception as ex:
            message = {"error": str(ex)}
            return JsonResponse(message, safe=False, status=500)