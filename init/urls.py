from django.urls import path
from . import views

app_name = 'init'

urlpatterns = [
    path('', views.begin, name='begin'),
    path('personal_info/', views.personal_info_create, name='q1'),
    path('service_type/', views.service_select, name='q2'),
    
    path('alc_type/yes/', views.hellojtj, name='q3-jtj'), #    
    path('alc_type/no/', views.alc_type_select, name='q3'),
    path('golajusem/', views.alc_product_select, name='q3-detail'),
    
    path('golajusem/list', views.alc_product_select_list, name='q3-list'),
    path('golajusem/alc_type', views.alc_type_select_list, name='q3-list-alc-type'),
    
    path('factor/', views.factor_select, name='q4'),
    path('factor/1/', views.scentorstrong_select, name='q4-scentorstrong'),
    path('factor/2/', views.sweetorsour_select, name='q4-sweetorsour'),
    path('factor/3/', views.bodyorfizzy_select, name='q4-bodyorfizzy'),
    path('factor/1/1/', views.scent_select, name='q4-scent-select'),
    
    path('alc_range_bool/', views.alc_range_bool_select, name='q5'),
    path('CE_good_bool/', views.CE_good_bool_select, name='q6'),
    
    path('golajum/', views.result, name='result'),
    path('signin/', views.signin, name='signin'),
    path('save/', views.save, name='save'),
]