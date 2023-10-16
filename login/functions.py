"""
Includes functions for the login app.
"""

from .models import CustomUser, UserTotalSavings

def make_response(details="", data=None, status=200, errors=None):
    """
    DESCRIPTION
        This function will return the response in the required format.
    """
    ret: dict = {
        'statusCode': status,
    }
    if details:
        ret['message'] = details
    if data:
        ret['result'] = data
    if not errors:
        errors = []
    ret['errors'] = errors
    return ret

def start_investment(user: CustomUser):
    """
    DESCRIPTION
        This function will start the investment for the user.
    """
    savings = UserTotalSavings.objects.get(user=user)
    amount = savings.current_savings
    savings.current_savings = 0
    savings.save()
    