#!/usr/bin/python3
# -*- coding: utf-8 -*-

#--------------------------------------------------------------

from aiogram import Bot, Dispatcher, executor, types
from bs4 import BeautifulSoup
from mp3_tagger import MP3File, VERSION_1, VERSION_2, VERSION_BOTH
import requests, urllib, os, re, logging

#--------------------------------------------------------------

logging.basicConfig(level = logging.DEBUG, format = '%(asctime)s : %(levelname)s : %(message)s')

bot_token = os.environ.get('BOT_TOKEN')

bot = Bot(token=bot_token)
dp = Dispatcher(bot)

x = 'html.parser'
BASE_URL = 'http://myzuka.club'
links = []
download_links = []

#--------------------------------------------------------------
'''
def connected(host = 'http://google.com'):
    try:
        urllib.request.urlopen(host)
        return True
    except:
        return False
'''
#--------------------------------------------------------------

def parse(html):
    soup = BeautifulSoup(html , x)
    all_ = soup.find('div', {'class':'all'})
    main = all_.find('div', {'class':'main'})
    content = main.find('div', {'class':'content'})
    inner = content.find('div', {'class':'inner'})
    top = inner.find_all('div', {'class':'top'})
    title = inner.find('h1')

    global links
    for top in inner.find_all('div', class_ = 'player-inline'):
        links.append(top.a['href'])

#--------------------------------------------------------------

def parse_2(html):
    soup = BeautifulSoup(html, x)
    all_ = soup.find('div', {'class':'all'})
    main = all_.find('div', {'class':'main'})
    content = main.find('div', {'class':'content'})
    inner = content.find('div', {'class':'inner'})
    options = inner.find('div', {'class':'options'})
    top = options.find('div', {'class':'top'})
    
    global download_links
    download_links.append(top.a['href'])
    
#--------------------------------------------------------------

def edited_links(nums, message):
    if nums != None :
        url = message[6:-(len(nums)+2)]
        check = nums
        if '-' in check and ',' not in check:
            nums = numbers(nums)
            edit_links = [i for i in range(int(nums[0]),int(nums[-1])+1)]
        elif ',' in check and '-' not in check :
            edit_links = numbers(nums)
        else:
            edit_links = nums.split(',')
            for i in edit_links:
                if len(i) >= 3 :
                    nums = i
                    break
            nums = numbers(nums)
            edit_links = [i for i in range(int(nums[0]),int(nums[-1])+1)] 
    else :
        url = message[6:]
        edit_links = None
        
    return edit_links, url

#--------------------------------------------------------------       

async def dloader(dlinks, chat_id):
    try:
       for i in dlinks:
           global download_links
           r = requests.get(BASE_URL + download_links[i-1], stream = True)
           if r.status_code == 200:
                 with open('song{}.mp3'.format(str(i)), 'wb') as f:
                     f.write(r.content)
                 renamer(i)
                 replacer()
                 await sender(chat_id)
                 remover()
           else :
                 pass
    except IndexError:
        pass

#--------------------------------------------------------------

async def dloader_2(chat_id):
    global download_links
    try:
       for i in range(len(download_links)):
            r = requests.get(BASE_URL + download_links[i], stream = True)
            if r.status_code == 200:
                with open('song{}.mp3'.format(str(i)), 'wb') as f:
                   f.write(r.content)
                renamer(i)
                replacer()
                await sender(chat_id)
                remover()
            else :
                pass
    except IndexError:
        pass
    
#--------------------------------------------------------------            

def renamer(i):
    try:
       mp3 = MP3File('song{}.mp3'.format(i))
       mp3.set_version(VERSION_1)
       song = mp3.get_tags()
       title = song['song']
       os.rename('song{}.mp3'.format(i), '{}. {}.mp3'.format(str(i), title))
    except OSError:
       pass
    
#--------------------------------------------------------------

def replacer():
    for files in os.listdir('./'):
        if files[-4:] == '.mp3':
            os.rename('./' + files, './music/' + files)

#--------------------------------------------------------------
    
async def sender(chat_id):
    for file in os.listdir('./music'):
       if file[-4:] == '.mp3':
          mp3 = MP3File('./music/' + file)
          mp3.set_version(VERSION_1)
          song = mp3.song
          artist = mp3.artist
          audio = open('./music/' + file, 'rb')
          await bot.send_audio(chat_id, audio, performer = artist, title = song)
          audio.close()
       else:
          pass

#--------------------------------------------------------------  

def remover():
    for files in os.listdir('./music'):
        if files[-4:] == '.mp3':
            os.remove('./music/' + files)

#--------------------------------------------------------------

def regexp(m):
    try:
        return m.split('(',1)[1].split(')')[0]
    except IndexError:
        return None
        pass

#--------------------------------------------------------------

def numbers(nums):
    l = len(nums)
    integ = []
    i = 0
    while i < l:
       num_int = ''
       a = nums[i]
       while '0' <= a <= '9':
          num_int += a
          i += 1
          if i < l:
             a = nums[i]
          else:
             break
       i += 1
       if num_int != '':
          integ.append(int(num_int))
 
    return sorted(integ)

#--------------------------------------------------------------
            
@dp.message_handler(commands = ['load'])
async def main(message: types.Message):
    chat_id = message.from_user.id
    msg_text = message.text
    nums = regexp(msg_text)
    edit_links = []

    edit_links, url = edited_links(nums, msg_text)
    try :
       response = requests.get(url, stream = True)
       parse(response.content) 
       
       global links, BASE_URL, download_links

       for i in range(len(links)):
          main_url = BASE_URL + str(links[i])
          r = requests.get(main_url, stream = True)
          parse_2(r.content)

       if edit_links == None:
           await dloader_2(chat_id)
       else:
           await dloader(edit_links, chat_id)
              
       links.clear()
       download_links.clear()

    except urllib.error.HTTPError:
       pass
    except AttributeError:
       pass
    except requests.exceptions.ConnectionError:
       pass
    except requests.exceptions.MissingSchema:
       pass
    except requests.exceptions.InvalidSchema:
       pass

#--------------------------------------------------------------

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates = True)
    
#--------------------------------------------------------------



