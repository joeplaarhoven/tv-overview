from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.shortcuts import render
from django.http import JsonResponse

import pymongo
import ssl
import datetime
from datetime import date, timedelta
import time
import threading
from background_task import background
from django.conf import settings

import time
import datetime


def timeDifference(time):
    now = datetime.datetime.now()
    difference = now - time

    hours = difference.seconds / 60 / 60
    minutes = (hours - int(hours)) * 60

    seconds = int((minutes - int(minutes)) * 60)
    minutes = int(minutes)
    hours = round(hours)

    days = difference.days
    months = int(days / 30)
    years = round(months / 12)

    return [days, hours, minutes, seconds]

def stats(request):
    errorList = []
    thresholdList = []
    hitRateList = []
    noScans = 0
    thresholdScans = 0
    totalAmount = 0
    online = 0
    yesterday = datetime.datetime.today() - timedelta(days=1)
    now = datetime.datetime.today()

    notPinging()

    for x in settings.DB.management.find():
        try:
            cameraSettings = settings.DB.cameras.find({'cameraIdentifier': x['cameraIdentifier']}, {'storeName': 1, 'accountName': 1})
            if ('scanThreshold' in x):
                pass
            else:
                if(x['wasstraatType'] == 'kettingbaan'):
                    newSettings = {'scanThreshold': 50}

                    myquery = { "cameraIdentifier": x['cameraIdentifier'] }
                    newvalues = { "$set":  newSettings  }

                    settings.DB.management.update_one(myquery, newvalues)

            if ('wasstraatType' in x):
                pass
            else:

                newSettings = {'wasstraatType': 'ketting'}

                myquery = { "cameraIdentifier": x['cameraIdentifier'] }
                newvalues = { "$set":  newSettings  }

                settings.DB.management.update_one(myquery, newvalues)

            if ('errorList' in x):
                pass
            else:

                newSettings = {'errorList': []}

                myquery = { "cameraIdentifier": x['cameraIdentifier'] }
                newvalues = { "$set":  newSettings  }

                settings.DB.management.update_one(myquery, newvalues)
        except:
            pass


    for x in settings.DB.cameras.find():
        if('camera-b8' in str(x['cameraIdentifier'])):
            if('accountName' not in x.keys() or x['accountName'] == None and 'storeName' not in x.keys() or x['storeName'] == None):
                pass
            else:
                if('test' in x['accountName']):
                    pass
                else:
                    total = settings.DB.licensePlates.find({'cameraIdentifier': x['cameraIdentifier'], 'createdAt':{'$gte':  yesterday , '$lt' :  now}}, {'licensePlate': 1}).count()
                    if(total == 0):
                        noScans = noScans + 1
                    elif(total < x['miniThreshold']):
                        thresholdScans = thresholdScans + 1
                        percentageThreshold = total / x['miniThreshold']
                        thresholdList.append([x['accountName'], total, x['miniThreshold'], percentageThreshold])
                    else:
                        online = online + 1
                    errorList.append([x['accountName'], x['errorList']])
                    if(total >0):
                        hitRateList.append([x['accountName'], total])

    chartdata = [online, noScans, thresholdScans]

    for u in errorList:

        if(u[0] == None):
            print(u)
            errorList.remove(u)

    for u in errorList:

        if(u[0] == None):
            print(u)
            errorList.remove(u)

    for u in errorList:

        if(u[0] == None):
            print(u)
            errorList.remove(u)
    timer = settings.DB.management.find_one({"startTimer":{"$exists": True}}, {'startTimer': 1, 'beginDateTime': 1})
    print(timer)

    return render(request, 'index.html', {
        "errors": errorList,
        "threshold": thresholdList,
        "hitRate": hitRateList,
        'chartdata': chartdata,

    })

