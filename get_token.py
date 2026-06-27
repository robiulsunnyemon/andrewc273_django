
import os
import django
import sys
sys.path.append('d:\\andrew273\\new\\andrewc273-django')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'projects.settings')
django.setup()

from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()
user = User.objects.filter(email="admin@gmail.com").first()
if not user:
    user = User.objects.first()

refresh = RefreshToken.for_user(user)
print("TOKEN:", str(refresh.access_token))
