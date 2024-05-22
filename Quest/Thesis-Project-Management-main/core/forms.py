from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm, AuthenticationForm

from .models import CustomUser, Project, AvailableFor, Category, FieldResearch, ProjectGroup, ProjectApplyDetail

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ("first_name", "last_name", "email", "is_student", "is_student", "is_coordinator", "is_supervisor")


class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = CustomUser
        fields = ("first_name", "last_name", "email", "is_student", "is_student", "is_coordinator", "is_supervisor")



class UserLoginForm(AuthenticationForm):
    username = forms.EmailField(label='Email')
    password = forms.CharField(widget=forms.PasswordInput())


class ProjectForm(forms.ModelForm):

    def __init(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['available_for'].queryset = AvailableFor.objects.all()
        self.fields['categories'].queryset = Category.objects.all()
        self.fields['fields_of_research'].queryset = FieldResearch.objects.all()

    class Meta:
        model = Project
        fields = ['topic_number','title', 'description', 'available_for', 'categories', 'fields_of_research']


class ProjectGroupForm(forms.ModelForm):
    class Meta:
        model = ProjectGroup
        fields = ['name']


class ProjectApplyDetailForm(forms.ModelForm):
    class Meta:
        model = ProjectApplyDetail
        fields = ['why_interested', 'relevant_skills', 'how_to_contribute']


class AnalysisQueryForm(forms.Form):
    query = forms.CharField(max_length=1024)