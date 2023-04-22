from django.urls import path
import amazon.views
urlpatterns = [
    path('place_order/', amazon.views.place_order, name='place_order'),
]