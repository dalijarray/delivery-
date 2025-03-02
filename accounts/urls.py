from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.user_login, name='login'),
    path('signup/', views.signup, name='signup'),
    path('logout/', views.user_logout, name='logout'),
    path('admin/add-product/', views.admin_add_product, name='admin_add_product'),
    path('admin/orders/', views.admin_orders, name='admin_orders'),
    path('livreur/dashboard/', views.livreur_dashboard, name='livreur_dashboard'),
    path('client/dashboard/', views.client_dashboard, name='client_dashboard'),
    path('product/<int:product_id>/', views.product_detail, name='product_detail'),
]