from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from cards import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', TemplateView.as_view(template_name='pay.html')),
    path('room/<str:room_name>/', include('cards.urls')),
    path('host/<str:room_name>/', TemplateView.as_view(template_name='host.html')),
    path('dashboard/', views.dashboard),
    path('winners/', views.winners_archive),
    path('paid-success/', TemplateView.as_view(template_name='paid_success.html')),
    path('create-checkout-session/', views.create_checkout_session),
    path('webhook/', views.stripe_webhook),
    path('api/status/<str:room_name>/', views.room_status_api),
]
