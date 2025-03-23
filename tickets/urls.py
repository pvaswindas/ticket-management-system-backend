from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'', views.TicketViewSet, basename='ticket')

urlpatterns = [
    path('', include(router.urls)),
    path(
        'tickets/stats/', views.TicketStatsView.as_view(), name='ticket-stats'
    ),
]
