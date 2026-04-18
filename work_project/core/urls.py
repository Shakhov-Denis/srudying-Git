from django.urls import path
from .views import (
    RegisterView, LoginView, LogoutView, ProfileView,
    AccessRuleListView, ProductsMockView, OrdersMockView
)

urlpatterns = [
    path('register/', RegisterView.as_view()),
    path('login/', LoginView.as_view()),
    path('logout/', LogoutView.as_view()),
    path('profile/', ProfileView.as_view()),
    path('admin/access-rules/', AccessRuleListView.as_view()),
    path('products/', ProductsMockView.as_view()),
    path('orders/', OrdersMockView.as_view()),
]