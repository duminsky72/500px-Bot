#!/usr/bin/env python

import requests, time, json, os
from bs4 import BeautifulSoup
from random import randint

scriptDirectory = os.path.abspath(os.path.dirname(__file__))
logDate = time.strftime('%Y-%m-%d')

userSession = requests.Session()
userSession.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36'
})

pendingFileName = 'pendingUsers.txt'
acceptedFileName = 'acceptedUsers.txt'
ignoredFileName = 'ignoredUsers.txt'

pendingFilePath = scriptDirectory + '/' + pendingFileName
acceptedFilePath = scriptDirectory + '/' + acceptedFileName
ignoredFilePath = scriptDirectory + '/' + ignoredFileName

logFileName = logDate + '_log.txt'
logFilePath = scriptDirectory + '/logs/'

loginParams = {
    'authenticity_token': '',
    'session[email]': '',
    'session[password]': ''
}

csrfHeaders = {
    'X-CSRF-Token': '',
    'X-Requested-With': 'XMLHttpRequest'
}

pendingFollowList = []
acceptedFollowList = []
ignoredFollowList = []

def printToLog(string):
    global logFilePath, logFileName
    logTime = time.strftime('%H:%M')
    if not os.path.exists(logFilePath):
        os.makedirs(logFilePath)
    with open(logFilePath + logFileName, 'a+') as f:
        f.write(logTime + ' - ' + string + '\n')
    print(logTime + ' - ' + string)

def retrieveLists():
    global pendingFilePath, acceptedFilePath, ignoredFilePath
    global pendingFollowList, acceptedFollowList, ignoredFollowList
    if os.path.exists(pendingFilePath):
        with open(pendingFilePath, 'r') as f:
            pendingFollowList = json.loads(f.read())
    if os.path.exists(acceptedFilePath):
        with open(acceptedFilePath, 'r') as f:
            acceptedFollowList = json.loads(f.read())
    if os.path.exists(ignoredFilePath):
        with open(ignoredFilePath, 'r') as f:
            ignoredFollowList = json.loads(f.read())

def isUserPending(targetUserName):
    global pendingFollowList
    userPending = False
    for i, v in enumerate(pendingFollowList):
        if v['name'] == targetUserName:
            userPending = True
            break
    return userPending

def isUserAccepted(targetUserName):
    global acceptedFollowList
    userAccepted = False
    for i, v in enumerate(acceptedFollowList):
        if v['name'] == targetUserName:
            userAccepted = True
            break
    return userAccepted

def isUserIgnored(targetUserName):
    global ignoredFollowList
    userIgnored = False
    for i, v in enumerate(ignoredFollowList):
        if v['name'] == targetUserName:
            userIgnored = True
            break
    return userIgnored

def followUser(targetUserName):
    global userSession, numFollowsDone
    continueLoop = True
    while continueLoop:
        try:
            followResp = userSession.post('https://500px.com/' + targetUserName + '/follow', timeout = 5, headers = csrfHeaders)
            if followResp.status_code == 200:
                printToLog('Followed ' + targetUserName + '.')
                numFollowsDone += 1
                addUserToPendingList(targetUserName)
                continueLoop = False
            elif followResp.status_code == 404:
                printToLog('User ' + targetUserName + ' no longer exists. Skipped follow.')
                continueLoop = False
            elif followResp.status_code == 403:
                printToLog('Already followed ' + targetUserName + '.')
                continueLoop = False
            else:
                printToLog('A server error (' + str(followResp.status_code) + ') occured. Retrying...')
                printToLog('Error page: ' + followResp.url)
                time.sleep(5)
        except requests.exceptions.RequestException:
            printToLog('Web page timed out. Retrying...')
            time.sleep(5)
    time.sleep(20)

def addUserToPendingList(targetUserName):
    global pendingFollowList, pendingFilePath
    pendingFollowList.append({'name': targetUserName, 'time_followed': time.time()})
    with open(pendingFilePath, 'w') as f:
        f.write(json.dumps(pendingFollowList))

def addUserToAcceptedList(targetUserName):
    global acceptedFollowList, acceptedFilePath
    acceptedFollowList.append({'name': targetUserName, 'time_followed': time.time()})
    with open(acceptedFilePath, 'w') as f:
        f.write(json.dumps(acceptedFollowList))

