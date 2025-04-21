from django.contrib import admin
from django.urls import path
from spinapp import views


urlpatterns = [
    path('', views.index, name='index'),

    path('add-user/', views.add_user, name='add_user'),
    path('display-users/', views.display_users, name='display_users'),
    path("deluser/<int:id>/", views.deluser, name='deluser'),
    path("updateuser/<int:id>/", views.updateuser, name='updateuser'),
    path("do_updateuser/<int:id>/", views.do_updateuser, name='do_updateuser'),



    path('assign-house-to-user/<str:house_csv_file>/<str:house_number>/', views.assign_house_to_user, name='assign_house_to_user'),
    path('assign_house/', views.assign_house, name='assign_house'),
    path('assign_house_display/', views.assign_house_display, name='assign_house_display'),
    path("delassignhouse/<int:id>/", views.delassignhouse, name='delassignhouse'),
    path("updateassignhouse/<int:id>/", views.updateassignhouse, name='updateassignhouse'),
    path("do_updateassignhouse/<int:id>/", views.do_updateassignhouse, name='do_updateassignhouse'),

    path("download_assigned_csv/", views.download_assigned_csv, name="download_assigned_csv"),
    path("clear_assigned_csv/", views.clear_assigned_csv, name="clear_assigned_csv"),



    path('adminpanel/', views.adminpanel, name='adminpanel'),

    path("upload_csv/", views.upload_csv, name="upload_csv"),
    path("display_uploaded_csv_files/", views.display_uploaded_csv_files, name="display_uploaded_csv_files"),
    path("delete_uploaded_csv_file/<str:filename>/", views.delete_uploaded_csv_file, name="delete_uploaded_csv_file"),


    path('upload_houses_csv/', views.upload_houses_csv, name='upload_houses_csv'),
    path("display_houses_csv_files/", views.display_houses_csv_files, name="display_houses_csv_files"),
    path("delete_houses_csv/<str:filename>/", views.delete_houses_csv, name="delete_houses_csv"),


    path('participated/', views.participated, name='participated'),

]