def update(request):
    errorList = []
    thresholdList = []
    hitRateList = []
    offline = 0
    online = 0
    newSettings = {}
    yesterday = datetime.datetime.today() - timedelta(days=1)
    now = datetime.datetime.today()

    notPinging()


    for x in settings.DB.cameras.find({}, {'cameraIdentifier':1, 'storeName': 1, 'accountName': 1, 'miniThreshold': 1, 'errorList': 1, 'status': 1, 'errorStatus': 1}):
        management = settings.DB.management.find_one({'cameraIdentifier': x['cameraIdentifier']})
        if ('wasstraatType' in management):
            pass
        else:

            newSettings = {'wasstraatType': 'kettingbaan'}

            myquery = { "cameraIdentifier": x['cameraIdentifier'] }
            newvalues = { "$set":  newSettings  }

            settings.DB.management.update_one(myquery, newvalues)

        management = settings.DB.management.find_one({'cameraIdentifier': x['cameraIdentifier']})
        if ('miniThreshold' in x):
            pass
        else:

            if(management['wasstraatType'] == 'kettingbaan'):
                newSettings = {'miniThreshold': 50}
            elif(management['wasstraatType'] == 'Rollover'):
                newSettings = {'miniThreshold': 25}
            elif(management['wasstraatType'] == 'Washbox'):
                newSettings = {'miniThreshold': 10}

            myquery = { "cameraIdentifier": x['cameraIdentifier'] }
            newvalues = { "$set":  newSettings  }

            settings.DB.cameras.update_one(myquery, newvalues)

        if ('errorStatus' in x):
            pass
        else:
            newSettings = {'errorStatus': 'up'}

            myquery = { "cameraIdentifier": x['cameraIdentifier'] }
            newvalues = { "$set":  newSettings  }

            settings.DB.cameras.update_one(myquery, newvalues)



        if ('errorList' in x):
            pass
        else:

            newSettings = {'errorList': []}

            myquery = { "cameraIdentifier": x['cameraIdentifier'] }
            newvalues = { "$set":  newSettings  }

            settings.DB.cameras.update_one(myquery, newvalues)
            print(x)


    for x in settings.DB.cameras.find({}, {'cameraIdentifier':1, 'storeName': 1, 'accountName': 1, 'miniThreshold': 1, 'errorList': 1, 'status': 1}):
        if(x['status'] == 'down'):
            pass
        else:

            if('camera-b8' in str(x['cameraIdentifier'])):

                total = settings.DB.licensePlates.find({'cameraIdentifier': x['cameraIdentifier'], 'createdAt':{'$gte':  yesterday , '$lt' :  now}}, {'licensePlate': 1}).count()
                if(total > 0 and total < x['miniThreshold']):
                    thresholdList.append([x['accountName'], total, x['miniThreshold']])

                elif(total == 0):
                    offline = offline + 1
                else:
                    online = online + 1
                try:
                    errorList.append([x['accountName'], x['errorList']])
                except:
                    pass
                if(total >0):
                    hitRateList.append([x['accountName'], total])


    sizes = [online, offline, len(thresholdList)]

    # explode = (0, 0, 0, 0)  # only "explode" the 2nd slice (i.e. 'Hogs')
    #
    # xdata = ['Online', 'Offline', 'onder threshold']
    chartdata = [online, offline, len(thresholdList)]

    for u in errorList:
        if(u[0] == None):
            errorList.remove(u)
    done = {
        "errors": errorList,
        "threshold": thresholdList,
        "hitRate": hitRateList,
        'chartdata': chartdata,
    }
    return JsonResponse(done)

def notPinging():
    errorList = []
    for x in settings.DB.cameras.find():
        if('lastPing' in x):

            difference = timeDifference(x['lastPing'])
            print(difference)
            if(difference[2] >= 5):

                errorList = x['errorList']
                if(1 in x['errorList']):
                    pass
                else:
                    errorList.append(1)
                    myquery = { "cameraIdentifier": x['cameraIdentifier'] }
                    newSettings = {'errorList': errorList}
                    newvalues = { "$set":  newSettings  }

                    settings.DB.management.update_one(myquery, newvalues)
            else:
                errorList = x['errorList']
                if(1 in x['errorList']):
                    x['errorList'].remove(1)
                    myquery = { "cameraIdentifier": x['cameraIdentifier'] }
                    newSettings = {'errorList': errorList}
                    newvalues = { "$set":  newSettings  }

                    settings.DB.management.update_one(myquery, newvalues)



        if('lastScan' in x):
            difference = timeDifference(x['lastScan'])
            if(difference[2] >= 15):
                errorList = x['errorList']
                if(2 in x['errorList']):
                    pass
                else:
                    errorList.append(2)
                    myquery = { "cameraIdentifier": x['cameraIdentifier'] }
                    newSettings = {'errorList': errorList}
                    newvalues = { "$set":  newSettings  }

                    settings.DB.cameras.update_one(myquery, newvalues)

            else:
                errorList = x['errorList']
                if(2 in x['errorList']):
                    print(x['accountName'], x['errorList'])
                    x['errorList'].remove(2)
                    myquery = { "cameraIdentifier": x['cameraIdentifier'] }
                    newSettings = {'errorList': errorList}
                    newvalues = { "$set":  newSettings  }

                    settings.DB.cameras.update_one(myquery, newvalues)
