from django.shortcuts import redirect, get_object_or_404
from django.shortcuts import redirect, render
from django.core import serializers
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.template import loader
from .forms import UserLoginForm, ProjectForm, ProjectGroupForm, ProjectApplyDetailForm, AnalysisQueryForm
from .models import CustomUser, Project, ProjectGroup, StudentInGroup, ProjectApplyDetail

from .llmware_sentiment import analyze_application_sentiment, analyze_application_query


def home(request):
    template = loader.get_template('home.html')
    context = {
        "username": "Test user",
        "project": "Test project"
    }
    return HttpResponse(template.render(context=context))


def user_login(request):
    if request.user.is_authenticated:
        logout(request=request)
    if request.method == "POST":
        form = UserLoginForm(request=request, data=request.POST)

        if form.is_valid():
            email = form.cleaned_data['username']
            print(email)
            password = form.cleaned_data['password']

            user = authenticate(username=email, password=password)

            if user is not None:
                login(request, user)

                if user.is_student:
                    return redirect('student')
                if user.is_supervisor:
                    return redirect('supervisor')
                if user.is_coordinator:
                    return redirect('coordinator')
    else:
        form = UserLoginForm()

    template = loader.get_template('login.html')
    return HttpResponse(template.render({'form': form}, request=request))


@login_required
def student_page(request):
    if request.user.is_student and request.user.has_joined_group:
        template = loader.get_template('student_page.html')

        projects = Project.objects.prefetch_related(
            'projectgroup_set').filter(is_approved=True)
        group = StudentInGroup.objects.select_related(
            'project_group').get(student=request.user)

        can_apply = True
        if group.project_group.applied_project and not group.project_group.is_rejected_by_supervisor:
            can_apply = False

        applied_project = None
        if not can_apply:
            project = group.project_group.applied_project

            applied_project = {
                'id': project.pk,
                'title': project.title,
                'description': project.description,
                'categories': [category.title for category in project.categories.all()],
                'field_of_research': [field.title for field in project.fields_of_research.all()],
                'available_for': [available.title for available in project.available_for.all()],
                'supervisor': project.supervisor,
                'is_approved_by_supervisor': group.project_group.is_approved_by_supervisor,
                'is_rejected_by_supervisor': group.project_group.is_rejected_by_supervisor,
                'is_application_selected': project.is_application_selected,
            }

        project_list = []
        for project in projects:
            categories = [
                category.title for category in project.categories.all()]
            fields_of_research = [
                field.title for field in project.fields_of_research.all()]
            available_for = [
                available.title for available in project.available_for.all()]

            accepted_group = None

            if project.is_application_selected:
                accepted_group = project.projectgroup_set.filter(
                    is_approved_by_supervisor=True).first()

            project_list.append({
                'id': project.pk,
                'title': project.title,
                'description': project.description,
                'categories': categories,
                'fields_of_research': fields_of_research,
                'available_for': available_for,
                'is_approved': project.is_approved,
                'supervisor': project.supervisor,
                'is_approved_by_supervisor': group.project_group.is_approved_by_supervisor,
                'is_rejected_by_supervisor': group.project_group.is_rejected_by_supervisor,
                'is_application_selected': project.is_application_selected,
                'accepted_group': accepted_group
            })
        context = {
            'project_list': project_list,
            'group': group.project_group,
            'can_apply': can_apply,
            'applied_project': applied_project,
            'has_joined_group': True
        }

        return HttpResponse(template.render(context=context, request=request))

    elif request.user.is_student and not request.user.has_joined_group:
        template = loader.get_template('student_page.html')

        context = {
            'has_joined_group': False
        }
        print(context)
        return HttpResponse(template.render(context=context, request=request))
    else:
        return redirect('login')


