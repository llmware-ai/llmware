from django.urls import path
from .views import (
    home,
    user_login,
    student_page,
    coordinator_page,
    supervisor_page,
    add_project,
    get_updated_project_list,
    approve_project,
    create_project_group,
    join_project_group,
    handle_join_group,
    apply_to_project,
    leave_project_group,
    withdraw_from_project,
    logout_user,
    reject_project,
    view_single_project,
    view_group,
    view_project_applications, 
    accept_application,
    reject_application,
    sentiment_analysis_application,
    query_analysis_application
)


urlpatterns = [
    path('home/', home, name='home'),
    path('login/', user_login, name='login'),
    path('student/', student_page, name='student'),
    path('coordinator/', coordinator_page, name='coordinator'),
    path('supervisor/', supervisor_page, name='supervisor'),
    path('add-project/', add_project, name='add-project'),
    path(
        'update-project-list/',
        get_updated_project_list,
        name='update-project-list'
    ),
    path('approve/<int:project_number>/', approve_project, name='approve'),
    path('reject/<int:project_number>/', reject_project, name='reject-project'),
    path('student/create-group/', create_project_group, name='create-group'),
    path('student/join-group/', join_project_group, name='join-group'),
    path(
        'student/join-group/<int:id>/',
        handle_join_group,
        name="handle-join-group"),
    path('student/apply/<int:id>/', apply_to_project, name="apply-project"),
    path(
        'url-to-join-group/<int:group_id>/',
        handle_join_group,
        name='handle-join-group'),
    path(
        'student/group-leave/<int:id>/',
        leave_project_group,
        name='leave-group'),
    path(
        'student/withdraw/<int:id>/',
        withdraw_from_project,
        name='withdraw-project'),
    path('user/logout/', logout_user, name='logout'),
    path('<str:role>/project/<int:topic_number>/', view_single_project, name='view_single_project'),
    path('supervisor/project/<int:id>/applications/', view_project_applications, name='view-applications'),
    path('supervisor/accept/<int:id>/<int:group_id>/', accept_application, name='accept-application'),
    path('supervisor/reject/<int:group_id>/', reject_application, name='reject-application'),
    path(
        '<str:role>/project/<int:topic_number>/',
        view_single_project,
        name='view_single_project'),
    path('group/<int:id>', view_group, name="view-group"),
    path('supervisor/analysis/<int:group_id>/', sentiment_analysis_application, name='sentiment-analysis'),
    path('supervisor/query-analysis/<int:group_id>/', query_analysis_application, name='query-analysis'),
]
