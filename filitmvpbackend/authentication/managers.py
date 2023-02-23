from django.contrib.auth.models import BaseUserManager

class CustomUserManager(BaseUserManager):
    def create_user(self, mobile, password, **extra_fields):
        if not mobile:
            raise ValueError("mobile can not be null.")
        user = self.model(mobile=mobile, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, mobile, password, **extra_fields):
        if not mobile:
            raise ValueError("Email can not be null.")
        user = self.model(mobile=mobile, is_admin=True, is_staff=True, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user