@login_required
def create_project_group(request):
    if request.user.is_student and not request.user.has_joined_group:
        template = loader.get_template('add_group.html')
        if request.method == "POST":
            form = ProjectGroupForm(data=request.POST)

            if form.is_valid():
                group = form.save()
                request.user.has_joined_group = True
                request.user.save()

                student_in_group = StudentInGroup(
                    project_group=group, student=request.user)
                student_in_group.save()

                return redirect('student')
            else:
                print(form.errors)
        else:
            form = ProjectGroupForm()

        return HttpResponse(template.render(request=request, context={"form": form}))
    return HttpResponse("Not authorized")


@login_required
def join_project_group(request):
    if request.user.is_student and not request.user.has_joined_group:
        template = loader.get_template('join_group.html')

        groups = ProjectGroup.objects.all()
        group_list = []

        for group in groups:
            can_join = True
            member_count = group.studentingroup_set.count()
            if member_count >= 4:
                can_join = False

            group_list.append({
                "id": group.pk,
                "name": group.name,
                "member_count": member_count,
                "can_join": can_join
            })

        context = {
            "group_list": group_list,
        }

        return HttpResponse(template.render(request=request, context=context))


@login_required
def leave_project_group(request, id):
    if request.user.is_student and request.user.has_joined_group:
        group = get_object_or_404(ProjectGroup, pk=id)

        student_in_group = StudentInGroup.objects.get(
            project_group=group.pk, student=request.user.pk)

        student_in_group.delete()

        if group.studentingroup_set.count() == 0:
            group.delete()

        request.user.has_joined_group = False
        request.user.save()

        return redirect('student')

    return HttpResponse("Unauthorized")


@login_required
def handle_join_group(request, id):
    if request.user.is_student and not request.user.has_joined_group:
        group = get_object_or_404(ProjectGroup, pk=id)

        add_to_group = StudentInGroup(
            project_group=group, student=request.user)
        add_to_group.save()

        request.user.has_joined_group = True
        request.user.save()

        return redirect('student')
    return HttpResponse("Not authorized")


@login_required
def view_group(request, id):
    if request.user.is_student or request.user.is_coordinator:
        template = loader.get_template('view_group.html')
        print(id)

        project_group = get_object_or_404(ProjectGroup, id=id)

        students_in_group = StudentInGroup.objects.filter(
            project_group=project_group).select_related('student')

        group = StudentInGroup.objects.select_related(
            'project_group').get(student=request.user)

        members = [
            f"{student.student.first_name} {student.student.last_name}" for student in students_in_group]

        group_details = {
            "id": project_group.id,
            "name": project_group.name,
            "members": members,
            "applied_project": project_group.applied_project,
            'is_approved_by_supervisor': group.project_group.is_approved_by_supervisor,
            'is_rejected_by_supervisor': group.project_group.is_rejected_by_supervisor,
        }
        print(project_group.applied_project)
        context = {
            'group': group_details
        }
        return HttpResponse(template.render(request=request, context=context))


@login_required
def apply_to_project(request, id):
    if request.user.is_student and request.user.has_joined_group:
        template = loader.get_template('apply_for_project.html')

        project = get_object_or_404(Project, pk=id)

        if project.is_application_selected:
            return HttpResponse("Application for this project is already accepted. Apply to other projects!")

        group = StudentInGroup.objects.select_related(
            'project_group').get(student=request.user)

        if group.project_group.applied_project and group.project_group.applied_project.pk == project.pk:
            if not group.project_group.applied_project.is_application_selected and group.project_group.is_rejected_by_supervisor:
                return HttpResponse("Cannot apply to this project, supervisor rejected it.")

        if group.project_group.is_rejected_by_supervisor:
            apply_detail = get_object_or_404(
                ProjectApplyDetail, project_group=group.project_group)
            group.project_group.projectapplydetail = None
            project = group.project_group.applied_project
            group.project_group.applied_project = None
            group.project_group.is_rejected_by_supervisor = False
            apply_detail.delete()
            group.project_group.save()

            if project:
                project.projectgroup = None
                project.save()

        if request.method == "POST":
            form = ProjectApplyDetailForm(data=request.POST)

            if form.is_valid():
                why_interested = form.cleaned_data['why_interested']
                relevant_skills = form.cleaned_data['relevant_skills']
                how_to_contribute = form.cleaned_data['how_to_contribute']

                apply_detail = ProjectApplyDetail(
                    project_group=group.project_group, why_interested=why_interested,
                    relevant_skills=relevant_skills, how_to_contribute=how_to_contribute)
                apply_detail.save()

                group.project_group.applied_project = project
                group.project_group.save()

                return redirect('student')
            else:
                print(form.errors)
        else:
            form = ProjectApplyDetailForm()

            context = {
                'form': form,
                'project': project
            }

        return HttpResponse(template.render(request=request, context=context))


