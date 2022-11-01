import requests
API_KEY='kz3c6481f69ebd537dfa4365a281445f83190d546a9eeb0702711b949f2a778f5089d9'




#data_2=requests.post('https://api.mobizon.kz/service/message/sendsmsmessage?recipient=+77761827619&from=&text=Сброс пароля+852442%21&apiKey=kz3c6481f69ebd537dfa4365a281445f83190d546a9eeb0702711b949f2a778f5089d9')

#print(data_2.json())
#{'code': 0, 'data': {'balance': '40.2000', 'currency': 'KZT'}, 'message': ''}


def correct_key():
    request=requests.post('https://api.mobizon.kz/service/user/getownbalance?apiKey={}'.format(API_KEY))
    if request.json()['code']==8:
        return False
    elif request.json()['code']==0:
        return True



def get_balance():
    request_balance=requests.post('https://api.mobizon.kz/service/user/getownbalance?apiKey={}'.format(API_KEY))
    if correct_key():
        return int(float(request_balance.json()['data']['balance']))
    if not correct_key():
        return "Токен для смс API не действителен"




def send_message(number,signature,organization,text):
    if correct_key():
        request_send_sms=requests.post('https://api.mobizon.kz/service/message/sendsmsmessage?recipient={}&from={}&text={}\n+{}%21&apiKey={}'.format(number,signature,organization,text,API_KEY))
        if request_send_sms.json()['code']==0:
            return True
        if  get_balance()<15:
          
            return False
        else:
            return request_send_sms.json()['message']
    if not correct_key():
        return "Токен для смс API не действителен"






