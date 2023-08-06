from django.contrib import admin
from django.urls import path
from authentication import views,AdminViews
from django.conf import settings
from django.conf.urls.static import static
from .AdminViews import get_related_images
from django.urls import reverse


urlpatterns = [    
    path("signup/", views.signupView, name="signup"),
    path('', views.loginView, name='loginhome'),
    path("login/", views.loginView, name="login"),
    path('logout/',views.logoutView, name='logout'),
    path('gerer_docker/', AdminViews.gerer_docker, name='gerer_docker'),
    path('PerformancesDetails/', AdminViews.PerformancesDetails, name='PerformancesDetails'),
    path('gerer_images/', AdminViews.gerer_images, name='gerer_images'),
    path('gerer_docker/<str:container_id>/', AdminViews.gerer_docker, name='gerer_docker'),
    path('run_container/', AdminViews.run_container, name='run_container'),
    path('create_containers/', AdminViews.create_containers, name='create_containers'),
    path('delete_container/<str:container_id>', AdminViews.delete_container, name='delete_container'),
    path('delete_containers/', AdminViews.delete_containers, name='delete_containers'),
    path('edit_container/', AdminViews.edit_container, name='edit_container'),
    path('start_container/<str:container_id>', AdminViews.start_container, name='start_container'),
    path('stop_container/<str:container_id>', AdminViews.stop_container, name='stop_container'),
    path('get_related_images/<str:image_name>/', get_related_images, name='get_related_images'),
    path('pull_image/<path:args>/',AdminViews.pull_image, name='pull_image'),
    path('delete_image/<path:args>/', AdminViews.delete_image, name='delete_image'),
    path('delete_all_ubuntu_images/', AdminViews.delete_all_ubuntu_images, name='delete_all_ubuntu_images'),
    
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

