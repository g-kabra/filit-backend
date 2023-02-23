from django.contrib.auth.models import BaseUserManager

class CustomUserManager(BaseUserManager):
    def create_user(self, email, **extra_fields):
        if not email:
            raise ValueError("Email can not be null.")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password("")
        user.save(using=self._db)
        return user
