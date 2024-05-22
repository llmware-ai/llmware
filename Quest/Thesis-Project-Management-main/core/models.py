from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.base_user import BaseUserManager


# Custom UserManager to create users using email field.
class CustomUserManger(BaseUserManager):
    def create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError("Email is required")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user
    
    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        return self.create_user(email, password, **extra_fields)
    

class CustomUser(AbstractUser):
    username = None
    email = models.EmailField(unique=True)
    is_student = models.BooleanField(default=False)
    is_coordinator = models.BooleanField(default=False)
    is_supervisor = models.BooleanField(default=False)
    has_joined_group = models.BooleanField(default=False)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = CustomUserManger()


    def __str__(self):
        return f'{self.first_name} {self.last_name}'
    
    def get_name(self):
        return f'{self.first_name} {self.last_name}'
    
    def get_role(self):
        if self.is_student:
            return "Student"
        elif self.is_coordinator:
            return "Coordinator"
        elif self.is_supervisor:
            return "Supervisor"
    

class AvailableFor(models.Model):
    title = models.CharField(max_length=255)

    def __str__(self):
        return self.title


class Category(models.Model):
    title = models.CharField(max_length=255)
    
    def __str__(self):
        return self.title


class FieldResearch(models.Model):
    title = models.CharField(max_length=255)

    def __str__(self):
        return self.title
    

class Project(models.Model):
    topic_number = models.AutoField(primary_key=True)
    title = models.CharField(max_length=1024)
    description = models.TextField()
    supervisor = models.ForeignKey(CustomUser, on_delete=models.CASCADE)

    available_for = models.ManyToManyField(AvailableFor)
    categories = models.ManyToManyField(Category)
    fields_of_research = models.ManyToManyField(FieldResearch)

    is_approved = models.BooleanField(default=False)
    is_rejected = models.BooleanField(default=False)

    is_application_selected = models.BooleanField(default=False)

    def __str__(self):
        return self.title


class ProjectGroup(models.Model):
    name = models.CharField(max_length=255)
    applied_project = models.ForeignKey(Project, null=True, blank=True, on_delete=models.CASCADE)
    is_approved_by_supervisor = models.BooleanField(default=False)
    is_rejected_by_supervisor = models.BooleanField(default=False)

    def __str__(self):
        return self.name
    

class StudentInGroup(models.Model):
    project_group = models.ForeignKey(ProjectGroup, on_delete=models.CASCADE)
    student = models.ForeignKey(CustomUser, on_delete=models.CASCADE)


class ProjectApplyDetail(models.Model):
    project_group = models.OneToOneField(ProjectGroup, on_delete=models.CASCADE)
    why_interested = models.TextField()
    relevant_skills = models.TextField()
    how_to_contribute = models.TextField()