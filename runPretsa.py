import sys
from pretsa import Pretsa
import pandas as pd
import profile
import pm4py

def executePretsa(eventLogName, k, t, instructionId, instanceId, fileId):
    filePath = "./PRETSA/input/" + eventLogName
    kasString = str(k) #k gets new base type int
    tasString = str(t) #t gets new base type float
    sys.setrecursionlimit(3000)
    targetFilePath = "./PRETSA/output/output_pretsa_" + instanceId + "_run_" + instructionId + "_" + fileId + ".csv" #% (runID) should be added to allow server distiction between runs
    xesTargetFilePath = "./PRETSA/output/output_pretsa_" + instanceId + "_run_" + instructionId + "_" + fileId + ".xes" #add xes file Path for the xes output


    print("Load Event Log")
    eventLog = pd.read_csv(filePath, delimiter=";")
    print("Starting experiments")
    pretsa = Pretsa(eventLog)
    cutOutCases = pretsa.runPretsa(k,t)
    print("Modified " + str(len(cutOutCases)) + " cases for k=" + str(k))
    privateEventLog = pretsa.getPrivatisedEventLog()
    privateEventLog.to_csv(targetFilePath, sep=";",index=False)

    
    changeCounterTime = 0
    changeCounterActivity = 0
    changeCounterCaseId = 0
    for columns in privateEventLog.columns:
        if (columns.lower() == "caseid" or columns.lower() == "case id" or columns.lower() == "case_id" or columns.lower() == "case:concept:name") and changeCounterCaseId == 0:
            oldCaseIdName = columns
            privateEventLog = privateEventLog.rename(columns={oldCaseIdName:"case:concept:name"})
            changeCounterCaseId = changeCounterCaseId + 1
        if (columns.lower() == "activity" or columns.lower() == "event" or columns.lower() == "task" or columns.lower() == "action" or columns.lower() == "concept:name") and changeCounterActivity == 0:
            oldActivityName = columns
            privateEventLog = privateEventLog.rename(columns={oldActivityName:"concept:name"})
            changeCounterActivity = changeCounterActivity + 1
        if (columns.lower() == "datetime" or columns.lower() == "date" or columns.lower() == "timestamp") and changeCounterTime == 0:
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
    