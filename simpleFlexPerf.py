

import requests
import time

from requests.auth import HTTPBasicAuth
requests.packages.urllib3.disable_warnings()

print("opening file")
fDataName: str = time.strftime("%d%m%Y-%H%M%S") + "-stressRun.txt"
fData = open(fDataName, 'w')

Usr = "admin"
Pwd = "Flex1234"
Srv: str = "192.168.116.3"
bUri = "https://" + Srv
lUri = bUri + "/api/login"
sUri = bUri + "/api/types/Sds/instances"
dUri = bUri + "/api/types/Device/instances"
hdr1 = {'content-type': 'application/json'}

Conn = requests.Session()
Conn.auth = HTTPBasicAuth(Usr, Pwd)
Conn.headers = hdr1
Conn.verify = False

print("authenticating stage 1")
r = Conn.get(lUri)
sPwd = r.text.replace('"', '')
Conn.auth = HTTPBasicAuth(Usr, sPwd)

# create a list of SDS with sds name and sds id's
print("authenticating stage 2")
rSDS = Conn.get(sUri)
count = 0
for lSds in rSDS.json():
    if count == 0:
        fData.write("SDSname,SDSid" + '\n')
    sOutLine = str(lSds['name'])
    sOutLine = sOutLine + ","
    sOutLine = sOutLine + str(lSds['id'])
    fData.write(sOutLine + '\n')

fData.write('\n')

# creat list of devices with sds ids, device id's,
# device name or current path, device URI
count = 0
arUri = ["Ford", "Volvo", "BMW"]
stUri = ""
sOutLine = ""
lOutLine = ""
fData.write("devId,devName,devSdsId,devCurrentPath" + '\n')
rDev = Conn.get(dUri)

for lDev in rDev.json():
    if count > 0:
        sOutLine = sOutLine + ","
        lOutLine = lOutLine + "\n"
    devId = str(lDev['id'])
    print("found device")
    lOutLine = lOutLine + devId
    lOutLine = lOutLine + ","
    lOutLine = lOutLine + str(lDev['name'])
    lOutLine = lOutLine + ","
    lOutLine = lOutLine + str(lDev['sdsId'])
    lOutLine = lOutLine + ","
    lOutLine = lOutLine + str(lDev['deviceCurrentPathName'])

    sOutLine = sOutLine + devId + " totalWriteBwcnumSeconds"
    sOutLine = sOutLine + ","
    sOutLine = sOutLine + devId + " totalWriteBwctotalWeightInKb"
    sOutLine = sOutLine + ","
    sOutLine = sOutLine + devId + " totalWriteBwcnumOccured"
    sOutLine = sOutLine + ","
    sOutLine = sOutLine + devId + " avgWriteLatencyInMicrosec"
    sOutLine = sOutLine + ","
    sOutLine = sOutLine + devId + " totalReadBwcnumSeconds"
    sOutLine = sOutLine + ","
    sOutLine = sOutLine + devId + " totalReadBwctotalWeightInKb"
    sOutLine = sOutLine + ","
    sOutLine = sOutLine + devId + " totalReadBwcnumOccured"
    sOutLine = sOutLine + ","
    sOutLine = sOutLine + devId + " avgReadLatencyInMicrosec"
    stUri = lDev['links'][1]['href']
    # print(stUri)
    if count < 3:
        arUri[count] = stUri
    else:
        arUri.append(stUri)
    count = count + 1

fData.write(lOutLine + '\n')
fData.write('\n')
fData.write(sOutLine + '\n')

#for i in range(5):
while 1 == 1:
    pOutLine = ""
    pOutLine = time.strftime("%H-%M-%S")
    for devUri in arUri:
        # print(bUri + devUri)
        rdevUri = Conn.get(bUri + devUri)
        if rdevUri.status_code == "200":
            jdevUri = rdevUri.json()
            pOutLine = pOutLine + ","
            pOutLine = pOutLine + str(jdevUri['totalWriteBwc']['numSeconds'])
            pOutLine = pOutLine + ","
            pOutLine = pOutLine + str(jdevUri['totalWriteBwc']['totalWeightInKb'])
            pOutLine = pOutLine + ","
            pOutLine = pOutLine + str(jdevUri['totalWriteBwc']['numOccured'])
            pOutLine = pOutLine + ","
            pOutLine = pOutLine + str(jdevUri['avgWriteLatencyInMicrosec'])
            pOutLine = pOutLine + ","
            pOutLine = pOutLine + str(jdevUri['totalReadBwc']['numSeconds'])
            pOutLine = pOutLine + ","
            pOutLine = pOutLine + str(jdevUri['totalReadBwc']['totalWeightInKb'])
            pOutLine = pOutLine + ","
            pOutLine = pOutLine + str(jdevUri['totalReadBwc']['numOccured'])
            pOutLine = pOutLine + ","
            pOutLine = pOutLine + str(jdevUri['avgReadLatencyInMicrosec'])
        else:
            for i in range(8):
                pOutLine = pOutLine + "0,"

    fData.write(pOutLine + '\n')
    print("just polled")
    time.sleep(5)

fData.close()
