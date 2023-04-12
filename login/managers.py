from django.contrib.auth.models import BaseUserManager

class CustomUserManager(BaseUserManager):
    def create_user(self, mobile, password=None, **kwargs):
        if not mobile:
            raise ValueError("Mobile can't be null")
        user = self.model(
            mobile = mobile,
            **kwargs
        )
        user.set_password(password)
        user.save()
        return user
    
    def create_superuser(self, mobile, password=None, **kwargs):
        if not mobile:
            raise ValueError("Mobile can't be null")
        user = self.model(
            mobile = mobile,
            is_admin = True, 
            is_staff = True,
            is_superuser = True,
            **kwargs
        )
        user.set_password(password)
        user.save()
        return user