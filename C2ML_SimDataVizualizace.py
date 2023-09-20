from ctypes import resize
from pickle import FALSE, TRUE
from SimpleGraphics import *
import configparser
import pandas as pd
import numpy as np
import os
import glob



# vygenerujeme prazdne 2D pole o rozmerech 100 x 100
g_Situace = [[0 for row in range(100)]for col in range(100)]

def ClearSituace():
    for y in range(100):
        for x in range(100):
            g_Situace[x][y] = 0


def VygenerujSituaci(data,cas,predcas,):
    if predcas<0: predcas = 0
    situace = data[((data['SimTime']<cas) & (data['SimTime']>predcas))]

#projdeme vsechny radky = vsechny jednotky a zobrazime je
    situace = situace.reset_index()
    ClearSituace()

    for index,row in situace.iterrows():
        unitx = row['UTM-Easting']
        unity = row['UTM-Northing']

        x = (unitx - left) / 200
        y = (unity - bottom) / 200

        if (row['Side'] == "friend"):
           g_Situace[int(x)][int(y)] = 1
        else: g_Situace[int(x)][int(y)] = 2

    return int(situace.size)


def VygenerujSituaciNP(data,cas,predcas):
    if predcas<0: predcas = 0
    situace = data[((data['SimTime']<cas) & (data['SimTime']>predcas))]

#projdeme vsechny radky = vsechny jednotky a zobrazime je
    situace = situace.reset_index()
    frame = np.zeros([100,100])

    for index,row in situace.iterrows():
        unitx = row['UTM-Easting']
        unity = row['UTM-Northing']

        x = (unitx - left) / 200
        y = (unity - bottom) / 200

        if (row['Side'] == "friend"):
           frame[int(x)][int(y)] = 1
        else: frame[int(x)][int(y)] = 2

    return int(situace.size),frame



def ZobrazSituaci():        
    
    for y in range(100):
        for x in range(100):
            if (g_Situace[x][y]==1):
                setFill("blue")
                rect(x*10,y*10,10,10)
            if (g_Situace[x][y]==2):
                setFill("red")
                rect(x*10,y*10,10,10)


def ZobrazGrid():
    for i in range(0,100):
        line(0,i*10,1000,i*10)
        line(i*10,0,i*10,1000)


def FindTimeStep(data):
    predchozicas = 0
    for index,row in data.iterrows():
        if (row['SimTime']-predchozicas) > 10:
            return int(row['SimTime']-predchozicas)



def PripravSekvenci(data,minimumframes):
    timestep = FindTimeStep(data)

    pole = np.zeros([0,100,100])

    frames = 0
    cas = 10
    
    pocet,frame = VygenerujSituaciNP(data,cas,cas - timestep)
    while (pocet>0):       
        cas+=timestep
        frames+=1
        if (frames>minimumframes): break
        image = np.expand_dims(frame,axis=0)
        pole = np.append(pole,image,axis=0)
        pocet,frame = VygenerujSituaciNP(data,cas,cas - timestep)

    return int(frames),pole


def ZjistiFramesVSekvenci(data):
    timestep = FindTimeStep(data)

    frames = 0
    cas = 10
    
    pocet,frame = VygenerujSituaciNP(data,cas,cas - timestep)
    while (pocet>0):       
        cas+=timestep
        frames+=1
        pocet,frame = VygenerujSituaciNP(data,cas,cas - timestep)


    return int(frames)


def listFiles(path, mask):

    """vraci slovnik kde klicem je adresar a hodnotami seznam souboru v nem

    vse v relativnich cestach """

    directory = {}

    for root, dirs, files in os.walk(path):

        files = glob.glob(os.path.join(root,mask))

        if (files!=[]) :

            directory[root]=glob.glob(root+os.path.sep+mask)

    return directory


def PripravSekvence(minimumframes):

    zacatek_addr = input("Zadej pocatecni adresar: ")
    soubory = listFiles(os.path.expanduser(zacatek_addr),"*.csv")

    learndata = np.zeros([0,minimumframes,100,100])

    for k,v in list(soubory.items()):
        for csvfile in v:
            #for mp3 in jmena:
            data = pd.read_csv(csvfile, delimiter=';')
            frames,pole = PripravSekvenci(data,minimumframes)
            print("Soubor: ",csvfile," Pocet sekvenci: ",frames)
            pole = np.expand_dims(pole,axis=0)
            learndata = np.append(learndata,pole,axis=0)
     
    print("final shape: ",learndata.shape)
    jmenosouboru = input("Zadej jmeno souboru dat pro ulozeni: ")
    np.save(jmenosouboru,learndata)
    print("ulozeno")



def ZjistiPocetFramesVSekvence():

    zacatek_addr = input("Zadej pocatecni adresar: ")
    soubory = listFiles(os.path.expanduser(zacatek_addr),"*.csv")


    minimum = 999

    for k,v in list(soubory.items()):
        for csvfile in v:
            #for mp3 in jmena:
            data = pd.read_csv(csvfile, delimiter=';')
            frames = ZjistiFramesVSekvenci(data)
            print("Soubor: ",csvfile," Pocet sekvenci: ",frames)
            if (frames<minimum): minimum = frames
     
    return minimum


# nacteni konfigurace - velikost a pozice oblasti dat v UTM
config = configparser.ConfigParser()
config.read("nastaveni.cfg")
left = int(config['area']['left'])
top = int(config['area']['top'])
right = int(config['area']['right'])
bottom = int(config['area']['bottom'])

resize(1024,1024)

minimumframes = ZjistiPocetFramesVSekvence()
print("Minimum frames je : ",minimumframes)

PripravSekvence(minimumframes)

data = pd.read_csv("logs\\sim6_stats2.csv", delimiter=';')


PripravSekvenci(data)

timestep = FindTimeStep(data)

# vyber dle indexu radku
#radek = data.iloc[1]
#unitid = radek['ID']

# vyber vsech radku dle podminky - u nas casu, vsechny jednotky, ktere se ulozili v nejaky cas
print("Ovladani:")
print("Dalsi snimek> +")
print("Zobraz grid> g")
print("Zmena casoveho kroku> t")
print("Konec> q")

cas = 10
zobrazgrid=False

while(True):
    clear();
    pocet = VygenerujSituaci(data,cas,cas - timestep)
    print("Pocet dat: ",end="")
    print(pocet)
   

    ZobrazSituaci()
    if (zobrazgrid): ZobrazGrid()
    text(5,5,"Cas: {} s".format(cas),align="nw")
    print("Prikaz> ",end='')
    prikaz = input();
    if (prikaz=="g"): 
       if zobrazgrid:
        zobrazgrid = False
       else: zobrazgrid = True
    if (prikaz=="t"):
        print("Zadej casovy krok v sekundach: ",end="")
        timestep = int(input())
    if (prikaz=="-"): cas-=timestep
    if (prikaz=="+"): cas+=timestep
    if (prikaz=="q"):
        break