@login_required
def withdraw_from_project(request, id):
    if request.user.is_student and request.user.has_joined_group:

        group = get_object_or_404(ProjectGroup, pk=id)

        if group.is_approved_by_supervisor and not group.is_rejected_by_supervisor:
            return HttpResponse("Cannot withdraw, application already accepted.")

        apply_detail = get_object_or_404(
            ProjectApplyDetail, project_group=group)
        group.projectapplydetail = None
        project = group.applied_project
        group.applied_project = None
        apply_detail.delete()
        group.save()

        if project:
            project.projectgroup = None
            project.save()

        return redirect('student')
    return HttpResponse("Not authorized")


@login_required
def coordinator_page(request):
    if request.user.is_coordinator:
        template = loader.get_template('coordinator_page.html')

        projects = Project.objects.all()

        project_list = []
        for project in projects:
            categories = [
                category.title for category in project.categories.all()]

            project_list.append({
                'id': project.pk,
                'title': project.title,
                'categories': categories,
                'is_approved': project.is_approved,
                'is_rejected': project.is_rejected,
                'supervisor': project.supervisor
            })

        context = {
            'project_list': project_list
        }

        return HttpResponse(template.render(context=context, request=request))

    else:
        return redirect('login')


@login_required
def supervisor_page(request):
    if request.user.is_supervisor:
        template = loader.get_template('supervisor_page.html')

        projects = Project.objects.filter(supervisor=request.user)
        project_list = []
        for project in projects:
            categories = [
                category.title for category in project.categories.all()]
            fields_of_research = [
                field.title for field in project.fields_of_research.all()]
            available_for = [
                available.title for available in project.available_for.all()]

            total_application_count = 0
            if project.is_approved:
                total_application_count = len(
                    ProjectGroup.objects.filter(applied_project=project))
            project_list.append({
                'id': project.pk,
                'title': project.title,
                'description': project.description,
                'categories': categories,
                'fields_of_research': fields_of_research,
                'available_for': available_for,
                'is_approved': project.is_approved,
                'is_rejected': project.is_rejected,
                "total_application_count": total_application_count
            })

        context = {
            'project_list': project_list
        }

        print(context)

        return HttpResponse(template.render(context=context, request=request))

    else:
        return redirect('login')


@login_required
def add_project(request):
    if request.method == 'POST' and request.user.is_supervisor:
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save(commit=False)
            project.supervisor = request.user
            project.save()
            form.save_m2m()

            return redirect('supervisor')
        else:
            print(form.errors)

    else:
        form = ProjectForm()

    template = loader.get_template('project_form.html')
    return HttpResponse(template.render({'form': form}, request))


@login_required
def approve_project(request, project_number):
    if request.user.is_coordinator:
        project = get_object_or_404(Project, pk=project_number)

        project.is_approved = True
        project.save()

        return redirect('coordinator')
    else:
        return HttpResponse("Not authorized")


@login_required
def reject_project(request, project_number):
    if request.user.is_coordinator:
        project = get_object_or_404(Project, pk=project_number)

        project.is_rejected = True
        project.save()

        return redirect('coordinator')

    else:
        return HttpResponse("Not authorized")


