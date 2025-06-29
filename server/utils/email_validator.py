from email_validator import validate_email, EmailNotValidError
import dns.resolver

def is_valid_email(email: str) -> bool:
    try:
        valid = validate_email(email)
        domain = valid["domain"]
        # Check for MX records (indicates valid domain for email)
        dns.resolver.resolve(domain, 'MX')
        return True
    except (EmailNotValidError, dns.resolver.NoAnswer, dns.resolver.NXDOMAIN):
        return False
