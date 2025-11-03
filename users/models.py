from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    ROLE_CHOICES = (
        ('CUSTOMER', 'Customer'),
        ('ADMIN', 'Admin'),
        ('KITCHEN', 'Kitchen Staff'),
        ('DELIVERY', 'Delivery Partner'),
    )

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='CUSTOMER')

    def __str__(self):
        return f"{self.username} ({self.role})"
