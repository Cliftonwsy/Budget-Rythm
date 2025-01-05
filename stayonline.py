from flask import Flask
from threading import Thread

#connect bot to uptimerobot to stay online 24/7 hosted by a cloud and not by me so it doesnt go offline when my computer is off

app = Flask('')

@app.route('/')
def home():
  return "Online"

def run():
  app.run(host='0.0.0.0',port=8080)

def stayonline():
  t = Thread(target=run)
  t.start()