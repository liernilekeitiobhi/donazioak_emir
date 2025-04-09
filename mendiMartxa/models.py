from django.db import models
from django.core.validators import MinValueValidator
from django.utils import timezone
import uuid
from django.conf import settings

class Donation(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pendiente'),
        ('completed', 'Completada'),
        ('failed', 'Fallida'),
    ]

    CAMPAIGN_CHOICES = ['donazioa', 'mendi-martxa']

    campaign = models.CharField(
        max_length=100,
        coices=CAMPAIGN_CHOICES,
        verbose_name="Campaña"
    )

    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(1.00)],
        verbose_name="Cantidad (€)"
    )
    
    transaction_id = models.CharField(
        max_length=100,
        unique=True,
        verbose_name="ID de Transacción"
    )
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )
    
    response_code = models.CharField(
        max_length=10,
        blank=True,
        verbose_name="Código de Respuesta"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Donación #{self.transaction_id} - {self.amount}€"

    def save(self, *args, **kwargs):
        if not self.transaction_id:
            self.transaction_id = f"DON-{timezone.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"
        super().save(*args, **kwargs)

    @classmethod
    def get_total_raised(cls):
        return cls.objects.filter(status='completed').aggregate(
            total=models.Sum('amount')
        )['total'] or 0.00

    @classmethod
    def get_progress_percentage(cls):
        total = cls.get_total_raised()
        return (total / settings.CAMPAIGN_GOAL) * 100