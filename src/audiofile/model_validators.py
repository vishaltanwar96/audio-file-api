from django.utils import timezone
from django.core.exceptions import ValidationError


def past_validator(value):
    """Checks whether the datetime value provided is of past"""

    if value < timezone.now():
        raise ValidationError("cannot be past date")
