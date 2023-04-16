"""
urls for log app
"""

from django.urls import path

from . import views

app_name = 'log'

urlpatterns = [
    path('', views.ArticleListView.as_view(), name='article_list'),
    path('tag/<slug:slug>/', views.ArticleTagListView.as_view(), name='article_tag_list'),

    path('<int:pk>/', views.ArticleDetailView.as_view(), name='article_detail'),
    path('create/', views.ArticleCreateView.as_view(), name='article_create'),
    path('update/<int:pk>/', views.ArticleUpdateView.as_view(), name='article_update'),
    path('delete/<int:pk>/', views.ArticleDeleteView.as_view(), name='article_delete'),

    path('tag/config/list/', views.TagListView.as_view(), name='tag_list'),
    path('tag/config/create/', views.TagCreateView.as_view(), name='tag_create'),
    path('tag/config/update/<int:pk>/', views.TagUpdateView.as_view(), name='tag_update'),
    path('tag/config/delete/<int:pk>/', views.TagDeleteView.as_view(), name='tag_delete'),
]
