from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, AvailableFor, Category, FieldResearch, Project, ProjectGroup, StudentInGroup, ProjectApplyDetail
from .forms import CustomUserCreationForm, CustomUserChangeForm


class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = CustomUser

    list_display = ("email", "is_student", "is_supervisor", "is_coordinator",)

    fieldsets = (
        (None, {"fields": ("first_name", "last_name", "email", "password")}),
        ("Permissions", {"fields": ("is_staff", "is_active", "is_student", "is_supervisor", "is_coordinator")})
    )

    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": (
                "first_name","last_name", "email", "password1", "password2", "is_staff", "is_active", "is_student", "is_supervisor", "is_coordinator",
            )
        }),
    )

    ordering = ("email",)
    search_fields = ("email",)




admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(AvailableFor)
admin.site.register(Category)
admin.site.register(FieldResearch)
admin.site.register(Project)
admin.site.register(StudentInGroup)
admin.site.register(ProjectGroup)
admin.site.register(ProjectApplyDetail)
