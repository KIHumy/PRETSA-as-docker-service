import requests
import time
import json
import socket
import runPretsa
#this file was written by Thorwin Bergholz
algoName = "PRETSA"
algoId = socket.gethostname()
algoIdentity = {"identification":{"name":algoName, "id":algoId}}

def serverHealthcheck():
    while True:
        try:
            healthcheck = requests.get("http://cliandanalyzer:8000/healthcheck")
            if healthcheck.status_code == 200:
                return
        except:
            time.sleep(5)

def mainEntrypoint():
    serverHealthcheck()
    stayActive = True
    while stayActive:
        instructionRequestAnswer = requests.post("http://cliandanalyzer:8000/task", json={"name":algoName, "id":algoId})
        if instructionRequestAnswer.json() != {"instruction":"no_instruction"}:
            print("Received a new instruction.", flush=True)
            print(instructionRequestAnswer.json(), flush=True)
            startInstructionHandler(instructionRequestAnswer.json())
        time.sleep(5)

def collectRequirementsForAlgo():
    #logName = {"name":"logName", "value":"someString", "description":"This tring should be the name of an event log.", "type":"string"}
    k = {"name":"k", "lowerBound":"1", "upperBound":None, "autoAdept":True, "autoStart": 1, "autoSigma": 2, "keyWordBoundUpper": "NUMBER_OF_TRACES", "keyWordBoundLower": None, "relativeInitial": 0.5, "choice": "exp_b_2", "type":"int"} #no default values there where no in the code
    t = {"name":"t", "lowerBound":"0.04", "upperBound":"1.0", "autoAdept":True, "autoStart": 0.5, "autoSigma": 0.25, "keyWordBoundUpper": None, "keyWordBoundLower": None, "relativeInitial": None, "choice": None, "type":"float"} #no default values there where no in the code. t needs to be bigger then 0.03
    algoVariables = [k, t]
    return {**algoIdentity, "inputFormat":"csv", "outputStructure":"eventLog", "requirements":algoVariables}

def startInstructionHandler(instruction):
    print("Entered the instruction block.", flush=True)
    if instruction["instruction"] == "start_n_test":
        print("Accessed n_test function.", flush=True)
        requests.post("http://cliandanalyzer:8000/result/status", json={**algoIdentity, "instructionId":instruction["instructionId"], "status":"network_stable", "fileId":""})
    if instruction["instruction"] == "send_requirements":
        print("Accessed requirements function.", flush=True)
        jsonRequirements = collectRequirementsForAlgo()
        requests.post("http://cliandanalyzer:8000/myRequirements", json=jsonRequirements)
    if instruction["instruction"] == "comparison" or instruction["instruction"] == "autoCompare":
        print("Accessed Template function.", flush=True)
        algoDictionary = instruction.get("payload")
        logName = "someString"
        k = 2
        t = 20.0
        for inputValues in algoDictionary["inputParameters"]:
            if inputValues["name"] == "logName":
                logName = inputValues["value"]
            if inputValues["name"] == "k":
                k = inputValues["value"]
            if inputValues["name"] == "t":
                t = inputValues["value"]
        maximalTryNumber = 3
        tryNumber = 0
        while tryNumber < maximalTryNumber:
            try:
                runPretsa.executePretsa(logName, k, t, instruction["instructionId"], algoIdentity["identification"]["id"], instruction["fileId"])
                tryNumber = maximalTryNumber
            except:
                tryNumber = tryNumber + 1
        print("Sending the result of the template function to the server.", flush= True)
        if instruction["instruction"] == "comparison":
            requests.post("http://cliandanalyzer:8000/result/status", json={**algoIdentity, "instructionId":instruction["instructionId"], "status":"finished_privacy_enhancing_algorithm", "fileId":instruction["fileId"]})
        else:
            requests.post("http://cliandanalyzer:8000/result/status", json={**algoIdentity, "instructionId":instruction["instructionId"], "status":"finished_privacy_enhancing_algorithm_for_auto_compare", "fileId":instruction["fileId"]})

if __name__ == "__main__":
    mainEntrypoint()
    #executePretsa() from runPretsa.py
