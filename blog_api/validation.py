
from django.contrib.auth.models import User
from django.http import JsonResponse

def validate_unique_email(value):
    """check  emial if the email is unique"""

    if User.objects.filter(email=value).exists():
        message = {
                    "message": "This email is already exists.",
                }
        return JsonResponse(message, safe=False, status=409)
    
    return value
