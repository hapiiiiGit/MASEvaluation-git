from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework import routers

from users.views import UserViewSet, UserRegistrationView
from events.views import EventViewSet, SummitViewSet, ConferenceViewSet, SessionViewSet
from ticketing.views import TicketViewSet, OrderViewSet, PaymentViewSet
from chatbot.views import ChatSessionViewSet, ChatMessageViewSet, UserInteractionViewSet
from dashboard.views import AdminDashboardView, AdminEventViewSet, AdminUserViewSet, AdminOrderViewSet, AdminPaymentViewSet

router = routers.DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'events', EventViewSet, basename='event')
router.register(r'summits', SummitViewSet, basename='summit')
router.register(r'conferences', ConferenceViewSet, basename='conference')
router.register(r'sessions', SessionViewSet, basename='session')
router.register(r'tickets', TicketViewSet, basename='ticket')
router.register(r'orders', OrderViewSet, basename='order')
router.register(r'payments', PaymentViewSet, basename='payment')
router.register(r'chatsessions', ChatSessionViewSet, basename='chatsession')
router.register(r'chatmessages', ChatMessageViewSet, basename='chatmessage')
router.register(r'userinteractions', UserInteractionViewSet, basename='userinteraction')
router.register(r'admin/events', AdminEventViewSet, basename='admin-event')
router.register(r'admin/users', AdminUserViewSet, basename='admin-user')
router.register(r'admin/orders', AdminOrderViewSet, basename='admin-order')
router.register(r'admin/payments', AdminPaymentViewSet, basename='admin-payment')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/register/', UserRegistrationView.as_view(), name='user-register'),
    path('api/dashboard/', AdminDashboardView.as_view(), name='admin-dashboard'),
    path('api/', include(router.urls)),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)