def get_updated_project_list(request):
    status_filter = request.GET.get('status_filter')

    if status_filter == 'all':
        updated_project_list = Project.objects.filter(
            supervisor=request.user) if request.user.is_supervisor else Project.objects.all()
    elif status_filter == 'approved':
        updated_project_list = Project.objects.filter(supervisor=request.user).filter(
            is_approved=True) if request.user.is_supervisor else Project.objects.filter(is_approved=True)
    elif status_filter == 'pending':
        updated_project_list = Project.objects.filter(supervisor=request.user).filter(is_approved=False).filter(is_rejected=False) if request.user.is_supervisor else Project.objects.filter(
            is_approved=False).filter(is_rejected=False)
    elif status_filter == 'rejected':
        updated_project_list = Project.objects.filter(supervisor=request.user).filter(
            is_rejected=True) if request.user.is_supervisor else Project.objects.filter(is_rejected=True)
    else:
        updated_project_list = Project.objects.filter(supervisor=request.user).all(
        ) if request.user.is_supervisor else Project.objects.all()

    project_list = []
    for project in updated_project_list:
        categories = [
            category.title for category in project.categories.all()]
        fields_of_research = [
            field.title for field in project.fields_of_research.all()]
        available_for = [
            available.title for available in project.available_for.all()]
        
        total_application_count = 0
        if project.is_approved:
            total_application_count = len(
                ProjectGroup.objects.filter(applied_project=project))

        project_list.append({
            'id':project.topic_number,
            'title': project.title,
            'description': project.description,
            'categories': categories,
            'fields_of_research': fields_of_research,
            'available_for': available_for,
            'is_approved': project.is_approved,
            'is_rejected': project.is_rejected,
            'supervisor': f"{project.supervisor.first_name} {project.supervisor.last_name}",
            "get_role": request.user.get_role(),
            "topic_number": project.topic_number,
            "total_application_count": total_application_count
        })

    context = {
        'project_list': project_list
    }

    serialized_projects = serializers.serialize('json', updated_project_list)
    return JsonResponse(context)


@login_required
def logout_user(request):
    logout(request=request)

    return redirect('login')


@login_required
def view_single_project(request, role, topic_number):
    if request.user.is_supervisor or request.user.is_student or request.user.is_coordinator:
        template = loader.get_template('single_project.html')

        single_project = Project.objects.prefetch_related(
            "projectgroup_set").filter(topic_number=topic_number)[0]
        categories = [
            category.title for category in single_project.categories.all()]
        fields_of_research = [
            field.title for field in single_project.fields_of_research.all()]
        available_for = [
            available.title for available in single_project.available_for.all()]

        accepted_group = None

        if single_project.is_application_selected:
            accepted_group = single_project.projectgroup_set.filter(
                is_approved_by_supervisor=True).first()
        project = {
            'title': single_project.title,
            'description': single_project.description,
            'categories': categories,
            'fields_of_research': fields_of_research,
            'available_for': available_for,
            'is_approved': single_project.is_approved,
            'supervisor': f"{single_project.supervisor.first_name} {single_project.supervisor.last_name}",
            "get_role": request.user.get_role(),
            "id": single_project.topic_number,
            'is_rejected': single_project.is_rejected,
            'accepted_group': accepted_group,
        }

        if single_project.is_approved:
            total_application_count = len(
                ProjectGroup.objects.filter(applied_project=single_project))

            project["total_application_count"] = total_application_count

        context = {
            'project': project,
        }

        print(context)

        if request.user.is_student:
            group = StudentInGroup.objects.select_related(
                'project_group').get(student=request.user)

            can_apply = True
            if group.project_group.applied_project and not group.project_group.is_rejected_by_supervisor:
                can_apply = False

            applied_project = []
            if not can_apply:
                applied_project = group.project_group.applied_project

            context["applied_project"] = applied_project
            context["group"] = group.project_group
            project["can_apply"] = can_apply
            project["is_approved_by_supervisor"] = group.project_group.is_approved_by_supervisor
            project["is_rejected_by_supervisor"] = group.project_group.is_rejected_by_supervisor
            project["is_application_selected"] = single_project.is_application_selected

        return HttpResponse(template.render(context=context, request=request))
    else:
        return redirect('login')


