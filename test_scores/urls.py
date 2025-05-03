from django.urls import path
from .views import (
    TestScoreCreateView,
    TestScoreUpdateView,
    TestScoreDeleteView,
    TestScoreSearchView
)

urlpatterns = [
    path('create/', TestScoreCreateView.as_view(), name='testscore-create'),  # Add score
    path('edit/<int:pk>/', TestScoreUpdateView.as_view(), name='testscore-edit'),  # Edit score
    path('delete/<int:pk>/', TestScoreDeleteView.as_view(), name='testscore-delete'),  # Delete score
    path('search/', TestScoreSearchView.as_view(), name='testscore-search'),  # Search score
]
