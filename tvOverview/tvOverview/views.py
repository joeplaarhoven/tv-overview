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
    offline = 0
    totalAmount = 0
    online = 0
    yesterday = datetime.datetime.today() - timedelta(days=1)
    now = datetime.datetime.today()

    notPinging()

    for x in settings.DB.management.find():
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
            print(x)

    for x in settings.DB.management.find():
        cameraSettings = settings.DB.cameras.find_one({'cameraIdentifier': x['cameraIdentifier']}, {'storeName': 1, 'accountName': 1})
        print(cameraSettings)
        #
        # if(x['errorList'] == []):
        #
        #     if(settings.STARTTIMER == False):
        #         pass
        #     else:
        #         settings.STARTTIMER = True
        # else:
        #     settings.STARTTIMER = False

        if(x['status'] == 'down'):
            pass
        else:
            if('camera-b8' in str(x['cameraIdentifier'])):

                total = settings.DB.licensePlates.find({'cameraIdentifier': x['cameraIdentifier'], 'createdAt':{'$gte':  yesterday , '$lt' :  now}}, {'licensePlate': 1}).count()
                totalAmount += total
                if(total > 0 and total < x['scanThreshold']):
                    thresholdList.append([cameraSettings['accountName'], total, x['scanThreshold']])

                elif(total == 0):
                    offline = offline + 1
                else:
                    online = online + 1
                try:
                    errorList.append([cameraSettings['accountName'], x['errorList']])
                except:
                    pass
                if(total >0):
                    hitRateList.append([cameraSettings['accountName'], total])

    print(totalAmount)
    sizes = [online, offline, len(thresholdList)]
    # if(settings.STARTTIMER == False):
    #     request.session['startTimer'] = 0
    # elif(settings.STARTTIMER == True):
    #     request.session['startTimer'] = 1
    # explode = (0, 0, 0, 0)  # only "explode" the 2nd slice (i.e. 'Hogs')
    #
    # xdata = ['Online', 'Offline', 'onder threshold']
    chartdata = [online, offline, len(thresholdList)]

    for u in errorList:
        if(u[0] == None):
            errorList.remove(u)


    print(errorList)
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
    yesterday = datetime.datetime.today() - timedelta(days=1)
    now = datetime.datetime.today()

    notPinging()


    for x in settings.DB.cameras.find({}, {'cameraIdentifier':1, 'storeName': 1, 'accountName': 1, 'scanThreshold': 1, 'errorList': 1, 'status': 1}):
        if ('scanThreshold' in x):
            pass
        else:

            newSettings = {'scanThreshold': 50}

            myquery = { "cameraIdentifier": x['cameraIdentifier'] }
            newvalues = { "$set":  newSettings  }

            settings.DB.cameras.update_one(myquery, newvalues)

        if ('wasstraatType' in x):
            pass
        else:

            newSettings = {'wasstraatType': 'ketting'}

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


    for x in settings.DB.cameras.find({}, {'cameraIdentifier':1, 'storeName': 1, 'accountName': 1, 'scanThreshold': 1, 'errorList': 1, 'status': 1}):
        if(x['status'] == 'down'):
            pass
        else:

            if('camera-b8' in str(x['cameraIdentifier'])):

                total = settings.DB.licensePlates.find({'cameraIdentifier': x['cameraIdentifier'], 'createdAt':{'$gte':  yesterday , '$lt' :  now}}, {'licensePlate': 1}).count()
                if(total > 0 and total < x['scanThreshold']):
                    thresholdList.append([x['accountName'], total, x['scanThreshold']])

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

    for x in settings.DB.management.find():

        if('lastPing' in x):
            if(x['status'] != 'down'):
                difference = timeDifference(x['lastPing'])
                if(difference[2] >= 5):

                    errorList = x['errorList']
                    if(1 in x['errorList']):
                        pass
                    else:
                        x['errorList'].append(1)
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
            if(x['status'] != 'down'):
                difference = timeDifference(x['lastScan'])
                if(difference[2] >= 15):
                    errorList = x['errorList']
                    if(2 in x['errorList']):
                        pass
                    else:
                        x['errorList'].append(2)
                        myquery = { "cameraIdentifier": x['cameraIdentifier'] }
                        newSettings = {'errorList': errorList}
                        newvalues = { "$set":  newSettings  }

                        settings.DB.management.update_one(myquery, newvalues)

                else:
                    errorList = x['errorList']
                    if(2 in x['errorList']):
                        print(x['accountName'], x['errorList'])
                        x['errorList'].remove(2)
                        myquery = { "cameraIdentifier": x['cameraIdentifier'] }
                        newSettings = {'errorList': errorList}
                        newvalues = { "$set":  newSettings  }

                        settings.DB.management.update_one(myquery, newvalues)
