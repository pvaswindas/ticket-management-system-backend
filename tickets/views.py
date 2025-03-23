from rest_framework.permissions import IsAuthenticated
from rest_framework import viewsets
from .models import Ticket
from .serializers import TicketSerializer
from rest_framework.exceptions import PermissionDenied
from .permissions import IsOwnerOrAdmin, CanEditTicket
from .pagination import TicketPagination
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters


class TicketViewSet(viewsets.ModelViewSet):
    queryset = Ticket.objects.all().order_by('-created_at')
    serializer_class = TicketSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrAdmin, CanEditTicket]
    pagination_class = TicketPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['status', 'priority']

    def perform_create(self, serializer):
        if self.request.user.is_staff:
            raise PermissionDenied(
                "Admins cannot create tickets."
            )
        serializer.save(created_user=self.request.user)

    def get_queryset(self):
        if self.request.user.is_staff:
            return Ticket.objects.all().order_by('-created_at')
        return Ticket.objects.filter(created_user=self.request.user)
