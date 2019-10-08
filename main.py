from telebot import TeleBot
from bs4 import BeautifulSoup
from mp3_tagger import MP3File, VERSION_1, VERSION_2, VERSION_BOTH
import requests, urllib, os, time

#--------------------------------------------------------------

#token = os.environ.get('BOT_TOKEN_2')

TOKEN = '908066763:AAFvrd1m3cmmCvnPni5xrl1h_L3EJmWs99Q'
bot = TeleBot(TOKEN)
x = 'html.parser'
BASE_URL = 'http://myzuka.club'
links = []
download_links = []

#--------------------------------------------------------------

def connected(host='http://google.com'):
    try:
        urllib.request.urlopen(host)
        return True
    except:
        return False

#--------------------------------------------------------------

def parse(html):
    soup = BeautifulSoup(html , x)
    all_ = soup.find('div' , {'class':'all'})
    main = all_.find('div' , {'class':'main'})
    content = main.find('div' , {'class':'content'})
    inner = content.find('div' , {'class':'inner'})
    top = inner.find_all('div' , {'class':'top'})
    title = inner.find('h1')

    global links
    for top in inner.find_all('div' , class_ = 'player-inline'):
        links.append(top.a['href'])

#--------------------------------------------------------------

def parse_2(html):
    soup = BeautifulSoup(html , x)
    all_ = soup.find('div' , {'class':'all'})
    main = all_.find('div' , {'class':'main'})
    content = main.find('div' , {'class':'content'})
    inner = content.find('div' , {'class':'inner'})
    options = inner.find('div' , {'class':'options'})
    top = options.find('div' , {'class':'top'})
    
    global download_links
    download_links.append(top.a['href'])
    
#--------------------------------------------------------------

def renamer(i):
    try:
       mp3 = MP3File('song{}.mp3'.format(i+1))
       mp3.set_version(VERSION_1)
       song = mp3.get_tags()
       title = song['song']
       os.rename('song{}.mp3'.format(i+1) , '{}. {}.mp3'.format(str(i+1),title))
    except OSError:
       pass
    
#--------------------------------------------------------------

def replacer():
    for files in os.listdir('./'):
        if files[-4:] == '.mp3':
            os.rename('./'+files, './music/'+files)

#--------------------------------------------------------------
    
def sender(chat_id):
    for file in os.listdir('./music'):
       mp3 = MP3File('./music/'+file)
       mp3.set_version(VERSION_1)
       song = mp3.song
       artist = mp3.artist
       audio=open('./music/'+ file, 'rb')
       bot.send_audio(chat_id , audio , performer=artist , title = song , timeout = 1)
       audio.close()

#--------------------------------------------------------------  

def remover():
    for files in os.listdir('./music'):
        if files[-4:] == '.mp3':
            os.remove('./music/'+files)

#--------------------------------------------------------------
            
@bot.message_handler(commands=['load'])
def main(message):
    start = time.time()
    url = message.text[6:]
    try :
       response = requests.get(url , stream=True)
       parse(response.content)
       
       global links , BASE_URL , download_links

       for i in range(len(links)):
          main_url = BASE_URL + links[i]
          r = requests.get(main_url , stream=True)
          parse_2(r.content)

       for i in range(len(download_links)):
          r = requests.get(BASE_URL + download_links[i],stream=True)
          if r.status_code == 200:
              with open('song{}.mp3'.format(str(i+1)) , 'wb') as f:
                  print('downloading started...')
                  f.write(r.content)
                  print('downloading ended...')
              renamer(i)
              replacer()
              sender(message.chat.id)
              remover()
    
          else :
              print('error')
              pass
              
       links.clear()
       download_links.clear()
       
    except TypeError:
       print('error')
       pass
    except urllib.error.HTTPError:
       print('error')
       pass
    except AttributeError:
       print('error')
       pass
    except requests.exceptions.ConnectionError:
       print('error')
       pass
    except requests.exceptions.MissingSchema:
       print('error')
       pass
    except requests.exceptions.InvalidSchema:
       print('error')
       pass
    
    end = time.time()

    runtime = print(end-start)

#--------------------------------------------------------------

print( 'connected' if connected() else 'no internet!' )
if connected():
    bot.polling()

#--------------------------------------------------------------




