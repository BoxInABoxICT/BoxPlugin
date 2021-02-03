# This program has been developed by students from the bachelor Computer Science at Utrecht University within the
# Software and Game project course
# ©Copyright Utrecht University Department of Information and Computing Sciences.

""" This file is not a part of the finished product, it's only use is to one-time convert the testdata to real data"""

import json

json_file = open("DTData.json", encoding = 'UTF-8')
outfile = open("DTout.json", 'w')
data = json.load(json_file)
idnum = 0
statements = list()

for attempt in data:
  account = {
    "homePage": "http://www.boxinabox.nl",
    "name": attempt["userHash"]
  }
  actor = {
    "account": account
  }
  
  verb = {
    "id": "https://adlnet.gov/expapi/verbs/completed",
    "display": {
      "en-US" : "completed"
    }
  }
  
  object = {
    "id": "https://en.dialoguetrainer.app/scenario/play" + str(attempt["scenarioID"]),
    "definition": {
      "type": "http://boxinabox.nl/activities/dialoguetrainer-session",
      "name": {
        "en-US" : "DialogueTrainer session"
      }
    }
  }
  
  partialResults = {}
  for partialResult in attempt['results']['results']:
    newPartialResult = {}
    for key in ['type','value']:
      newPartialResult[key] = partialResult[key]
    partialResults[partialResult['name']] = newPartialResult
    
  
  result = {
    "score": {
      "raw": attempt['totalScore']
    },
    "extensions": {
      "http://www.boxinabox.nl/extensions/multiple-results": partialResults
    }
  }
  
  ids = {}
  i = 0
  for dialogue in attempt['history']['dialogue']:
    ids[i]=dialogue['id']
    i+=1
  
  context = {
    "platform": "DialogueTrainer",
    "language": attempt['languageCode'],
    "extensions": {
      "http://www.boxinabox.nl/extensions/dialogue": ids
    },
   "contextActivities": {
      "category": [
        {
          "id": "http://en.dialoguetrainer.app",
          "definition": {
            "type": "http://id.tincanapi.com/activitytype/source",
            "name": {
              "en": "DialogueTrainer"
            }
          },
          "objectType": "Activity"
        }
      ]
    } 
  }
  
  timestamp = attempt['date']
  
  statement = {
    "actor": actor,
    "verb": verb,
    "object": object,
    "result": result,
    "context": context,
    "timestamp": timestamp
  }
  
  
  
  statements.append(statement)
  
outfile.write(json.dumps(statements, indent = 2))
  