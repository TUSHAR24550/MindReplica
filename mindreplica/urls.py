from django.urls import path
from . import views
from accounts import views as account_views

urlpatterns = [
    path('', views.home, name='home'),
    path('train/', views.train_clone, name='train_clone'),
    path('memories/', views.memory_board, name='memory_board'),

    # Sabke twins ki list
    path('twins/', views.twin_list, name='twin_list'),

    # Chat pages
    path('chat/', views.chat_page, name='chat'),
    path('chat/<str:username>/', views.chat_page, name='chat_with_twin'),

    # AI API endpoint
    path('chat_with_ai/', views.chat_with_ai, name='chat_with_ai'),
    
    
]