from django.core.exceptions import ObjectDoesNotExist
from django.utils.datastructures import MultiValueDictKeyError


from rest_framework import generics
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.permissions import AllowAny,IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework.pagination import PageNumberPagination
from rest_framework_simplejwt.views import TokenObtainPairView


import jwt as JWT_


from .serilaizers import RegistrationSerializer
from .serilaizers  import (
                        NewsSerilaizers,
                        Last_News_Serilizer,
                        LogoutSerilizers,
                        PostCreatedSerilaizers,
                        SearchSerilizer,
                        AuthorizateSerializer,
                        AuthorSerilizer,
                        AuthorDetailSerilizer,
                        
                        )

from .models import News,last_News_date,Author


from .utils import captcha_gen,captcha_validetet,date_time_format


from captcha.models import CaptchaStore

from .auth import user

from newsprojects.settings import TIME_ZONE,SIMPLE_JWT
   
import pytz
import datetime


# Refresh TokenObtainPairView (add user)
class AuthorizateView(TokenObtainPairView):
    serializer_class= AuthorizateSerializer
    


class ProfileView(generics.GenericAPIView):
    serializer_class=AuthorSerilizer
    permission_classes = (IsAuthenticated,)
    def get(self,request):
        refresh_token_get = request.META.get('HTTP_AUTHORIZATION', ' ').split(' ')[1]
        jwt=JWT_.decode(
            refresh_token_get,
            SIMPLE_JWT['SIGNING_KEY'],
        algorithms = [SIMPLE_JWT['ALGORITHM']],
            )
        
        queryset=Author.objects.get(id=jwt['user_id'])
        serilaizers= self.get_serializer(queryset)
        return Response(serilaizers.data)

class ProfileDetailView(generics.GenericAPIView):
    serializer_class=AuthorDetailSerilizer
    permission_classes = (IsAuthenticated,)
    def get(self,request):
        refresh_token_get = request.META.get('HTTP_AUTHORIZATION', ' ').split(' ')[1]
        jwt=JWT_.decode(
            refresh_token_get,
            SIMPLE_JWT['SIGNING_KEY'],
        algorithms = [SIMPLE_JWT['ALGORITHM']],
            )
        
        queryset=Author.objects.get(id=jwt['user_id'])
        serilaizers= self.get_serializer(queryset)
        return Response(serilaizers.data,status=status.HTTP_200_OK)

 

 

    
class News_Views(generics.ListAPIView):
    queryset=News.objects.filter(published=True)
    serializer_class = NewsSerilaizers
    pagination_class = PageNumberPagination




class Post_News(generics.GenericAPIView):
    serializer_class = PostCreatedSerilaizers
    permission_classes = (IsAuthenticated,)
    
    def post(self,request):
        # Паттерн создания сериализатора, валидации и сохранения - довольно
        # стандартный, и его можно часто увидеть в реальных проектах.
        
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        if str(user(request)) == str(request.data['user']): 
            serializer.save()
            return Response({"sucess":"Ваш пост создался"},status=status.HTTP_200_OK)
        else:
          
            return Response({"error":"Имя пользователя не было передана или он подменен"},status=status.HTTP_401_UNAUTHORIZED)

        
    

class MainNews(generics.ListAPIView):
    queryset=News.objects.filter(main_news=True,published=True)
    serializer_class = NewsSerilaizers
    pagination_class = PageNumberPagination
    


class Last_News_Views(generics.ListAPIView):
    Almaty = pytz.timezone(TIME_ZONE)
    timeInAlmaty = datetime.datetime.now(Almaty)
    currenttimeInAlmaty= timeInAlmaty.strftime(date_time_format())
    queryset = News.objects.filter(date_add__range=(last_News_date.objects.filter(trues=True).first().last_news_date,
                datetime.datetime.strptime(currenttimeInAlmaty,date_time_format())),
                published=True)
    serializer_class=Last_News_Serilizer
    pagination_class = PageNumberPagination
       
 

class GetPost(APIView):
    serializer_class = NewsSerilaizers

    def get(self,request,pk):
        try:
            queryset = self.get_queryset(pk)
        except ObjectDoesNotExist:
            return Response([{"error":"Токого поста не существует"},])
        serializer = NewsSerilaizers(queryset)

        return Response([serializer.data])

    def get_queryset(self,pk):
        
        return News.objects.get(id=pk,published=True)


class SearchPostAPI(APIView):
    serializer_class = SearchSerilizer
 
    def get(self,request):
   

        queryset = self.get_queryset()
        serializer = SearchSerilizer(queryset, many=True)

        return Response(serializer.data)

    def get_queryset(self):
        
        return News.objects.filter(published=True)




                                                #########################################
                                                            #AUTH
                                                #########################################
class RegistrationAPIView(generics.GenericAPIView):
    
    """
    Разрешить всем пользователям (аутентифицированным и нет) доступ к данному эндпоинту.
    """
    permission_classes = (AllowAny,)
    serializer_class = RegistrationSerializer


    def get(self,request):
        CaptchaStore.remove_expired() #удаляем капчи у которых время истекло
        return Response(captcha_gen())   


    def post(self, request):
        

        # Паттерн создания сериализатора, валидации и сохранения - довольно
        # стандартный, и его можно часто увидеть в реальных проектах.
        
        serializer = self.get_serializer(data=request.data)

        try:
            
            captcha_=captcha_validetet(request,hash_key=request.data['hashkey'],get_text=request.data['captcha_value'])
        except MultiValueDictKeyError:
            return Response({"captcha_value":"Капча не передана"},status=status.HTTP_400_BAD_REQUEST)
       
        if captcha_:
            serializer.is_valid(raise_exception=True)


            serializer.save()
            user=Author.objects.get(username=serializer.data['username'],email=serializer.data['email'])
            refresh = RefreshToken.for_user(user)
            return Response({'user':serializer.data,      
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                    }, status=status.HTTP_201_CREATED)
        if not captcha_:
             return Response({'captcha_value':'Капча не валидна'}, status=status.HTTP_400_BAD_REQUEST)
 
        

class LogoutView(generics.GenericAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class=LogoutSerilizers
    def post(self, request):
        try:
            try:
                refresh_token = request.data["refresh_token"]
            except KeyError:
                return Response({'refresh_token':' refresh_token не был передан'},status=status.HTTP_400_BAD_REQUEST)
            token = RefreshToken(refresh_token)
            token.blacklist()

            return Response({"detail": "Токен занесен в черный список",
                        "code": "token_blacklisted",
    "messages": [
        {
            "token_class": "AccessToken",
            "token_type": "access",
            "message": "Токен занесен в черный список"
        }]},
        status=status.HTTP_205_RESET_CONTENT)
        except TokenError:
            return Response({"detail": "Данный в черном списке",
                        "code": "the_token_is_already_blacklisted",
    "messages": [
        {
            "token_class": "AccessToken",
            "token_type": "access",
            "message": "Токен уже в черном списке"
        }
    ]},status=status.HTTP_400_BAD_REQUEST)



