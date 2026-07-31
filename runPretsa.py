import sys
from pretsa import Pretsa
import pandas as pd
import profile
import pm4py
import datetime

#sanitizer function so that pretsa works with standard event logs. The function is based on add_annotation_duration.py.
def sanitizeInputLog(eventLog):
    caseIdColName = "Case ID" #copied from add_annotation_duration.py
    durationColName = "Duration" #copied from add_annotation_duration.py
    timeStampColName = "Complete Timestamp" #copied from add_annotation_duration.py
    activityColName = "Activity"
    columnNames = eventLog.columns.tolist()
    existsCaseId = False
    existsDuration = False
    existsTimeStamp = False
    existsActivity = False
    for name in columnNames:
        if name == durationColName:
            existsDuration = True
        if name == caseIdColName:
            existsCaseId = True
        if name == timeStampColName:
            existsTimeStamp = True
        if name == activityColName:
            existsActivity = True
    if existsDuration == True and existsCaseId == True and existsTimeStamp == True and existsActivity:
        return eventLog
    if existsCaseId == False or existsTimeStamp == False or existsActivity == False:
        columnNamesWithDuration = eventLog.columns.tolist()
        caseId = "someString"
        activity = "someString"
        timeStamp = "someString"
        for elements in columnNamesWithDuration:
            if (elements.lower() == "caseid" or elements.lower() == "case id" or elements.lower() == "case_id" or elements.lower() == "case:concept:name") and existsCaseId == False:
                caseId = elements
            elif (elements.lower() == "activity" or elements.lower() == "concept:name") and existsActivity == False:
                activity = elements
            elif (elements.lower() == "timestamp" or elements.lower() == "complete timestamp" or elements.lower() == "time:timestamp") and existsTimeStamp == False:
                timeStamp = elements
        if caseId != "someString":
            eventLog = eventLog.rename(columns={caseId:caseIdColName})
        if activity != "someString":
            eventLog = eventLog.rename(columns={activity:activityColName})
        if timeStamp != "someString":
            eventLog = eventLog.rename(columns={timeStamp:timeStampColName})
    eventLog = eventLog.sort_values([caseIdColName, timeStampColName])
    if existsDuration == False:
        eventLog[durationColName] = None
        #copied from add_annotation_duration.py. The only modifications are changes so it works with a pandas dataframe instead of reading a file.
        eventLog[timeStampColName] = pd.to_datetime(eventLog[timeStampColName])
        currentCase = ""
        for rowIndex in eventLog.index:
            newTimeStamp = eventLog.at[rowIndex, timeStampColName] #'%Y/%m/%d %H:%M:%S.%f'
            if currentCase != eventLog.at[rowIndex, caseIdColName]:
                currentCase = eventLog.at[rowIndex, caseIdColName]
                duration = 0.0
            else:
                duration = (newTimeStamp - oldTimeStamp).total_seconds()
            oldTimeStamp = newTimeStamp
            eventLog.at[rowIndex, durationColName] = duration
        eventLog[timeStampColName] = eventLog[timeStampColName].dt.strftime('%Y/%m/%d %H:%M:%S.%f')
        #until here
    return eventLog

def executePretsa(eventLogName, k, t, instructionId, instanceId, fileId):
    filePath = "./PRETSA/input/" + eventLogName
    kasString = str(k) #k gets new base type int
    tasString = str(t) #t gets new base type float
    sys.setrecursionlimit(3000)
    targetFilePath = "./PRETSA/output/output_pretsa_" + instanceId + "_run_" + instructionId + "_" + fileId + ".csv" #% (runID) should be added to allow server distiction between runs
    xesTargetFilePath = "./PRETSA/output/output_pretsa_" + instanceId + "_run_" + instructionId + "_" + fileId + ".xes" #add xes file Path for the xes output


    print("Load Event Log")
    eventLog = pd.read_csv(filePath, delimiter=";")
    sanitizedInputLog = sanitizeInputLog(eventLog)
    print("Starting experiments")
    pretsa = Pretsa(sanitizedInputLog)
    cutOutCases = pretsa.runPretsa(k,t)
    print("Modified " + str(len(cutOutCases)) + " cases for k=" + str(k))
    privateEventLog = pretsa.getPrivatisedEventLog()
    privateEventLog.to_csv(targetFilePath, sep=";",index=False)

    
    changeCounterTime = 0
    changeCounterActivity = 0
    changeCounterCaseId = 0
    for columns in privateEventLog.columns.tolist():
        if (columns.lower() == "caseid" or columns.lower() == "case id" or columns.lower() == "case_id" or columns.lower() == "case:concept:name"):
            if changeCounterCaseId == 0:
                oldCaseIdName = columns
                privateEventLog = privateEventLog.rename(columns={oldCaseIdName:"case:concept:name"})
            changeCounterCaseId = changeCounterCaseId + 1
        if (columns.lower() == "activity" or columns.lower() == "concept:name"):
            if changeCounterActivity == 0:
                oldActivityName = columns
                privateEventLog = privateEventLog.rename(columns={oldActivityName:"concept:name"})
            changeCounterActivity = changeCounterActivity + 1
        if (columns.lower() == "datetime" or columns.lower() == "date" or columns.lower() == "timestamp" or columns.lower() == "complete timestamp" or columns.lower() == "time:timestamp"):
            if changeCounterTime == 0:
                oldTimestampName = columns
                privateEventLog = privateEventLog.rename(columns={oldTimestampName:"time:timestamp"})
            changeCounterTime = changeCounterTime + 1
    if changeCounterTime > 1 or changeCounterCaseId > 1 or changeCounterActivity > 1:
        print("Warning: The csv file might not have been converted to xes correctly please check manually.", flush=True)
    if changeCounterTime == 0:
        privateEventLog["time:timestamp"] = pd.to_datetime("2000-01-01T00:00:00.000+00:00") #add dummy datetime to match xes requirements
    if (changeCounterCaseId == 0 or changeCounterActivity == 0) == False:
        xes_output = pm4py.format_dataframe(privateEventLog, case_id= "case:concept:name", activity_key= "concept:name", timestamp_key="time:timestamp") #convert pandas frame to xes format
        pm4py.write_xes(xes_output, xesTargetFilePath) #output .xes file
    else:
        print("Xes conversion failed because csv file could not be converted.")
    