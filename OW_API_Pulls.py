import requests
import cv2
from PIL import Image, ImageFont, ImageDraw
import numpy as np
import urllib
import datetime
import os

#Possible that they blocked me due to to many request. userData was resulting in no actual data, this herolist resulted
#in a bunch of nothing.

def userData(userName="Asome#1762", region="us", platform="pc"):
    #Pulls all a available data on player. Serves as the main data set for other functions.
    userName = userName.replace("#", "-")
    url = "https://ow-api.com/v1/stats/"+platform+"/"+region+"/"+userName+"/complete"
    print url
    jsonFile = requests.get(url)
    data = jsonFile.json()
    return data

def heroPlayTime(data):
    #Extracts a list of heroes that have been played in competitive mode.
    heroes = []
    time = []
    heroList = data["competitiveStats"]["careerStats"].keys()
    heroList.remove("allHeroes")
    for hero in heroList:
        timePlayed = data["competitiveStats"]["careerStats"][hero]["game"]["timePlayed"]
        timeList = timePlayed.split(":")
        timeList = map(float, timeList)
        if len(timeList) == 3:
            minutes10Played = ((timeList[0] * 60) + timeList[1] + (timeList[2] / 60)) / 10
        elif len(timeList) == 2:
            minutes10Played = (timeList[0] + (timeList[1] / 60)) / 10
        else:
            minutes10Played = (timeList[0] / 60) / 10
        if minutes10Played >= 1.5:
            heroes.append(hero)
            time.append(minutes10Played)
    return heroes, time

def heroStatExtraction(data, hero, timePlayed):
    #Gets the final stats for each hero
    totalDamage = data["competitiveStats"]["careerStats"][hero]["combat"]["heroDamageDone"]
    totalEliminations = data["competitiveStats"]["careerStats"][hero]["combat"]["eliminations"]
    totalDeaths = data["competitiveStats"]["careerStats"][hero]["combat"]["deaths"]
    try:
        winPercentage = data["competitiveStats"]["careerStats"][hero]["game"]["winPercentage"]
    except:
        winPercentage = 0
    damagePer10 = totalDamage / timePlayed
    deathsPer10 = totalDeaths / timePlayed
    eliminationsPer10 = totalEliminations / timePlayed
    if hero=="ana" or hero=="brigitte" or hero=="lucio" or hero=="mercy" or hero=="moira" or hero=="zenyatta":
        healingPer10 = data["competitiveStats"]["careerStats"][hero]["assists"]["healingDone"] / timePlayed
        return winPercentage, timePlayed, damagePer10, deathsPer10, eliminationsPer10, int(healingPer10), "HEALING/10"
    elif hero=="reinhardt":
        accuracy = data["competitiveStats"]["careerStats"][hero]["heroSpecific"]["rocketHammerMeleeAccuracy"]
        return winPercentage, timePlayed, damagePer10, deathsPer10, eliminationsPer10, accuracy, "ACCURACY"
    else:
        try:
            accuracy = data["competitiveStats"]["careerStats"][hero]["combat"]["weaponAccuracy"]
        except:
            accuracy = "0%"
        return winPercentage, timePlayed, damagePer10, deathsPer10, eliminationsPer10, accuracy, "ACCURACY"

def heroListStats(data, heroList, timeList):
    winPercentageList = []
    damagePer10List = []
    deathsPer10List = []
    eliminationsPer10List = []
    miscStatList = []
    mistStatTitleList = []
    x = 0
    for hero in heroList:
        heroData = heroStatExtraction(data, hero, timeList[x])
        winPercentageList.append(heroData[0])
        damagePer10List.append(heroData[2])
        deathsPer10List.append(heroData[3])
        eliminationsPer10List.append(heroData[4])
        miscStatList.append(heroData[5])
        mistStatTitleList.append(heroData[6])
        x += 1
    x=0
    heroList1 = []
    timeList1 = []
    winPercentageList1 = []
    damagePer10List1 = []
    deathsPer10List1 = []
    eliminationsPer10List1 = []
    miscStatList1 = []
    mistStatTitleList1 = []
    while x < 10:
        maxIndex = timeList.index(max(timeList))
        if timeList[maxIndex] < 0:
            break
        heroList1.append(heroList[maxIndex])
        timeList1.append(timeList[maxIndex])
        winPercentageList1.append(winPercentageList[maxIndex])
        damagePer10List1.append(damagePer10List[maxIndex])
        deathsPer10List1.append(deathsPer10List[maxIndex])
        eliminationsPer10List1.append(eliminationsPer10List[maxIndex])
        miscStatList1.append(miscStatList[maxIndex])
        mistStatTitleList1.append(mistStatTitleList[maxIndex])
        timeList[maxIndex] = -1
        x += 1
    return heroList1, timeList1, winPercentageList1, damagePer10List1, deathsPer10List1, eliminationsPer10List1, \
           miscStatList1, mistStatTitleList1


def dataPull(userName="Asome#1762", region="us", platform="pc"):
    data = userData(userName, region, platform)
    timeList = heroPlayTime(data)
    stats = heroListStats(data, timeList[0], timeList[1])
    dataframe = {"Hero": stats[0], "TimePlayed": stats[1], "WinPercentage": stats[2], "Damage/10": stats[3],
                 "Deaths/10": stats[4], "Elims/10": stats[5], "MiscStatTitle": stats[7], "MiscStat": stats[6]}
    return dataframe

