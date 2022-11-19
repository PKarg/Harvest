import decimal

from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.urls import reverse
from django.utils import timezone


# Create your models here.
class Harvest(models.Model):
    date = models.DateField(verbose_name="Date of harvest",
                            null=False,
                            default=timezone.now)

    FRUITS = (
        ("raspberry", "Raspberry"),
        ("strawberry", "Strawberry"),
        ("apple", "Apple"),
        ("cherry", "Cherry"),
    )

    fruit = models.CharField(verbose_name="Fruit harvested",
                             max_length=15, choices=FRUITS,
                             null=False, default='"raspberry')

    amount = models.IntegerField(verbose_name="Amount harvested",
                                 validators=[MinValueValidator(10),
                                             MaxValueValidator(5000)]
                                 )

    price = models.DecimalField(verbose_name="Price per kg",
                                max_digits=4,
                                decimal_places=2,
                                validators=[MinValueValidator(decimal.Decimal("0.1")),
                                            MaxValueValidator(decimal.Decimal("50.0"))])

    owner = models.ForeignKey(User, on_delete=models.CASCADE, null=True)

    class Meta:
        ordering = ["date"]
        constraints = [
            models.UniqueConstraint(fields=["date", "owner", "fruit"], name="unique_date_and_fruit_for_owner")
        ]

    @property
    def value(self):
        return self.price * self.amount

    def __str__(self):
        return f"{self.fruit.capitalize()} {self.date}"

    def get_absolute_url(self):
        return reverse('harvests:edit', kwargs={"pk": self.pk})