@login_required
def view_project_applications(request, id):
    if request.user.is_supervisor:
        template = loader.get_template('view_project_applications.html')
        project = get_object_or_404(Project, pk=id)
        if project.is_approved:
            groups = ProjectGroup.objects.filter(applied_project=project)

            application_list = []

            for group in groups:
                members = [member.student.get_name()
                           for member in group.studentingroup_set.all()]

                apply_detail = ProjectApplyDetail.objects.get(
                    project_group=group)

                application_list.append({
                    'group': group.name,
                    'group_id': group.pk,
                    'members': members,
                    'why_interested': apply_detail.why_interested,
                    'relevant_skills': apply_detail.relevant_skills,
                    'how_to_contribute': apply_detail.how_to_contribute,
                    'is_approved_by_supervisor': group.is_approved_by_supervisor,
                    'is_rejected_by_supervisor': group.is_rejected_by_supervisor,
                    'is_application_approved': group.is_approved_by_supervisor and not group.is_rejected_by_supervisor,
                })

            context = {
                'application_list': application_list,
                'project': project.title,
                'id': project.pk,
                'is_application_selected': project.is_application_selected,
            }

            return HttpResponse(template.render(request=request, context=context))


@login_required
def accept_application(request, id, group_id):
    if request.user.is_supervisor:
        project = get_object_or_404(Project, pk=id)
        group = get_object_or_404(ProjectGroup, pk=group_id)

        groups = ProjectGroup.objects.filter(applied_project=project)
        for g in groups:
            g.is_rejected_by_supervisor = True
            g.save()

        project.is_application_selected = True
        group.is_approved_by_supervisor = True
        group.is_rejected_by_supervisor = False

        project.save()
        group.save()

        return redirect('supervisor')

    return HttpResponse("Not authorized")


@login_required
def reject_application(request, group_id):
    if request.user.is_supervisor:
        group = get_object_or_404(ProjectGroup, pk=group_id)

        group.is_rejected_by_supervisor = True
        group.save()

        return redirect('supervisor')
    return HttpResponse("Not authorized")


def get_input_to_model(group, categories):
    input_to_model = f'Project: {group.applied_project.title}\n'
    input_to_model += f'Description: {group.applied_project.description}\n'
    input_to_model += f'Categories: {categories}\n'
    input_to_model += f'What excites you the most about this project, and why do you want to be a part of it? {group.projectapplydetail.why_interested}\n'
    input_to_model += f'Describe any previous experiences or skills you have that are directly relevant to this project. {group.projectapplydetail.relevant_skills}\n'
    input_to_model += f'How do you think these will help you contribute effectively?What specific contributions do you hope to make to this project, and what are your personal and professional goals for participating in it? {group.projectapplydetail.how_to_contribute}\n'

    return input_to_model


@login_required
def sentiment_analysis_application(request, group_id):
    if request.user.is_supervisor:
        group = ProjectGroup.objects.prefetch_related('projectapplydetail').select_related('applied_project').get(pk=group_id)

        categories = [category.title for category in group.applied_project.categories.all()]
        

        confidence_level, sentiment_value = analyze_application_sentiment(get_input_to_model(group, categories))

        context = {
            "confidence_level": confidence_level,
            "sentiment_value": sentiment_value[0],
        }

        print(context)
        
        return JsonResponse(context)


@login_required
def query_analysis_application(request, group_id):
    if request.user.is_supervisor:
        template = loader.get_template('query_analysis.html')
        if request.method == "POST":
            group = ProjectGroup.objects.prefetch_related('projectapplydetail').select_related('applied_project').get(pk=group_id)

            categories = [category.title for category in group.applied_project.categories.all()]

            form = AnalysisQueryForm(data=request.POST)
            if form.is_valid():
                query = form.cleaned_data.get('query')

                answer, explanation = analyze_application_query(get_input_to_model(group, categories), query)

                context = {
                    "answer": answer[0],
                    "explanation": explanation[0]
                }

                print(context)

                return HttpResponse(template.render(context=context))

        else:
            form = AnalysisQueryForm()

            return HttpResponse(template.render({"form":form}, request=request))

