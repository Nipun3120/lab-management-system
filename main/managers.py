from django.contrib.auth.base_user import BaseUserManager
from django.utils.translation import ugettext_lazy

class CustomUserManager(BaseUserManager):

    def create_user(self, email, password, **extra_fields):
        
        # Create and save a User with the given email and password.
        if not email:
            raise ValueError(ugettext_lazy('Please provide an Email address'))
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        extra_fields.setdefault('active', True)
        user.save()
        print(user.is_active)
        return user

    def create_superuser(self, email, password, **extra_fields):
        # Create and save a SuperUser with the given email and password.
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('active', Tru)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError(ugettext_lazy('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(ugettext_lazy('Superuser must have is_superuser=True.'))
        return self.create_user(email, password, **extra_fields)

        


