import requests
import time
import os

from requests.auth import HTTPBasicAuth
requests.packages.urllib3.disable_warnings()

print("opening file")
fDataName: str = time.strftime("%d%m%Y-%H%M%S") + "-stressRun.txt"
fData = open(fDataName, 'w')

Usr = "admin"
Pwd = "Scaleio123"
Srv: str = "10.1.0.41"
baseUri = "https://{}".format(Srv)
loginUri = "{}/api/login".format(baseUri)
sdsUri = "{}/api/types/Sds/instances".format(baseUri)
deviceUri = "{}/api/types/Device/instances".format(baseUri)
hdr1 = {'content-type': 'application/json'}

Conn = requests.Session()
Conn.auth = HTTPBasicAuth(Usr, Pwd)
Conn.headers = hdr1
Conn.verify = False

print("authenticating stage 1")
r = Conn.get(loginUri)
sPwd = r.text.replace('"', '')
Conn.auth = HTTPBasicAuth(Usr, sPwd)

# create a list of SDS with sds name and sds id's
print("authenticating stage 2")
rSDS = Conn.get(sdsUri)
count = 0
for lSds in rSDS.json():
    if count == 0:
        fData.write("SDSname,SDSid" + '\n')
    sOutLine = f"{str(lSds['name'])},{str(lSds['id'])}"
    fData.write(sOutLine + '\n')
    count = count + 1

fData.write('\n')

# creat list of devices with sds ids, device id's,
# device name or current path, device URI
count = 0
arUri = ["Ford", "Volvo", "BMW"]
fData.write("devId,devName,devSdsId,devCurrentPath" + '\n')
rDev = Conn.get(deviceUri)
couterlabel = ""
for lDev in rDev.json():
    if count == 0:
        couterlabel = "Timestamp,"
    else:
        couterlabel = couterlabel + ","
    devId = str(lDev['id'])
    print("found device")
    lOutLine = f"{devId},{str(lDev['name'])},{str(lDev['sdsId'])},{str(lDev['deviceCurrentPathName'])}"
    fData.write(lOutLine + '\n')
    couterlabel = couterlabel + f"{devId} PrimaryWriteBwcnumSeconds," \
        f"{devId} PrimaryWriteBwcPrimaryWeightInKb," \
        f"{devId} PrimaryWriteBwcnumOccured," \
        f"{devId} avgWriteLatencyInMicrosec," \
        f"{devId} PrimaryReadBwcnumSeconds," \
        f"{devId} PrimaryReadBwcPrimaryWeightInKb," \
        f"{devId} PrimaryReadBwcnumOccured," \
        f"{devId} avgReadLatencyInMicrosec"
    print("cout" + couterlabel)
    stUri = lDev['links'][1]['href']
    # print(stUri)
    if count < 3:
        arUri[count] = stUri
    else:
        arUri.append(stUri)
    count = count + 1


fData.write('\n')
fData.write(couterlabel + '\n')

# for i in range(5):
while 1 == 1:
    finalLine = f"{time.strftime('%H-%M-%S')}"
    for devUri in arUri:
        rdevUri = Conn.get(f"{baseUri}{devUri}")
        if rdevUri.status_code == 200:
            jdevUri = rdevUri.json()
            print("json output")
            print(jdevUri)
            pOutLine = f"{str(jdevUri['primaryWriteBwc']['numSeconds'])}," \
                f"{str(jdevUri['primaryWriteBwc']['totalWeightInKb'])}," \
                f"{str(jdevUri['primaryWriteBwc']['numOccured'])}," \
                f"{str(jdevUri['avgWriteLatencyInMicrosec'])}," \
                f"{str(jdevUri['primaryReadBwc']['numSeconds'])}," \
                f"{str(jdevUri['primaryReadBwc']['totalWeightInKb'])}," \
                f"{str(jdevUri['primaryReadBwc']['numOccured'])}," \
                f"{str(jdevUri['avgReadLatencyInMicrosec'])}"
            finalLine = finalLine + "," + pOutLine
        else:
            pOutLine = f"{time.strftime('%H-%M-%S')},"
            for i in range(8):
                pOutLine = pOutLine + "0"
                if i < 8:
                    pOutLine = pOutLine + ","

    fData.write(finalLine + '\n')
    fData.flush()
    os.fsync(fData.fileno())
    print("just polled")
    exit()
#    time.sleep(5)

fData.close()
