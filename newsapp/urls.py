from django.urls import path


from .views import (Post_News,                           
                    RegistrationAPIView,
                    News_Views,MainNews,
                    Last_News_Views,GetPost,
                    LogoutView,
                    SearchPostAPI,
                    AuthorizateView
                    )
 

from rest_framework_simplejwt.views import (
    TokenRefreshView,
    TokenVerifyView,
)


urlpatterns = [
    #auth
    path('api/v1/register/', RegistrationAPIView.as_view()),
    path('api/v1/login/', AuthorizateView.as_view(), name='token_obtain_pair'),
    path('api/v1/login/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/v1/logout/', LogoutView.as_view(), name='auth_logout'),
    path('api/v1/token/verify/', TokenVerifyView.as_view(), name='token_verify'),


    #get
    path('', News_Views.as_view()),
    path('api/v1/news/get/main_news',MainNews.as_view()),
    path('api/v1/news/get/last_news',Last_News_Views.as_view()),
    path('api/v1/news/get/content/<int:pk>',GetPost.as_view()),
    path('api/v1/news/get/search',SearchPostAPI.as_view()),
    


    #post
    path('api/v1/news/post/new_post',Post_News.as_view()),

    

  

]
