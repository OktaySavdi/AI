---
name: "django-security"
description: >
  Django security best practices: CSRF, SQL injection, XSS, auth hardening,
  HTTPS settings, and secrets management. Activate for Django security review.
metadata:
  version: 1.0.0
  category: engineering
---

# Django Security Skill

## Production Security Settings

```python
# settings/production.py
DEBUG = False
SECRET_KEY = env.str("SECRET_KEY")  # never hardcode

ALLOWED_HOSTS = env.list("ALLOWED_HOSTS")

# HTTPS
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"
```

## SQL Injection Prevention

```python
# WRONG — raw SQL with interpolation
User.objects.raw(f"SELECT * FROM users WHERE email = '{email}'")

# CORRECT — parameterized
User.objects.raw("SELECT * FROM users WHERE email = %s", [email])

# BEST — ORM (handles parameterization automatically)
User.objects.filter(email=email)
```

## CSRF Protection

```python
# All POST/PUT/DELETE views protected by default with CsrfViewMiddleware
# API views using DRF with token auth can exempt CSRF:
from rest_framework.authentication import SessionAuthentication

class CsrfExemptSessionAuthentication(SessionAuthentication):
    def enforce_csrf(self, request):
        return  # Exempt for API token auth
```

## Input Validation

```python
# Always use Forms or Serializers for external input
class CreateUserForm(forms.Form):
    email = forms.EmailField(max_length=255)
    name = forms.CharField(max_length=100, strip=True)

    def clean_email(self):
        email = self.cleaned_data["email"].lower()
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Email already registered.")
        return email
```

## File Upload Security

```python
# Validate file type — never trust Content-Type header
import magic

def validate_image(file):
    mime = magic.from_buffer(file.read(1024), mime=True)
    if mime not in {"image/jpeg", "image/png", "image/webp"}:
        raise ValidationError("Invalid file type.")
    file.seek(0)

# Serve media files through a CDN or pre-signed URLs, not Django directly
```

## Password Policies

```python
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
     "OPTIONS": {"min_length": 12}},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]
```

## Rate Limiting

```python
# Use django-ratelimit or DRF throttling
from rest_framework.throttling import UserRateThrottle

class BurstRateThrottle(UserRateThrottle):
    rate = "60/min"

class AuthViewSet(viewsets.ViewSet):
    throttle_classes = [BurstRateThrottle]
```

## Secrets Checklist

- [ ] `SECRET_KEY` from environment variable only
- [ ] `DEBUG=False` in production
- [ ] `DATABASES` from `DATABASE_URL` env var
- [ ] API keys in environment or Key Vault — never in code
- [ ] `.env` files in `.gitignore`
- [ ] `ALLOWED_HOSTS` explicitly configured
