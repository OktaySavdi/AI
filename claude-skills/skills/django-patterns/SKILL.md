---
name: "django-patterns"
description: >
  Django patterns: models, views, serializers, ORM best practices, signals,
  and clean architecture. Activate for Django development work.
metadata:
  version: 1.0.0
  category: engineering
---

# Django Patterns Skill

## Models

```python
from django.db import models
import uuid

class User(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "users"
        indexes = [models.Index(fields=["email"])]
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return self.email
```

## Managers and QuerySets

```python
class ActiveUserManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_active=True)

class User(models.Model):
    objects = models.Manager()
    active = ActiveUserManager()

# Usage
active_users = User.active.select_related("profile").prefetch_related("orders")
```

## Views with Django REST Framework

```python
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response

class UserViewSet(viewsets.ModelViewSet):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return User.objects.filter(is_active=True).select_related("profile")

    @action(detail=True, methods=["post"])
    def deactivate(self, request, pk=None):
        user = self.get_object()
        user.is_active = False
        user.save(update_fields=["is_active"])
        return Response(status=status.HTTP_204_NO_CONTENT)
```

## Serializers

```python
from rest_framework import serializers

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "email", "name", "created_at"]
        read_only_fields = ["id", "created_at"]

    def validate_email(self, value: str) -> str:
        if User.objects.filter(email=value).exclude(pk=self.instance.pk if self.instance else None).exists():
            raise serializers.ValidationError("Email already in use.")
        return value.lower()
```

## Service Layer (avoid fat models/views)

```python
# services/user_service.py
from django.db import transaction

class UserService:
    @staticmethod
    @transaction.atomic
    def create_user(email: str, name: str) -> User:
        user = User.objects.create(email=email.lower(), name=name)
        Profile.objects.create(user=user)
        send_welcome_email.delay(user.id)  # Celery task
        return user
```

## N+1 Prevention

```python
# WRONG — N queries for related data
users = User.objects.all()
for user in users:
    print(user.profile.bio)  # N+1 query

# CORRECT
users = User.objects.select_related("profile").all()
users = User.objects.prefetch_related("orders").all()
```

## Settings Structure

```python
# settings/base.py → settings/local.py → settings/production.py
# Use django-environ for environment variables
import environ
env = environ.Env()
DEBUG = env.bool("DEBUG", default=False)
DATABASES = {"default": env.db("DATABASE_URL")}
SECRET_KEY = env.str("SECRET_KEY")
```
