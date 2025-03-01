from django.urls import path
from . import views

urlpatterns = [
    path('signup/', views.signup, name='signup'),
    path('login/', views.user_login, name='login'),
    path('admin/dashboard/', views.admin_dashboard, name='admin_dashboard'),
path('livreur/dashboard/', views.livreur_dashboard, name='livreur_dashboard'),
path('client/dashboard/', views.client_dashboard, name='client_dashboard'),
path('product/<int:product_id>/', views.product_detail, name='product_detail'),
]