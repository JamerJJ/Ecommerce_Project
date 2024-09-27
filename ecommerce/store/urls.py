from django.urls import path, include
from . import views 

urlpatterns = [
    #empty string for base url
    path('', views.store, name='store'),
    path('cart/', views.cart, name='cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('update_item/', views.updateItem, name='update_item'),
    path('process_order/', views.processOrder, name='process_order'),

    path('register/', views.registerPage, name='register'),
    path('login/', views.loginPage, name='login'),
    path('logout/', views.logoutUser, name='logout'),
    path('product/<int:product_id>/', views.productDetail, name='product_detail'),
    path('search/', views.search_view, name='search'),
    path('wishlist/', views.wishlist_view, name='wishlist'),
    path('add/<int:product_id>/', views.addToWishlist, name='addToWishlist'),
    path('remove/<int:product_id>/', views.removeFromWishlist, name='removeFromWishlist'),
    path('filter_category/', views.filterByCategory , name='filter_category'),
    
    
]