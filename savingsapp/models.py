# savings_app/models.py

from django.db import models
from datetime import date


class Contribution(models.Model):
    """
    Represents a single financial contribution.
    Amount is stored as an Integer, suitable for Ugandan Shillings (UGX).
    """

    # Member's Full Name
    name = models.CharField(
        max_length=100,
        verbose_name="Member Name"
    )

    # Contribution Amount (Changed to IntegerField for UGX)
    amount = models.IntegerField(
        verbose_name="Amount Contributed (UGX)"
    )

    # Date of Contribution
    date = models.DateField(
        default=date.today,
        verbose_name="Date"
    )

    class Meta:
        ordering = ['date', 'name']
        verbose_name = "Contribution"
        verbose_name_plural = "Contributions"

    def __str__(self):
        # Format the amount clearly for display
        return f"{self.name} - UGX {self.amount:,} on {self.date.isoformat()}"