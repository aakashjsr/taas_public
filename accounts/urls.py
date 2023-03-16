from django.urls import path

import accounts.views
from . import views as account_views

urlpatterns = [
    path('taggable-users/', accounts.views.TaggableUserListView.as_view()),
    path('users/', accounts.views.UserCreateView.as_view()),
    path('users/<int:pk>/', account_views.UserRUDView.as_view()),
    path('login/', account_views.LoginView.as_view()),
    path('logout/', account_views.LogoutView.as_view()),
]
