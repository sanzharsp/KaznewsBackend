from django.db import models
from django.conf import settings 
from django.contrib.auth.models import (
	AbstractBaseUser, PermissionsMixin
)

import jwt
from datetime import datetime, timedelta
from ckeditor.fields import RichTextField # староняя библиотека для работы текстом
from .utils import html_tags_delete # кастомная функция для удаления html тегов

from .Manager import UserManager






class Author(AbstractBaseUser, PermissionsMixin):
    
    # Каждому пользователю нужен понятный человеку уникальный идентификатор,
    # который мы можем использовать для предоставления User в пользовательском
    # интерфейсе. Мы так же проиндексируем этот столбец в базе данных для
    # повышения скорости поиска в дальнейшем.
    username = models.CharField(db_index=True, max_length=255,verbose_name='Логин', unique=True)
    first_name=models.CharField(db_index=True,verbose_name='Имя',max_length=150)
    last_name=models.CharField(db_index=True,verbose_name='Фамилия',max_length=150)
    surname=models.CharField(db_index=True,verbose_name='Отчество',max_length=150)
    email=models.EmailField(db_index=True,verbose_name='электоронная почта', unique=True)
        
    # Когда пользователь более не желает пользоваться нашей системой, он может
    # захотеть удалить свой аккаунт. Для нас это проблема, так как собираемые
    # нами данные очень ценны, и мы не хотим их удалять :) Мы просто предложим
    # пользователям способ деактивировать учетку вместо ее полного удаления.
    # Таким образом, они не будут отображаться на сайте, но мы все еще сможем
    # далее анализировать информацию.
    is_active = models.BooleanField(default=True)

    # Этот флаг определяет, кто может войти в административную часть нашего
    # сайта. Для большинства пользователей это флаг будет ложным.
    is_staff = models.BooleanField(default=False,verbose_name='Персонал')

    # Временная метка создания объекта.
    created_at = models.DateTimeField(auto_now_add=True)

    # Временная метка показывающая время последнего обновления объекта.
    updated_at = models.DateTimeField(auto_now=True)

    # Дополнительный поля, необходимые Django
    # при указании кастомной модели пользователя.

    # Свойство USERNAME_FIELD сообщает нам, какое поле мы будем использовать
    # для входа в систему. В данном случае мы хотим использовать почту.
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email','first_name','last_name','surname']

    # Сообщает Django, что определенный выше класс UserManager
    # должен управлять объектами этого типа.
    objects = UserManager()
    
    
    
    class Meta:
        ordering = ['id']
        verbose_name='Автор'
        verbose_name_plural='Авторы'

    def __str__(self):
        return "{} {} {}".format(self.first_name,self.last_name,self.surname)

    @property
    def token(self):
        """
        Позволяет получить токен пользователя путем вызова Author.token, вместо
        user._generate_jwt_token(). Декоратор @property выше делает это
        возможным. token называется "динамическим свойством".
        """
        return self._generate_jwt_token()

    def get_full_name(self):
        """
        Этот метод требуется Django для таких вещей, как обработка электронной
        почты. Обычно это имя фамилия пользователя, но поскольку мы не
        используем их, будем возвращать username.
        """
        return self.username

    def get_short_name(self):
        """ Аналогично методу get_full_name(). """
        return self.username

    def _generate_jwt_token(self):
        """
        Генерирует веб-токен JSON, в котором хранится идентификатор этого
        пользователя, срок действия токена составляет 1 день от создания
        """
        dt = datetime.now() + timedelta(days=1)

        token = jwt.encode({
            'id': self.pk,
            'exp': int(dt.strftime('%S'))
        }, settings.SECRET_KEY, algorithm='HS256')

        return token

class News(models.Model):
    user=models.ForeignKey(Author, verbose_name='Автор', on_delete=models.CASCADE)
    title= RichTextField(db_index=True,verbose_name='Наименования новости' )
    context=RichTextField(db_index=True,verbose_name='Краткое описание новости' )
    image1= models.ImageField(db_index=True,blank=True,verbose_name='Изображения')
    image2= models.ImageField(db_index=True,null=True, blank=True,verbose_name='Изображения')
    image3= models.ImageField(db_index=True,null=True, blank=True,verbose_name='Изображения')
    date_add= models.DateTimeField(db_index=True,auto_now=True,verbose_name='Дата создания ленты')
    content_text= RichTextField(db_index=True,verbose_name='Текст новости')
    main_news=models.BooleanField(db_index=True,verbose_name='Главные новости', default=False)
    category=models.CharField(db_index=True,default="новая запись" ,max_length=150,verbose_name="Категория")
    published=models.BooleanField(db_index=True,verbose_name='Публиковать', default=False)

    
    class Meta:
        ordering = ['-id']
        verbose_name='Пост'
        verbose_name_plural='Посты'

    def __str__(self):
        return html_tags_delete(self.title)

    def get_full_name(self):
        '''
        Returns the first_name plus the last_name, with a space in between.
        '''
        full_name = '%s %s' % (self.user.username)
        return full_name.strip()
        

class last_News_date(models.Model):
    trues=models.BooleanField(default=False,verbose_name='Этот период')
    last_news_date= models.DateTimeField(verbose_name='Период для недавных новостей')
    


    class Meta:
        ordering = ['id']
        verbose_name='Последние новости'
        verbose_name_plural='Последние новости'

    def __str__(self):
        return "{}".format(self.last_news_date)


