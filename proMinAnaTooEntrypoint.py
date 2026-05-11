import requests
import time
import json
import socket
import runPretsa

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
    logName = {"name":"logName", "value":"someString", "description":"This tring should be the name of an event log.", "type":"string"}
    k = {"name":"k", "lowerBound":"2", "upperBound":"2", "type":"int"} #no default values there where no in the code
    t = {"name":"t", "lowerBound":"20.0", "upperBound":"20.0", "type":"float"} #no default values there where no in the code
    algoVariables = [logName, k, t]
    return {**algoIdentity, "requirements":algoVariables}

def startInstructionHandler(instruction):
    print("Entered the instruction block.", flush=True)
    if instruction == {"instruction":"start_n_test"}:
        print("Accessed n_test function.", flush=True)
        requests.post("http://cliandanalyzer:8000/result/status", json={**algoIdentity, "status":"network_stable"})
    if instruction == {"instruction":"send_requirements"}:
        print("Accessed requirements function.", flush=True)
        jsonRequirements = collectRequirementsForAlgo()
        requests.post("http://cliandanalyzer:8000/myRequirements", json=jsonRequirements)
    if isinstance(instruction.get("instruction"), dict):
        print("Accessed Template function.", flush=True)
        algoDictionary = instruction.get("instruction")
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
        runPretsa.executePretsa(logName, k, t)
    return

if __name__ == "__main__":
    mainEntrypoint()
    #executePretsa() from runPretsa.py
