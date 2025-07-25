import re
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _

def validate_no_symbols(password, user=None):
    """
    Raises a ValidationError if the password contains any symbol.
    Only letters and digits are allowed.
    """
    if re.search(r'[^a-zA-Z0-9]', password):
        raise ValidationError(
            _("Password must not contain any symbols."),
            code='password_no_symbols'
        )
