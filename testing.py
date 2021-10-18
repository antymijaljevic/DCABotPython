from datetime import datetime
from os import system
import time, json

system('cls')
now = str(datetime.now())
# pairList = {now[:10]:['ADABUSD', 'BNBBUSD','ETHBUSD'], '2021-10-19':['LINKBUSD','BTCBUSD']}
# newPairLIst = {'2021-10-20':['XRPBUSD','SOLBUSD']}

filename = 'orderDB.json'
new = "NECRO"


with open(filename, "r+") as file:
    data = json.load(file)
    print(json.dumps(data, indent=4))

    data['2021-10-18'].append(new)
    
    data.update(data)

    file.seek(0)

    json.dump(data, file, indent=4, separators=(',',': '))

    print(json.dumps(data, indent=4))
