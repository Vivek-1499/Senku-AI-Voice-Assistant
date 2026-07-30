from shlex import quote
import struct
import subprocess
import time

from playsound import playsound
import pyaudio
import pyautogui
from engine.config import ASSISTANT_NAME
import eel
from engine.command import speak
import os
import pywhatkit as kit
import re
import sqlite3
import webbrowser
import pvporcupine

from engine.helper import extract_yt_term, remove_words
# Playing Assistant sound

conn = sqlite3.connect("senku.db")
cursor = conn.cursor()
@eel.expose
def playAssistantSound():
  music_dir = "www\\assets\\audio\\start_sound.mp3"
  playsound(music_dir)
  
def openCommand(query):
  query = query.replace(ASSISTANT_NAME, "")
  query = query.replace("open", "")
  query.lower()
  
  app_name = query.strip()
  
  if app_name != "":
    try:
      cursor.execute('SELECT path FROM sys_command WHERE LOWER(name) IN (?)', (app_name,))
      results = cursor.fetchall()
      print("Results:", results)
      
      if len(results) != 0:
        speak("Opening "+ query)
        os.startfile(results[0][0])
      elif len(results) == 0:
        cursor.execute('SELECT url FROM web_command WHERE LOWER(name) IN (?)', (app_name,))
        results = cursor.fetchall()
        print("Results:", results)
        
        if len(results) != 0:
          speak("Opening "+ query)
          webbrowser.open(results[0][0])
          
        else:
          speak("Opening "+ query)
          try:
            os.system('start '+ query)
          except:
            speak('Not Found')
    except:
      speak("some thing went wrong")
    
def playYoutube(query):
  search_term = extract_yt_term(query)
  speak("Playing " + search_term+ " on YouTube")
  kit.playonyt(search_term)
  
def hotword():
    porcupine=None
    paud=None
    audio_stream=None
    try:
       
        # pre trained keywords    
        porcupine=pvporcupine.create(keywords=["jarvis","alexa"]) 
        paud=pyaudio.PyAudio()
        audio_stream=paud.open(rate=porcupine.sample_rate,channels=1,format=pyaudio.paInt16,input=True,frames_per_buffer=porcupine.frame_length)
        
        # loop for streaming
        while True:
            keyword=audio_stream.read(porcupine.frame_length)
            keyword=struct.unpack_from("h"*porcupine.frame_length,keyword)

            # processing keyword comes from mic 
            keyword_index=porcupine.process(keyword)

            # checking first keyword detetcted for not
            if keyword_index>=0:
                print("hotword detected")

                # pressing shorcut key win+j
                import pyautogui as autogui
                autogui.keyDown("win")
                autogui.press("j")
                time.sleep(2)
                autogui.keyUp("win")
                
    except:
        if porcupine is not None:
            porcupine.delete()
        if audio_stream is not None:
            audio_stream.close()
        if paud is not None:
            paud.terminate()
            
# Whatsapp Message Sending
def findContact(query):
    words_to_remove = [ASSISTANT_NAME, 'make', 'a', 'to', 'phone', 'call', 'send', 'message', 'whatsapp', 'video']
    query = remove_words(query, words_to_remove)

    try:
        query = query.strip().lower()
        cursor.execute("SELECT mobile_no FROM contacts WHERE LOWER(name) LIKE ? OR LOWER(name) LIKE ?", ('%' + query + '%', query + '%'))
        results = cursor.fetchall()
        print(results[0][0])
        mobile_number_str = str(results[0][0])
        if not mobile_number_str.startswith('+91'):
            mobile_number_str = '+91' + mobile_number_str

        return mobile_number_str, query
    except:
        speak('not exist in contacts')
        return 0, 0
      
def whatsApp(mobile_no, flag, message, name):

    if flag == 'message':
        target_tab = 16
        jarvis_message = "message send successfully to " + name

    elif flag == 'call':
        target_tab = 10
        message = ''
        jarvis_message = "calling to " + name

    else:
        target_tab = 10
        message = ''
        jarvis_message = "starting video call with " + name

    # clean message
    message = message.replace("'", "").replace('"', "")
    message = message.strip()

    # encode message
    encoded_message = quote(message)

    # direct WhatsApp URL
    whatsapp_url = f"whatsapp://send?phone={mobile_no}&text={encoded_message}"

    # open WhatsApp chat directly
    subprocess.run(f'start "" "{whatsapp_url}"', shell=True)

    # wait for WhatsApp
    time.sleep(10)

    # MESSAGE
    if flag == 'message':

        # move focus to send button/message box
        for i in range(target_tab):
            pyautogui.press('tab')

        time.sleep(1)

        pyautogui.press('enter')

    # VOICE CALL
    elif flag == 'call':

        for i in range(target_tab):
            pyautogui.press('tab')

        pyautogui.press('enter')

        time.sleep(1)

        pyautogui.press('down')

        pyautogui.press('enter')

    # VIDEO CALL
    else:

        for i in range(target_tab):
            pyautogui.press('tab')

        pyautogui.press('enter')

        time.sleep(1)

        pyautogui.press('down')
        pyautogui.press('down')

        pyautogui.press('enter')

    speak(jarvis_message)