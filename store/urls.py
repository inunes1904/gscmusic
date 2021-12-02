from . import views
from django.urls import path

urlpatterns = [
    path('', views.store, name="store"),
    path('cart/', views.cart, name="cart"),
    path('checkout', views.checkout, name="checkout"),
    path('update_item/', views.update_item, name="update_item"),
    path('process_order/', views.process_order, name="process_order"),
    path('login', views.login, name="login"),
    path('logout', views.logout_user, name="logout"),
    path('register', views.register, name="register"),
    path('product/<int:id>', views.product, name="product")

]



