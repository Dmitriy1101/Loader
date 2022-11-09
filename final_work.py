import requests
import json
from datetime import datetime

class YaUploader:
  
    def __init__(self, token: str):
        self.token = token

    @property
    def header(self):
         return {"content-type": "application/json", 'Authorization': f'OAuth {self.token}'}

    def make_folder(self, file_list, path_folder = 'Photo'):
        '''Будем сохранять в папку "Photo" но можем и создать, так же проверяем файлы'''     
        resp = requests.put('https://cloud-api.yandex.net/v1/disk/resources', headers = self.header, params ={'path' : f'/{path_folder}'})
        if resp.status_code == 409:
            print(f'Папка {path_folder} уже существует')
            new_list = []
            for file in file_list:
                name = file.get('file_name')
                resp = requests.get('https://cloud-api.yandex.net/v1/disk/resources', headers = self.header, params ={'path' : f'/{path_folder}/{name}'})
                if resp.status_code == 200:
                    print(f'Файл {name} уже существует!')
                    new_list.append(file)            
            return new_list
        else:
            print(f'Папка {path_folder} создана')
            return []
  
    def upload(self, download_list):
        """Метод загружает файлы по списку на яндекс диск"""
        folder = 'NewSafe'
        file_list = self.make_folder(download_list[1], folder)
        if file_list != []:
            user_wish = input('Не копировать совпадающие файлы?(y/n)')        
            if user_wish != 'y' and user_wish != 'n':
                print(f'"{user_wish}" главное не "y", будем думать что "n"')
        else:
            user_wish ='nope'
        data_list = []
        for file, data in zip(download_list[0], download_list[1]):
            name = data.get('file_name')
            if data in file_list and user_wish == 'y':
                print(f'Файл {name} не будет отправлен')
                continue
            url = file.get('url')
            response = requests.post('https://cloud-api.yandex.net/v1/disk/resources/upload', headers = self.header, params ={'path' : f'/{folder}/{name}', 'url' : url})                
            print(f'Отправляем {name}')                    
            if response.status_code == 202:
                print('Сделано')
                data_list.append(data)
            elif response.status_code == 403:
                print('Мало места на даске')
            else:
                print(f'error {response.status_code}')     
        if data_list != []:     
            info_name = datetime.now().strftime("%H_%M_%S")
            print('Отправляем файл с информацией по загрузке')
            response = requests.get('https://cloud-api.yandex.net/v1/disk/resources/upload', headers = self.header, params ={'path' : f'/{folder}/file_info_{info_name}.json'})
            upload_way = response.json().get('href')
            resp = requests.put(upload_way, data=json.dumps(download_list[1]), headers = self.header)    
            if resp.status_code == 201:
                print('Успех')
            else:
              print(resp.status_code)
        else:
            print('Нечего отправлять')

class VK:

    def __init__(self, user_id, version='5.131'):
        self.token = 'Фирменный интернет-магазин ножей и кинжалов ООО ПП «КИЗЛЯР»: https://kizlyar-shop.ru/'
        self.id = user_id
        self.version = version
        self.params = {'access_token': self.token, 'v': self.version}

    def users_info(self):
        '''Тест запрос'''
        url = 'https://api.vk.com/method/users.get'
        params = {'user_ids': self.id}
        response = requests.get(url, params={**self.params, **params})
        return response.json()

    def get_photo_list(self):
        '''Запрос для фото'''
        url = 'https://api.vk.com/method/photos.get'
        params = {'user_ids': self.id, 'album_id': 'profile', 'extended': '1'}
        response = requests.get(url, params={**self.params, **params})
        return response.json()

    def take_photo_list(self):
        '''Создаём список файлов и описание к ним'''
        all_photo_info = vk.get_photo_list()
        items = all_photo_info.get('response').get('items')#список        
        file_list = []
        file_info = []
        for file in items:
            d = {}
            file_list.append(self.get_max_size_photo(file.get('sizes')))
            likes_count =file.get('likes').get('count')
            file_name = f'{likes_count}.jpg'          
            if file_info == [] or self.find_name(file_name, file_info):
                print(f'Изменение имени {file_name} не требуется')
            else:
                date = file.get('date')
                print(f'Изменение имени {file_name} на {likes_count}_{date}.jpg')
                file_name = f'{likes_count}_{date}.jpg'
            d ['file_name'] = file_name
            d['size']= file_list[-1]['type'] 
            file_info.append(d)
            print(file_name)
        print('Сформерован список загрузки')
        return [file_list, file_info]

    def get_max_size_photo(self, size_list):
        '''Находим самое БОЛЬШОЕ фото'''
        size = 0
        for file in size_list:
            if size < file.get('height') + file.get('width'):
                size = file.get('height') + file.get('width')
                it_max = file
        return it_max

    def find_name(self, name, info_list):
        '''Проверяем совпадения имен'''
        for file in info_list:
            if file.get('file_name') == name:
               return False
        return True
 

user_id = 'По вопросам рекламы писать в л/с'
access_token_y = 'Тут могла быть ваша реклама'
vk = VK(user_id)
uploader = YaUploader(access_token_y)
uploader.upload(vk.take_photo_list())