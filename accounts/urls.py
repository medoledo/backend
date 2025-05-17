from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from . import views
from .views import CustomTokenObtainPairView , PublicKeyView

urlpatterns = [
    # Authentication Endpoints
    path('login/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('public-key/', PublicKeyView.as_view(), name='public-key'),

    # Dashboard Endpoints
    path('dashboard/admin/', views.admin_dashboard, name='admin_dashboard'),
    path('dashboard/teacher/', views.teacher_dashboard, name='teacher_dashboard'),
    path('dashboard/student/', views.student_dashboard, name='student_dashboard'),
    path('dashboard/assistant/', views.assistant_dashboard, name='assistant_dashboard'),

    # Student Management
    path('students/', views.list_students, name='list_students'),
    path('students/create/', views.create_student, name='create_student'),
    path('students/<int:pk>/', views.student_detail, name='student_detail'),
    path('students/approve/<int:student_id>/', views.approve_student, name='approve_student'),

    # Teacher Management
    path('teachers/', views.list_teachers, name='list_teachers'),
    path('teachers/create/', views.create_teacher_profile, name='create_teacher'),
    path('teachers/me/', views.my_teacher_profile, name='my_teacher_profile'),
    path('teachers/<int:pk>/', views.teacher_detail, name='teacher_detail'),

    # Assistant Management
    path('assistants/', views.view_assistants, name='list_assistants'),
    path('assistants/create/', views.create_assistant, name='create_assistant'),
    path('assistants/<int:assistant_id>/', views.update_assistant, name='update_assistant'),
    path('assistants/<int:assistant_id>/delete/', views.delete_assistant, name='delete_assistant'),

    # Center Management
    path('centers/create/', views.create_center, name='create_center'),
    path('centers/', views.list_centers, name='list_centers'),

]