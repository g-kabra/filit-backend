"""
Includes functions for the login app.
"""

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