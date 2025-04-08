# Create your models here.

from django.db import models
from django.core.validators import MinValueValidator
from django.utils import timezone
import uuid

class Donation(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pendiente'),
        ('completed', 'Completada'),
        ('failed', 'Fallida'),
        ('refunded', 'Reembolsada'),
    ]

    # Información básica
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(1.00)],  # Mínimo 1€
        verbose_name="Cantidad (€)"
    )
    
    # Identificación de transacción
    transaction_id = models.CharField(
        max_length=100,
        unique=True,  # Evita duplicados
        verbose_name="ID de Transacción"
    )
    
    # Estado y seguimiento
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name="Estado"
    )
    response_code = models.CharField(
        max_length=10,
        blank=True,
        verbose_name="Código de Respuesta"
    )
    error_message = models.TextField(
        blank=True,
        verbose_name="Mensaje de Error"
    )
    
    # Datos temporales
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de creación")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Última actualización")
    
    # Campos adicionales para Redsys
    merchant_parameters = models.TextField(
        blank=True,
        verbose_name="Parámetros Redsys (Base64)"
    )
    raw_response = models.JSONField(
        blank=True,
        null=True,
        verbose_name="Respuesta Cruda"
    )

    class Meta:
        verbose_name = "Donación"
        verbose_name_plural = "Donaciones"
        ordering = ['-created_at']

    def __str__(self):
        return f"Donación #{self.transaction_id} - {self.amount}€ ({self.get_status_display()})"
    
    def save(self, *args, **kwargs):
        """Garantiza formato consistente del ID de transacción"""
        if not self.transaction_id:
            self.transaction_id = f"DON-{timezone.now().strftime('%Y%m%d-%H%M%S')}-{uuid.uuid4().hex[:6].upper()}"
        super().save(*args, **kwargs)
    
        

class Campaign(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    goal_amount = models.DecimalField(max_digits=10, decimal_places=2)
    current_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return self.name
    
    def progress_percentage(self):
        return (self.current_amount / self.goal_amount) * 100
