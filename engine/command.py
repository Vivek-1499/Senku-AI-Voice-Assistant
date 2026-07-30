import pyttsx3
import speech_recognition as sr
import eel
import time
def speak(text):
  engine =pyttsx3.init('sapi5')
  voices = engine.getProperty('voices')
  engine.setProperty('voice', voices[0].id)
  engine.setProperty('rate', 174)
  eel.DisplayMessage(text)
  engine.say(text)
  engine.runAndWait()
  
def takeCommand():
  r = sr.Recognizer()
  with sr.Microphone() as source:
    print('listening...')
    eel.DisplayMessage('listening...')
    r.pause_threshold =1
    r.adjust_for_ambient_noise(source)
    audio = r.listen(source, 10, 6)
    
  try:
    print('recognizing')
    eel.DisplayMessage('Recognizing...')
    query = r.recognize_google(audio, language='en-in')
    print(f"user said: {query}")
    eel.DisplayMessage(query)
    time.sleep(2)
  except Exception as e:
    return ""
  
  return query.lower()

@eel.expose
def allCommands():
  try:
    query = takeCommand()
    print(query)
    
    if "open" in query:
      from engine.features import openCommand
      openCommand(query)
    elif "on youtube" in query:
      from engine.features import playYoutube
      playYoutube(query)
    elif "message" in query or "send message" in query or "phone call" in query or "video call" in query or "call" in query:
      from engine.features import findContact, whatsApp
      message = ""
      contact_no, name = findContact(query)
      if(contact_no != 0):
        if "send message" in query or "message" in query:
          message = 'message'
          speak("what message to send")
          query = takeCommand()  
        elif "video call" in query:
          message = 'video call'     
        elif "call" in query or "phone call" in query:
          message = 'call'
        whatsApp(contact_no, message, query, name)
    else:
      print("not run")
  except:
    print("error")
    
  eel.ShowHood()