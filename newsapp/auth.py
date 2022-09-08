
from rest_framework_simplejwt.authentication import JWTAuthentication
def user(request):
    jwt_object      = JWTAuthentication() 
    header          = jwt_object.get_header(request)
    raw_token       = jwt_object.get_raw_token(header)
    validated_token = jwt_object.get_validated_token(raw_token)
    user            = jwt_object.get_user(validated_token)

    return user