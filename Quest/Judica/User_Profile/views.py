from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from User_Profile.models import *

def register(request):
    messages_list = []
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        profile_photo = request.FILES.get('profile_photo')

        if password == confirm_password:
            if User.objects.filter(username=username).exists():
                messages.error(request, 'Username already exists.')
            elif User.objects.filter(email=email).exists():
                messages.error(request, 'Email already exists.')
            else:
                user = User.objects.create_user(username=username, email=email, password=password)
                user.save()
                user_profile = UserProfile.objects.create(user=user, profile_photo=profile_photo)
                user_profile.save()
                messages.success(request, 'Registration successful. Please log in.')
                return redirect('login')
        else:
            messages.error(request, 'Passwords do not match.')
    for message in messages.get_messages(request):
        messages_list.append(message)
    context = {'messages': messages_list}
    return render(request, 'register.html', context)

def user_login(request):
    messages_list = []
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('user_cases')
        else:
            messages.error(request, 'Invalid username or password.')
    for message in messages.get_messages(request):
        messages_list.append(message)
    context = {'messages': messages_list}
    return render(request, 'login.html', context)

@login_required
def file_case(request):
    user = request.user
    user_profile = get_object_or_404(UserProfile, user=user)
    all_users = User.objects.exclude(username__in=['admin', user.username])

    if request.method == 'POST':
        case_against_id = request.POST.get('case_against')
        details = request.POST.get('details')
        document = request.FILES.get('document')
        
        if case_against_id and details:
            case_against = User.objects.get(id=case_against_id)
            Case.objects.create(
                filed_by=user,
                case_against=case_against,
                details=details,
                document=document
            )
            return redirect('user_cases')

    context = {
        'user': user,
        'user_profile': user_profile,
        'all_users': all_users
    }
    return render(request, 'file_case.html', context)

@login_required
def user_cases(request):
    user = request.user
    user_profile = get_object_or_404(UserProfile, user=user)
    filed_cases = Case.objects.filter(filed_by=user)
    cases_against = Case.objects.filter(case_against=user)
    
    user_cases = filed_cases.union(cases_against)
    
    context = {
        'user_profile': user_profile,
        'user': user,
        'user_cases': user_cases
    }
    
    return render(request, 'cases.html', context)

@login_required
def user_messages(request):
    return render (request,'messages.html')