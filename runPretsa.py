import sys
from pretsa import Pretsa
import pandas as pd
import profile

def executePretsa(eventLogName, k, t):
    filePath = "./PRETSA/input/" + eventLogName
    kasString = str(k) #k gets new base type int
    tasString = str(t) #t gets new base type float
    sys.setrecursionlimit(3000)
    targetFilePath = "./PRETSA/output/output_pretsa_run_.csv" #% (runID) should be added to allow server distiction between runs


    print("Load Event Log")
    eventLog = pd.read_csv(filePath, delimiter=";")
    print("Starting experiments")
    pretsa = Pretsa(eventLog)
    cutOutCases = pretsa.runPretsa(k,t)
    print("Modified " + str(len(cutOutCases)) + " cases for k=" + str(k))
    privateEventLog = pretsa.getPrivatisedEventLog()
    privateEventLog.to_csv(targetFilePath, sep=";",index=False)