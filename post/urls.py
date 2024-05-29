from django.urls import path
from .views import *

urlpatterns = [
    path('create/', create_post, name='create-post'),
    path('user-posts/', get_user_posts, name='get-user-posts'),
    path('category/create/', create_category, name='create-category'),
    path('category-list/', get_category_list, name='get-category-list'),
    path('category-posts/', get_category_posts, name='get-category-posts'),
    path('feed/', get_feed_posts, name='get-feed-posts'),
]