def addUserToIgnoredList(targetUserName):
    global ignoredFollowList, ignoredFilePath
    ignoredFollowList.append({'name': targetUserName, 'time_followed': time.time()})
    with open(ignoredFilePath, 'w') as f:
        f.write(json.dumps(ignoredFollowList))

'''
def userExists(targetUserName):
    global userSession
    continueLoop = True
    while continueLoop:
        try:
            userResp = userSession.get('https://500px.com/' + targetUserName, timeout = 5)
            if userResp.status_code == 200:
                return True
            elif userResp.status_code == 404:
                return False
            else:
                printToLog('A server error (' + str(userResp.status_code) + ') occured. Retrying...')
                printToLog('Error page: ' + userResp.url)
                time.sleep(5)
        except requests.exceptions.RequestException:
            printToLog('Web page timed out. Retrying...')
            time.sleep(5)
    time.sleep(20)
'''

def unfollowUser(targetUserName):
    global userSession
    continueLoop = True
    while continueLoop:
        try:
            unfollowResp = userSession.post('https://500px.com/' + targetUserName + '/unfollow', timeout = 5, headers = csrfHeaders)
            if unfollowResp.status_code == 200:
                printToLog('Unfollowed ' + targetUserName + '.')
                continueLoop = False
            elif unfollowResp.status_code == 404:
                printToLog('User ' + targetUserName + ' no longer exists. Skipped unfollow.')
                continueLoop = False
            else:
                printToLog('A server error (' + str(unfollowResp.status_code) + ') occured. Retrying...')
                printToLog('Error page: ' + unfollowResp.url)
                time.sleep(5)
        except requests.exceptions.RequestException:
            printToLog('Web page timed out. Retrying...')
            time.sleep(5)
    time.sleep(20)

def removeUserFromPendingList(targetUserName):
    global pendingFollowList, pendingFilePath
    for i, v in enumerate(list(pendingFollowList)):
        if v['name'] == targetUserName:
            pendingFollowList.remove(v)
            break
    with open(pendingFilePath, 'w') as f:
        f.write(json.dumps(pendingFollowList))

def removeUserFromAcceptedList(targetUserName):
    global acceptedFollowList, acceptedFilePath
    for i, v in enumerate(list(acceptedFollowList)):
        if v['name'] == targetUserName:
            acceptedFollowList.remove(v)
            break
    with open(acceptedFilePath, 'w') as f:
        f.write(json.dumps(acceptedFollowList))

def removeUserFromIgnoredList(targetUserName):
    global ignoredFollowList, ignoredFilePath
    for i, v in enumerate(list(ignoredFollowList)):
        if v['name'] == targetUserName:
            ignoredFollowList.remove(v)
            break
    with open(ignoredFilePath, 'w') as f:
        f.write(json.dumps(ignoredFollowList))

# Retrieving the list of currently pending followed users by the bot.

retrieveLists()

# Time to remove anyone in any list for more than a week.

currentTime = time.time()
for i, v in enumerate(list(acceptedFollowList)):
    if currentTime - v['time_followed'] > 604800:
        acceptedFollowList.remove(v)
        with open(acceptedFilePath, 'w') as f:
            f.write(json.dumps(acceptedFollowList))

for i, v in enumerate(list(ignoredFollowList)):
    if currentTime - v['time_followed'] > 604800:
        ignoredFollowList.remove(v)
        with open(ignoredFilePath, 'w') as f:
            f.write(json.dumps(ignoredFollowList))

# This is used in order to obtain the authenticity token required for logging in.

continueLoop = True
while continueLoop:
    try:
        loginPage = userSession.get('https://500px.com/login', timeout = 5)
        if loginPage.status_code == 200:
            printToLog('Retrieved login page.')
            continueLoop = False
        else:
            printToLog('A server error (' + str(loginPage.status_code) + ') occured. Retrying...')
            printToLog('Error page: ' + loginPage.url)
            time.sleep(5)
    except requests.exceptions.RequestException:
        printToLog('Web page timed out. Retrying...')
        time.sleep(5)
time.sleep(20)

