from django.contrib import admin

from .models import News,last_News_date,Author

from .utils import html_tags_delete # кастомная функция для удаления html тегов

from django.contrib.auth.admin import UserAdmin

from captcha.models import CaptchaStore




class NewsAdmin(admin.ModelAdmin):
    list_display = ('get_author','date_add')
    
    
    @admin.display(ordering='title', description='News')
    def get_author(self, obj):
        return html_tags_delete(obj.title)

class Last_News_Date_Admin(admin.ModelAdmin):
    list_display = ('last_news_date',)



class Author_Admin(UserAdmin):
    model = Author
    list_display = ('username', 'is_superuser','is_staff')
    list_filter = ('username', 'is_superuser', 'first_name','last_name')
    fieldsets = (
        (None, {'fields': ('username', 'password', 'first_name','last_name','surname','email',)}),
        ('Права доступа и потверждение', {'fields': ('is_staff','is_superuser')}),
        
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2', 'first_name','last_name','surname','email',)},
            
        ),
         ('Права доступа и потверждение', {'fields': ('is_staff','is_superuser')}),
    )
    search_fields = ('username',)
    ordering = ('username',)


class CaptchaStoreAdmin(admin.ModelAdmin):
    CaptchaStore._meta.verbose_name ="Каптча"
    CaptchaStore._meta.verbose_name_plural ="Каптчы"



# Register your models here.
admin.site.register(News)
admin.site.register(Author,Author_Admin)
admin.site.register(last_News_date,Last_News_Date_Admin)
admin.site.register(CaptchaStore,CaptchaStoreAdmin)


admin.site.site_header="Новостная лента" # Шапка приложения

admin.site.site_title="Новости" # Титулка приложения





