from django.urls import path
from .views import *

urlpatterns = [
    path('apply/', apply_job, name='apply-for-job'),
    path('list/', get_cv_list, name='get-cv-list'),
    path('jobs/', get_applied_jobs, name='get_applied_jobs'),
    path('jobs/feedback/', get_applied_jobs_feedback, name='get_applied_jobs_feedback'),
    path('summary/', get_cv_summary, name='get-cv-summary'),
    path('update-cv/', change_cv_status, name='change-cv-status'),
]
