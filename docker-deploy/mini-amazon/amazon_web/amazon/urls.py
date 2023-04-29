from django.urls import path
import amazon.views
urlpatterns = [
    path('place_order/', amazon.views.place_order, name='place_order'),
    path('login/', amazon.views.login_request, name='login'),
    path('register/',amazon.views.register, name='register'),
    path("logout", amazon.views.logout_view, name='logout'),
    path('product_detail/<int:product_id>',amazon.views.product_detail,name='product_detail'),
    path('shopping_cart',amazon.views.cart,name='cart'),
    path('add_to_cart/<int:product_id>/',amazon.views.add_to_cart,name='add_to_cart'),
    path('remove_from_cart/<int:product_id>/',amazon.views.remove_from_cart,name='remove_from_cart'),
    path('search/<str:user_type>/', amazon.views.search, name='search'),
    path('user_profile',amazon.views.user_profile,name='user_profile'),
    path('order/<int:package_id>/',amazon.views.order_detail,name='order_detail'),
    path('user_edit/',amazon.views.user_edit,name='user_edit'),
    path('products/<str:category_name>/',amazon.views.products, name='products'),
    path('remove_order/<int:package_id>/',amazon.views.remove_order,name='remove_order'),

]