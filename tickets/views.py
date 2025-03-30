from rest_framework.permissions import IsAuthenticated
from rest_framework import viewsets
from .models import Ticket
from .serializers import TicketSerializer
from rest_framework.exceptions import PermissionDenied
from .permissions import IsOwnerOrAdmin, CanEditTicket
from .pagination import TicketPagination
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from django.db.models import Count
from django.db.models.functions import TruncMonth
from datetime import datetime
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser


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


class TicketStatsView(APIView):
    """
    API endpoint to provide ticket statistics for the admin dashboard
    """
    permission_classes = [IsAdminUser]

    def get(self, request):
        total_tickets = Ticket.objects.count()
        open_tickets = Ticket.objects.filter(status='open').count()
        in_progress_tickets = Ticket.objects.filter(
            status='in-progress'
        ).count()
        resolved_tickets = Ticket.objects.filter(status='resolved').count()

        tickets_by_priority = {
            'low': Ticket.objects.filter(priority='low').count(),
            'medium': Ticket.objects.filter(priority='medium').count(),
            'high': Ticket.objects.filter(priority='high').count()
        }

        current_year = datetime.now().year
        ticket_creation_by_month = [0] * 12

        tickets_by_month = Ticket.objects.filter(
            created_at__year=current_year
        ).annotate(
            month=TruncMonth('created_at')
        ).values('month').annotate(
            count=Count('id')
        ).order_by('month')

        for entry in tickets_by_month:
            month_idx = entry['month'].month - 1
            ticket_creation_by_month[month_idx] = entry['count']

        recent_tickets = Ticket.objects.all().order_by('-created_at')[:5]
        recent_tickets_data = []

        for ticket in recent_tickets:
            recent_tickets_data.append({
                'id': ticket.id,
                'title': ticket.title,
                'priority': ticket.priority,
                'status': ticket.status,
                'createdAt': ticket.created_at.strftime('%Y-%m-%d'),
                'assignedTo': ticket.assigned_to
            })

        return Response({
            'totalTickets': total_tickets,
            'openTickets': open_tickets,
            'inProgressTickets': in_progress_tickets,
            'resolvedTickets': resolved_tickets,
            'ticketsByPriority': tickets_by_priority,
            'ticketCreationByMonth': ticket_creation_by_month,
            'ticketsByStatus': [
                open_tickets, in_progress_tickets, resolved_tickets
            ],
            'recentTickets': recent_tickets_data
        })


class UserTicketStatsView(APIView):
    """API endpoint to provide ticket statistics for the user dashboard"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        status_counts = Ticket.objects.filter(
            created_user=request.user
        ).values('status').annotate(
            count=Count('id')
        ).order_by()

        counts = {
            'open': 0,
            'in-progress': 0,
            'resolved': 0,
        }

        for item in status_counts:
            counts[item['status']] = item['count']

        total_tickets = sum(counts.values())

        return Response({
            'totalTickets': total_tickets,
            'openTickets': counts['open'],
            'inProgressTickets': counts['in-progress'],
            'resolvedTickets': counts['resolved']
        })
