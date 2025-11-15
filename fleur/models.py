# fleur/models.py
from django.db import models
from decimal import Decimal


class Distributor(models.Model):
    name = models.CharField(max_length=120)
    serial_number = models.CharField(max_length=64, unique=True)
    location = models.CharField(max_length=255, blank=True)
    is_online = models.BooleanField(default=False)
    last_heartbeat = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.name} ({self.serial_number})"


class Bouquet(models.Model):
    name = models.CharField(max_length=120)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to="bouquets/", blank=True, null=True)

    def __str__(self):
        return self.name


class Slot(models.Model):
    distributor = models.ForeignKey(Distributor, on_delete=models.CASCADE, related_name="slots")
    index = models.PositiveIntegerField()  # numéro de case = 1,2,3...
    label = models.CharField(max_length=20, blank=True)  # "Porte 1", "Case A1"...
    capacity = models.PositiveIntegerField()
    quantity = models.PositiveIntegerField(default=0)
    bouquet = models.ForeignKey(Bouquet, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        unique_together = ("distributor", "index")

    def __str__(self):
        return f"{self.distributor} - Slot {self.index}"


class OrderStatus(models.TextChoices):
    PENDING_PAYMENT = "PENDING_PAYMENT", "En attente paiement"
    PAID = "PAID", "Payée"
    VENDING = "VENDING", "Distribution en cours"
    COMPLETED = "COMPLETED", "Terminée"
    FAILED = "FAILED", "Échec"


class Order(models.Model):
    distributor = models.ForeignKey(Distributor, on_delete=models.CASCADE, related_name="orders")
    slot = models.ForeignKey(Slot, on_delete=models.PROTECT)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    inserted_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    status = models.CharField(
        max_length=32, choices=OrderStatus.choices, default=OrderStatus.PENDING_PAYMENT
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def is_fully_paid(self):
        return self.inserted_amount >= self.amount

    def add_credit(self, cents: int):
        self.inserted_amount += Decimal(cents)
        if self.is_fully_paid() and self.status == OrderStatus.PENDING_PAYMENT:
            self.status = OrderStatus.PAID
        self.save()