loginPage_soup = BeautifulSoup(loginPage.text, 'html.parser')
loginParams['authenticity_token'] = loginPage_soup.find('meta', {'name': 'csrf-token'}).get('content')
csrfHeaders['X-CSRF-Token'] = loginParams['authenticity_token']

# This is the actual login request.

continueLoop = True
while continueLoop:
    try:
        userLogin = userSession.post('https://api.500px.com/v1/session', data = loginParams, timeout = 5)
        if userLogin.status_code == 200:
            printToLog('Logged in successfully.')
            continueLoop = False
        else:
            printToLog('A server error (' + str(userLogin.status_code) + ') occured. Retrying...')
            printToLog('Error page: ' + userLogin.url)
            time.sleep(5)
    except requests.exceptions.RequestException:
        printToLog('Web page timed out. Retrying...')
        time.sleep(5)
time.sleep(20)

# Getting my user info from login response.

myUserInfo = json.loads(userLogin.text)['user']

# Time to see who has actually bothered following us.

pageNum = 1 # Do not change
pendingUserNames = [pendingFollowUser['name'] for pendingFollowUser in pendingFollowList]
myFollowers_json = []

while True:
    try:
        myFollowers = userSession.get('https://api.500px.com/v1/users/' + str(myUserInfo['id']) + '/followers?fullformat=0&page=' + str(pageNum) + '&rpp=50', timeout = 5)
        if myFollowers.status_code != 200:
            printToLog('A server error (' + str(myFollowers.status_code) + ') occured. Retrying...')
            printToLog('Error page: ' + myFollowers.url)
            time.sleep(5)
            continue
    except requests.exceptions.RequestException:
            printToLog('Web page timed out. Retrying...')
            time.sleep(5)
            continue
    tmpFollowers_json = json.loads(myFollowers.text)
    myFollowers_json += tmpFollowers_json['followers']
    if pageNum == tmpFollowers_json['followers_pages']:
        break
    pageNum += 1
    time.sleep(20)

for follower in list(myFollowers_json):
    currentTime = time.time()
    if not follower['username'] in pendingUserNames:
        myFollowers_json.remove(follower)
        continue
    removeUserFromPendingList(follower['username'])
    addUserToAcceptedList(follower['username'])
    printToLog(follower['username'] + ' followed you. Accepted.')
    pendingUserNames.remove(follower['username'])
    myFollowers_json.remove(follower)

for follower in list(pendingFollowList):
    currentTime = time.time()
    if currentTime - follower['time_followed'] <= 172800:
        continue
    removeUserFromPendingList(follower['name'])
    #if userExists(follower['name']): # Commented this out, so should save some time when unfollowing.
    unfollowUser(follower['name'])
    addUserToIgnoredList(follower['name'])
    pendingUserNames.remove(follower['name'])
    printToLog(follower['name'] + ' didn\'t follow you. Ignored and unfollowed.')
printToLog('Review of followed users finished.')

# Time to view the up-and-coming and follow more people :)

pageNum = 1 # Do not change.
numFollowsWanted = 101 # If I recall, 101 is the daily limit, and any more than this fails.
numFollowsDone = 0 # Do not change.

while numFollowsDone < numFollowsWanted:
    try:
        upcomingPage = userSession.get('https://api.500px.com/v1/photos?feature=upcoming&include_states=false&page=' + str(pageNum) + '&rpp=50', timeout = 5, headers = csrfHeaders)
        if upcomingPage.status_code != 200:
            printToLog('A server error (' + str(upcomingPage.status_code) + ') occured. Retrying...')
            printToLog('Error page: ' + upcomingPage.url)
            time.sleep(5)
            continue
    except requests.exceptions.RequestException:
            printToLog('Web page timed out. Retrying...')
            time.sleep(5)
            continue
    upcomingPage_json = json.loads(upcomingPage.text)
    for upcomingPhoto in upcomingPage_json['photos']:
        if not isUserPending(myUserInfo['username']) and not isUserAccepted(myUserInfo['username']) and not isUserIgnored(myUserInfo['username']) and numFollowsDone < numFollowsWanted:
            followUser(upcomingPhoto['user']['username'])
        elif numFollowsDone >= numFollowsWanted:
            break
    pageNum += 1
    time.sleep(20)
printToLog('Finished. No more users left to follow.')
