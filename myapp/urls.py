from django.urls import path
from . import views

app_name = 'myapp'

urlpatterns = [
    path('login/', views.login_view, name='login'),
    
    path('', views.home, name='home'),
    path('today/', views.today, name='today'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('dashboard/detail', views.detail, name='detail'),
    
    path('site_wiki/', views.site_wiki, name='site-wiki'),
    path('mypage/', views.mypage, name='mypage'),
    path('mypage/logout/', views.logout, name='logout'),
    path('mypage/appearance/', views.appearance, name='appearance'),
    
    path('image/', views.image, name='image'),
    path('dashboard/chart/', views.chart, name='chart'),
]