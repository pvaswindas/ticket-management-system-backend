from django.db import models
from accounts.models import User

PRIORITY_CHOICES = [
    ('low', 'Low'),
    ('medium', 'Medium'),
    ('high', 'High')
]

STATUS_CHOICES = [
    ('open', 'Open'),
    ('in-progress', 'In-Progress'),
    ('resolved', 'Resolved')
]


class Ticket(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    priority = models.CharField(
        max_length=10,
        choices=PRIORITY_CHOICES,
        default='low'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='open'
    )
    created_user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
    )
    assigned_to = models.CharField(
        max_length=255,
        null=True,
        blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if self.assigned_to and self.status == 'open':
            self.status = 'in-progress'
        super().save(*args, **kwargs)
