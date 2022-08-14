from re import I
from rest_framework import serializers
from .models import News
from .models import Author

from django.core.exceptions import ObjectDoesNotExist


class NewsSerilaizers(serializers.ModelSerializer):
  
    class Meta:
        model = News
        fields = (
                'id',
                'user',
                'title',
                'context',
                'image1',
                'image2',
                'image3',
                'date_add',
                'content_text',
                'main_news',
                'category')




class PostCreatedSerilaizers(serializers.ModelSerializer):
    user=serializers.CharField(

        label=("Логин Автора"),
        write_only=True

            )
    title=serializers.CharField(

        label=("Наименование Поста"),
        write_only=True

            )
    context=serializers.CharField(

        label=("Краткое описание поста"),
        write_only=True

            )

    content_text=serializers.CharField(

        label=("Текст поста"),
        write_only=True

            )
    image1=serializers.ImageField(
        label=("Изображение 1"),
        write_only=True,
        required=True
    )
    image2=serializers.ImageField(
        label=("Изображение 2"),

        write_only=True,
       
    )
    image3=serializers.ImageField(
        label=("Изображение 3"),
        write_only=True,
       
    )
    main_news=serializers.BooleanField(
        label=("Пост в главные"),
        write_only=True,
     
    )
    category=serializers.CharField(

        label=("Категория поста"),
        write_only=True

            )
    class Meta:
        model = News
        fields = ('user',
                'title',
                'context',
                'image1',
                'image2',
                'image3',
                'content_text',
                'main_news',
                'category',)

    def create(self, validated_data):
     
        try:
          
                des_characteristic = News.objects.update_or_create(
                                        user=Author.objects.get(username=validated_data['user']),
                                        title=validated_data['title'],
                                        context=validated_data['context'],
                                        image1=validated_data['image1'],
                                        image2=validated_data['image2'],
                                        image3=validated_data['image3'],
                                        content_text=validated_data['content_text'],
                                        main_news=validated_data['main_news'],
                                        category=validated_data['category'],

                                        )



        except ObjectDoesNotExist:
            msg = ('Такого Автора не существует')
            raise serializers.ValidationError(str(msg), code='characteristic')
        return des_characteristic

class AuthorSerilizerUsername(serializers.ModelSerializer):
    
    class Meta:
        model = Author
        fields = 'username','first_name','last_name'

class SearchSerilizer(serializers.ModelSerializer):
      user=AuthorSerilizerUsername()
      class Meta:
        model = News
        fields = (
                'id',
                'user',
                'title',
                'category',
                'image1',
                'context',
                'date_add'
                )


class AuthorSerilizer(serializers.ModelSerializer):
    
    class Meta:
        model = Author
        fields = 'first_name','last_name','username'

class Last_News_Serilizer(serializers.ModelSerializer):
    user=AuthorSerilizer()

    
    class Meta:
        model= News
        fields = ('id','title','image1','category','user','context','date_add')



class RegistrationSerializer(serializers.ModelSerializer):
    """ Сериализация регистрации пользователя и создания нового. """

    # Убедитесь, что пароль содержит не менее 8 символов, не более 128,
    # и так же что он не может быть прочитан клиентской стороной


    password = serializers.CharField(
        max_length=128,
        min_length=8,
        write_only=True,
        label="Пароль"

    )

    # Клиентская сторона не должна иметь возможность отправлять токен вместе с
    # запросом на регистрацию. Сделаем его доступным только на чтение.


    class Meta:
        model = Author
        # Перечислить все поля, которые могут быть включены в запрос
        # или ответ, включая поля, явно указанные выше.
        fields = ['username','first_name','last_name','surname','email', 'password']

    def create(self, validated_data):

        # Использовать метод create_user, который мы
        # написали ранее, для создания нового пользователя.
      
        return  Author.objects.create_user(**validated_data)
        


class LogoutSerilizers(serializers.Serializer):
    refresh_token = serializers.CharField(
        write_only=True,
        label="Refresh токен"

    )