def userProfileInfo(userName="Asome#1762", region="us", platform="pc"):
    userName = userName.replace("#", "-")
    url = "https://ow-api.com/v1/stats/"+platform+"/"+region+"/"+userName+"/profile"
    jsonFile = requests.get(url)
    data = jsonFile.json()
    return data["icon"], data["rating"], data["competitiveStats"]["games"]["won"], data["competitiveStats"]["games"]["played"]

def createGraphic(userName="Asome#1762", region="us", platform="pc", fileLocation = "pp"):
    #Cut off list at top 10 characters
    dataframe = dataPull(userName, region, platform)
    cwd = os.getcwd()
    bg = cv2.imread(cwd + "\VisualAssets\Background.png")
    WPIcon = cv2.imread(cwd + "\VisualAssets\HeroIcons\WPIcon.png")
    accuracyTitle = cv2.imread(cwd + "\VisualAssets\HeroIcons\Accuracy.png")
    healingTitle = cv2.imread(cwd + "\VisualAssets\HeroIcons\Healing.png")
    heroNum = 1
    #Paste Hero Icon to the correct locations
    for hero in dataframe["Hero"]:
        icon = cv2.imread(cwd + "\VisualAssets\HeroIcons\Icon-"+hero+".png")
        if heroNum <= 5:
            x = 10
            y = (100*heroNum)+10
        else:
            x = 410
            y = 100*(heroNum-5)+10
        bg[y:(y+80), x:(x+80)] = icon
        y = y+100
        bg[y - 31:(y - 31 + 21), x + 21:(x + 21 + 40)] = WPIcon
        print heroNum
        y = y-100
        if hero=="ana" or hero=="brigitte" or hero=="lucio" or hero=="mercy" or hero=="moira" or hero=="zenyatta":
            bg[y-5:y-5+23, x+215:x+215+95] = healingTitle
        else:
            bg[y-5:y-5+23, x+215:x+215+95] = accuracyTitle
        heroNum += 1
    userInfo = userProfileInfo(userName, region, platform)
    req1 = urllib.urlopen(userInfo[0])
    arr1 = np.asarray(bytearray(req1.read()), dtype=np.uint8)
    userPlayerIcon = cv2.imdecode(arr1, -2)
    userPlayerIcon = cv2.resize(userPlayerIcon, (78, 78))
    bg[11:11+78, 11:11+78] = userPlayerIcon

    userRank = str(userInfo[1])
    userWon = float(userInfo[2])
    userPlayed = float(userInfo[3])
    userWinPercentage = str(round(userWon / userPlayed, 2))
    userWinPercentage = userWinPercentage[2:]
    if len(userWinPercentage) == 1:
        userWinPercentage = userWinPercentage + "0%"
    else:
        userWinPercentage = userWinPercentage + "%"
    cv2.imwrite(cwd+"\VisualAssets\TestImage.png", bg)
    img = Image.open(cwd+"\VisualAssets\TestImage.png")
    draw = ImageDraw.Draw(img)
    font1 = ImageFont.truetype("C:\Windows\Fonts\Big_noodle_titling.ttf", 22)
    draw.text((555, 24), userWinPercentage, (255, 255, 255), font=font1)
    draw.text((555, 64), str(int(userPlayed)), (255, 255, 255), font=font1)
    heroNum = 1
    for hero in dataframe["Hero"]:
        damagePer10 = str(int(dataframe["Damage/10"][heroNum-1]))
        deathsPer10 = str(round(dataframe["Deaths/10"][heroNum-1],2))
        time = str(round(dataframe["TimePlayed"][heroNum-1]/6, 2))
        otherStat = str(dataframe["MiscStat"][heroNum-1])
        winRate = str(dataframe["WinPercentage"][heroNum-1])
        if heroNum <= 5:
            x = 180
            y = heroNum * 100 + 27
        else:
            x = 580
            y = (heroNum-5) * 100 + 27
        draw.text((x, y), damagePer10, (255, 255, 255), font=font1)
        draw.text((x, y+40), time, (255,255,255), font=font1)
        draw.text((x+150, y+40), deathsPer10, (255,255,255), font=font1)
        draw.text((x+150, y), otherStat, (255, 255, 255), font=font1)
        draw.text((x-142, y+50), winRate, (255, 255,255), font=font1)
        heroNum += 1
    font = ImageFont.truetype(cwd+"\VisualAssets\Fonts\Big_noodle_titling.ttf", 75)
    userName = userName.split("#")[0]
    draw.text((100, 5), userName, (255, 255, 255), font=font)
    font2 = ImageFont.truetype(cwd+"\VisualAssets\Fonts\Big_noodle_titling.ttf", 55)
    draw.text((650, 28), userRank, (255,255,255), font=font2)
    now = datetime.datetime.now()
    img.save(fileLocation + "/" + str(now.year) + "_" + str(now.month) + "_" + str(now.day) + "_" + userName + ".png")
    return

cwd = os.getcwd()
print cwd