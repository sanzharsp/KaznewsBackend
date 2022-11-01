from rest_framework import generics
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import status



from newsapp.serilaizers import PasswordResetSerilizer

from newsapp.utils import captcha_validetet

from newsapp.models import Author

from django.utils.datastructures import MultiValueDictKeyError




class PasswordResetAPI(generics.GenericAPIView):
    serializer_class=PasswordResetSerilizer

    def post(self,request):
        
        serializer = self.get_serializer(data=request.data)

        try:
            
            captcha_=captcha_validetet(request,hash_key=request.data['hashkey'],get_text=request.data['captcha_value'])
        except MultiValueDictKeyError:
            return Response({"captcha_value":"Капча не передана"},status=status.HTTP_400_BAD_REQUEST)
       
        if captcha_:
            serializer.is_valid(raise_exception=False)
            author=Author.objects.filter(email=request.data['email'])
            if author.exists():
                pass
            
            
            
        if not captcha_:
             return Response({'captcha_value':'Капча не валидна'}, status=status.HTTP_400_BAD_REQUEST)

        return Response({},status=status.HTTP_200_OK)
