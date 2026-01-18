from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.forms import ValidationError
from django.conf import settings

class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    def is_open_for_signup(self, request, sociallogin):
        """
        Checks if the email domain matches bits lmao.
        """
        user_email = sociallogin.user.email or ""
        allowed_domain = getattr(settings, 'ALLOWED_SIGNUP_DOMAIN', None)
        if not allowed_domain:
            return True
        if not user_email.endswith(allowed_domain):
            raise ValidationError(f"Only emails from {allowed_domain} are allowed.")
        return True