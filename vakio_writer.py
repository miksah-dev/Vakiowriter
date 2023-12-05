#%%
from email import header
from operator import index
from urllib import request
import pandas as pd
import requests
import csv
import json
from datetime import date



# Vaaditut otsikkotietueet
headers = {
	'Content-type':'application/json',
	'Accept':'application/json',
	'X-ESA-API-Key':'ROBOT'
}

# Sisäänkirjautuminen Veikkauksen tilille palauttaa sessio-objektin
def login (username, password):
	s = requests.Session()
	login_req = {"type":"STANDARD_LOGIN","login":username,"password":password}
	r = s.post("https://www.veikkaus.fi/api/bff/v1/sessions", data=json.dumps(login_req), headers=headers)
	if r.status_code == 200:
		return s
	else:
		raise Exception("Authentication failed", r.status_code)

# Main-funktio.
# 1. Kirjautuu sisään
# 2. Hakee Vakion tulevat kohteet 
# 3. Hakee Vakio peliprosentit ensimmäiseltä riviltä (Lauantaivakio, paitsi sunnuntaina)
def main():
    # s = login('esimerkki','salasana')
    vakio = requests.get('https://www.veikkaus.fi/api/sport-open-games/v1/games/SPORT/draws', headers=headers)
    jsonResponse = vakio.json()
    kaikkirivit = len(jsonResponse)
    lauantaivakio = []
    sunnuntaivakio = []

    # check current date
    today = date.today()
    todayfileLauantai = today.strftime("%b-%d-%Y") + "Lauantai" + ".CSV"
    todayfileSunnuntai = today.strftime("%b-%d-%Y") + "Sunnuntai" + ".CSV"

    headerit = ["home", "away", "OLBG", "FST", "Veikka", "Rivi", "prosentit 1", "prosentit x", "prosentit 2", '', "Kertoimet 1", "Kertoimet x", "Kertoimet 2" ]

    for i in range(kaikkirivit):
        if jsonResponse[i]["name"] == "Lauantaivakio":
            lauantaivakio = jsonResponse[i]
            Lauantaiid = lauantaivakio["id"]
            peliosoite = "https://www.veikkaus.fi/api/sport-popularity/v1/games/SPORT/draws/" + str(Lauantaiid) + "/popularity"
            prossatLau = requests.get(peliosoite, headers=headers)
            prossatresponseLau = prossatLau.json()
            exportFile(todayfileLauantai, headerit, lauantaivakio, prossatresponseLau)
            
        if jsonResponse[i]["name"] == "Sunnuntaivakio":
            sunnuntaivakio = jsonResponse[i]
            Sunnuntaiid = sunnuntaivakio["id"]
            peliosoite = "https://www.veikkaus.fi/api/sport-popularity/v1/games/SPORT/draws/" + str(Sunnuntaiid) + "/popularity"
            prossatSun = requests.get(peliosoite, headers=headers)
            prossatresponseSun = prossatSun.json()
            exportFile(todayfileSunnuntai, headerit, sunnuntaivakio, prossatresponseSun)

    
def exportFile(filename, header, gameslist, prosentit):

    with open(filename, 'w', newline='') as f:
        # create the csv writer
        writer = csv.writer(f, delimiter=';')
        prossaindex = 0   
      
        writer.writerow(header)  
        # write a row to the csv file

        for rivit in gameslist["rows"]:
            koti = rivit ["outcome"]["home"]["name"]
            vieras = rivit ["outcome"]["away"]["name"]
            homewin = (prosentit["resultPopularities"][prossaindex]["percentage"]/100)
            homewinodds = str(1/(homewin/100))
            
            prossaindex = prossaindex + 1
            draw = (prosentit["resultPopularities"][prossaindex]["percentage"]/100)
            drawodds = str(1/(draw/100))

            prossaindex = prossaindex + 1
            awaywin = (prosentit["resultPopularities"][prossaindex]["percentage"]/100)
            awaywinodds = str(1/(awaywin/100))

            prossaindex = prossaindex + 1

            peli = [koti,vieras, '', '', '', '', str(homewin),str(draw),str(awaywin)]
            peli2 = ['', '','','','', '', homewinodds, drawodds , awaywinodds]
            writer.writerow(peli)  
            writer.writerow(peli2)      


main()
# %%
