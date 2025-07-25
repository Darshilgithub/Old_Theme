from django.core.exceptions import ValidationError

def validate_email_domain(email):
    allowed_domains = ['vulnix.org', 'gmail.com']
    try:
        domain = email.split('@')[1]
    except IndexError:
        raise ValidationError("Invalid email format.")

    if domain.lower() not in allowed_domains:
        raise ValidationError("Only emails from vulnix.org or gmail.com are allowed.")
