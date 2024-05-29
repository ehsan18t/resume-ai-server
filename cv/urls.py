from django.urls import path
from .views import *

urlpatterns = [
    path('apply/', apply_job, name='apply-for-job'),
    path('list/', get_cv_list, name='get-cv-list'),
    path('update-cv/', change_cv_status, name='change-cv-status'),
]
