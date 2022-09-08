import re # библиотека для регулярных выражений


from captcha.models import CaptchaStore
from captcha.helpers import captcha_image_url
from rest_framework.response import Response

#работа с датой
import pytz
import datetime

""" функция с использованием регулярных выпажений для удалений html тегов """

def html_tags_delete(html_string):

    res = re.sub(r"<[^>]+>", "",html_string, flags=re.S)

    return str(res)

def captcha_gen():

    key=CaptchaStore.generate_key()
    image=captcha_image_url(key)

    return {
        "key":key,
        'image_url':image
        }

def captcha_validetet(request,hash_key,get_text):

    CaptchaStore.remove_expired() #удаляем капчи у которых время истекло
    validate_upper=CaptchaStore.objects.filter(hashkey=hash_key,challenge=get_text)
    validate_lowwer=CaptchaStore.objects.filter(hashkey=hash_key,response=get_text)
    
    if validate_upper.exists() or validate_lowwer.exists():
        if validate_upper.exists():
            validate_upper.delete()
        if validate_lowwer.exists():
            validate_lowwer.delete()
            
        return True

    else:

        return False
        
def date_time_format():
      return "%Y-%m-%d %H:%M:%S"
      
def date_time_now():
    Almaty = pytz.timezone("Asia/Almaty") 
    timeInAlmaty = datetime.datetime.now(Almaty)
  
    currenttimeInAlmaty= timeInAlmaty.strftime(date_time_format())
    return currenttimeInAlmaty
