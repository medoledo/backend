from django.urls import path
from .views import (
    AttendanceCreateView,
    AttendanceUpdateView,
    AttendanceDeleteView,
    StudentSearchListView,
    AttendanceListView  # New view for listing attendance
)

urlpatterns = [
    path('add/', AttendanceCreateView.as_view(), name='attendance-create'),  # Add attendance
    path('edit/<int:pk>/', AttendanceUpdateView.as_view(), name='attendance-edit'),  # Edit attendance
    path('delete/<int:pk>/', AttendanceDeleteView.as_view(), name='attendance-delete'),  # Delete attendance
    path('search/', StudentSearchListView.as_view(), name='student-search'),  # Search students
    path('list/', AttendanceListView.as_view(), name='attendance-list'),  # View attendance list
]
