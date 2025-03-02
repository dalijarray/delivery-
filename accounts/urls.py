from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.user_login, name='login'),
    path('signup/', views.signup, name='signup'),
    path('logout/', views.user_logout, name='logout'),
    path('admin/add-product/', views.admin_add_product, name='admin_add_product'),
    path('admin/orders/', views.admin_orders, name='admin_orders'),
    path('admin/dashboard/', views.admin_dashboard, name='admin_dashboard'),
        path('livreur/dashboard/', views.livreur_dashboard, name='livreur_dashboard'),
        path('client/dashboard/', views.client_dashboard, name='client_dashboard'),
        path('product/<int:product_id>/', views.product_detail, name='product_detail'),
    path('orders/', views.orders, name='orders'),
    path('update-location/<int:order_id>/', views.update_delivery_location, name='update_location'),  # Updated
    path('track-delivery/<int:order_id>/', views.track_delivery, name='track_delivery'),
    path('edit-product/<int:product_id>/', views.edit_product, name='edit_product'),  # New
    path('delete-product/<int:product_id>/', views.delete_product, name='delete_product'),  # New
]
