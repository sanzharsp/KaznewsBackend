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
from .pagination import CustomPagination

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
                        LikeSerilizer,
                        Post_id_Serilizer,
                        
                        )

from .models import News,last_News_date,Author


from .utils import captcha_gen,captcha_validetet


from captcha.models import CaptchaStore

from .auth import user

from newsprojects.settings import SIMPLE_JWT



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


class UserPostView(generics.ListAPIView):
    serializer_class=Last_News_Serilizer
    pagination_class = PageNumberPagination
    permission_classes = (IsAuthenticated,)

    def get(self,request):
        refresh_token_get = request.META.get('HTTP_AUTHORIZATION', ' ').split(' ')[1]
        jwt=JWT_.decode(
            refresh_token_get,
            SIMPLE_JWT['SIGNING_KEY'],
        algorithms = [SIMPLE_JWT['ALGORITHM']],
            )
        
        queryset=News.objects.filter(user=jwt['user_id'])
        serilaizers= self.get_serializer(queryset, many=True)
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
    serializer_class=Last_News_Serilizer
    pagination_class = CustomPagination
    def get(self, request):
      
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            result = self.get_paginated_response(serializer.data)
            data = result.data # pagination data
        else:
            serializer = self.get_serializer(queryset, many=True)
            data = serializer.data
        return Response(data)

    def get_queryset(self):
        return News.objects.filter(date_add__gte=(last_News_date.objects.filter(trues=True).first().last_news_date),published=True)
 

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
 
        

class LogoutViewV1(generics.GenericAPIView):
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


# система лайков продукта
class AddLike(generics.GenericAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = LikeSerilizer
    def post(self,request,*args,**kwargs):
        refresh_token_get = request.META.get('HTTP_AUTHORIZATION', ' ').split(' ')[1]
        jwt=JWT_.decode(
            refresh_token_get,
            SIMPLE_JWT['SIGNING_KEY'],
        algorithms = [SIMPLE_JWT['ALGORITHM']],
            )
        
        author=Author.objects.get(id=jwt['user_id'])
        posts=request.data['post']
        post=0
        try:
            post=News.objects.get(pk=posts)
        except ObjectDoesNotExist:
            data={"error":"post not found"}
            return Response(data,status=status.HTTP_404_NOT_FOUND)
        is_like=False
        for like in post.likes.all():
            if like==request.user:
                is_like=True
                break  
        if not is_like:
            post.likes.add(author)
            post.value='Like'   
        if is_like:
            post.likes.remove(author)
            post.value='Unlike'
          
        post.save()
        
        data={  
                'is_like':is_like,
                'post_like':post.likes.all().count(),
        }
        return Response(data, status=status.HTTP_201_CREATED)


#delete post
class DeletePostApi(generics.GenericAPIView):
    serializer_class=Post_id_Serilizer
    permission_classes = (IsAuthenticated,)
    def delete(self, request,pk, *args, **kwargs):
        refresh_token_get = request.META.get('HTTP_AUTHORIZATION', ' ').split(' ')[1]
        jwt=JWT_.decode(
            refresh_token_get,
            SIMPLE_JWT['SIGNING_KEY'],
        algorithms = [SIMPLE_JWT['ALGORITHM']],
            )
        author=Author.objects.get(id=jwt['user_id'])
        try:
            post=News.objects.get(id=pk)
        except ObjectDoesNotExist:
            data={"error":"post not found"}
            return Response(data,status=status.HTTP_404_NOT_FOUND)
        if (post.user.id == author.id):
            post.delete()
            return Response({'success': True},status=status.HTTP_200_OK)
        else:
            return Response({'success': False},status=status.HTTP_403_FORBIDDEN)

#post verify
class PostApiIdentificated(generics.GenericAPIView):
    serializer_class=Post_id_Serilizer
    #permission_classes = (IsAuthenticated,)
    def post(self, request, *args, **kwargs):
        refresh_token_get = request.META.get('HTTP_AUTHORIZATION', ' ').split(' ')[1]
        jwt=JWT_.decode(
            refresh_token_get,
            SIMPLE_JWT['SIGNING_KEY'],
        algorithms = [SIMPLE_JWT['ALGORITHM']],
            )
        author=Author.objects.get(id=jwt['user_id'])
        try:
            post=News.objects.get(id=request.data['post_id'])
        except ObjectDoesNotExist:
            data={"error":"post not found"}
            return Response(data,status=status.HTTP_404_NOT_FOUND)
        if (post.user.id == author.id):
            return Response({'post': True},status=status.HTTP_200_OK)
        else:
            return Response({'post': False},status=status.HTTP_403_FORBIDDEN)
