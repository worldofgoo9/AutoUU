import requests
import schedule
import datetime
import json
import time
# Public Version 1.0

def waitUntil(targetH = 17.0):
    tNow = time.localtime()
    tHour = tNow.tm_hour
    tMin = tNow.tm_min
    tNow = tHour + float(tMin)/60.0
    tWait = ((targetH - tNow) % 24) * 3600.0
    print(f"Need to wait {tWait} seconds.", flush=True)
    time.sleep(tWait)


class MyError(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)

class AutoUU:
    def __init__(self,maxInvPageIndex = 1,config = {},timeSleep = 3.0,gameId = "730"):
        self.isLogin = False
        self.userId = 123456
        self.token = ""
        self.invData = None
        self.price = None
        self.config = config
        self.timeSleep = timeSleep
        self.gameId = gameId  # 730 == CSgo
        self.itemsOnSale = None
        self.maxInvPageIndex = maxInvPageIndex
        self.name = ""


    def clear(self):
        self.__init__()

    def operateSleep(self):
        time.sleep(self.timeSleep)
    
    def loadConfigs(self, pathList, encoding = "utf-8"):
        for path in pathList:
            self.__loadConfig__(path)


    def __loadConfig__(self, path="cfg.json", encoding="utf-8"):
        with open(path, "r", encoding=encoding) as f:
            config = json.load(f)
        num = len(config)
        result = {}
        for item in config:
            result[str(item['float'])] = item

        self.printLog(f"Successfully Load {num} Configurations.")

        self.config.update(result)  
        return result

    def printLog(self, info, level=0):
        if(level == 0):
            print(f"{str(datetime.datetime.now())} Level:{level} INFO: {info} ")
        else:
            print(f"{str(datetime.datetime.now())} Level:{level} ERROR: {info} ")            

    def login(self, userName, userPwd):
        url = "https://api.youpin898.com/api/user/Auth/PwdSignIn"
        headers = {
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.64 Safari/537.36",
            "accept": "application/json, text/plain, */*",
            "accept-encoding": "gzip, deflate, br",
            "accept-language": "zh-CN,zh;q=0.9",
            "apptype": '1',
            "origin": "https://www.youpin898.com",
            "referer": "https://www.youpin898.com/",
            "sec-ch-ua": '" Not A;Brand";v="99", "Chromium";v="101", "Google Chrome";v="101"',
            "sec-ch=-ua=mobile": "?0",
            "sec-ch-ua-platform": '"Windows"',
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-site"


        }
        data = {
            "code": "",
            "SessionId": "",
            "UserName": userName,
            "UserPwd": userPwd
        }

        res = requests.post(url, headers=headers, json=data).json()
        if(res["Code"] == 0):
            token = res['Data']['Token']
            self.printLog(f"Get Session Token:{token}")
            self.token = token
            self.isLogin = True
        else:
            raise MyError(f"Get Session Failed. Res code:{res['Code']},res:{res}")


        url = "https://api.youpin898.com/api/user/Account/GetUserInfo"
        headers = {

            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.64 Safari/537.36",
            "accept": "application/json, text/plain, */*",
            "accept-encoding": "gzip, deflate, br",
            "accept-language": "zh-CN,zh;q=0.9",
            "apptype": '1',
            "authorization": f"Bearer {token}",
            "origin": "https://www.youpin898.com",
            "referer": "https://www.youpin898.com/",
            "sec-ch-ua": '" Not A;Brand";v="99", "Chromium";v="101", "Google Chrome";v="101"',
            "sec-ch=-ua=mobile": "?0",
            "sec-ch-ua-platform": '"Windows"',
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-site"

        }
        res = requests.get(url, headers=headers).json()
        if(res["Code"] == 0):
            self.userId = res['Data']['UserId']
            self.name = res['Data']['NickName']
            #self.printLog(
            #    f"Get User Info. Id:{res['Data']['UserId']},Name:{res['Data']['NickName']}")
            self.isLogin = True
            #return True
        else:
            raise MyError(f"Get User Info Failed. Response code:{res['Code']}, body:{res}")

    def getInv(self):
        if(not self.isLogin):
            raise MyError("Please Login first.")
        headers = {

            "app-version": "4.1.3",
            "version": "4.1.3",
            "platform": "ios",
            "accept": "*/*",
            "accept-encoding": "br;q=1.0, gzip;q=0.9, deflate;q=0.8",
            "accept-language": "zh-Hans-CN;q=1.0, en-CN;q=0.9",
            "AppType": '3',
            "authorization": f"Bearer {self.token}",
        } # 这里实际采用的是IOS客户端的API，因为网页客户端有时会崩溃

        self.invData = []

        pageIndex = 1
        while(pageIndex <= self.maxInvPageIndex):
            url = f'''https://api.youpin898.com/api/commodity/Inventory/GetUserInventoryDataList?AppType=3&GameID=730&IsRefresh=false&ItemStatus=0&PageIndex={pageIndex}&PageSize=30&Platform=ios&Sort=0&Version=4.1.3'''
            res = requests.get(url, headers=headers).json()
            pageIndex += 1
            if(res["Code"] == 0):
                self.invData += res['Data']['ItemsInfos']
                self.operateSleep()

            else:
                raise MyError(f"Get Inv Info Failed. Response code:{res['Code']}, body:{res}")

        self.printLog(f"Get Inv Info Success. Total Num : {len(self.invData)}")

    def __getMarketPrice__(self, itemId):
        if(not self.isLogin):
            raise MyError("Please Login first.")       
        url = "https://api.youpin898.com/api/homepage/es/commodity/GetCsGoPagedList"
        itemId = str(itemId)
        headers = {

            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.64 Safari/537.36",
            "accept": "application/json, text/plain, */*",
            "accept-encoding": "gzip, deflate, br",
            "accept-language": "zh-CN,zh;q=0.9",
            "apptype": '1',
            "authorization": f"Bearer {self.token}",
            'content-type': "application/json;charset=UTF-8",
            "origin": "https://www.youpin898.com",
            "referer": "https://www.youpin898.com/",
            "sec-ch-ua": '" Not A;Brand";v="99", "Chromium";v="101", "Google Chrome";v="101"',
            "sec-ch=-ua=mobile": "?0",
            "sec-ch-ua-platform": '"Windows"',
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-site"
            # "Connection": "keep-alive",
        }
        queryShort = {"templateId": itemId, "pageSize": 30, "pageIndex": 1,
                      "sortType": 1, "listSortType": 2, "listType": 30, "stickersIsSort": False}
        queryLong = {"templateId": itemId, "pageSize": 30, "pageIndex": 1,
                     "sortType": 1, "listSortType": 3, "listType": 30, "stickersIsSort": False}

        res = requests.post(url, headers=headers, json=queryShort).json()
        if(res["Code"] == 0):
            shortPrice = float(res["Data"]['CommodityList'][0]['LeaseUnitPrice'])

        else:
            raise MyError(f"Get Short-Lease Price Failed. Response code:{res['Code']}, body:{res}")

        res = requests.post(url, headers=headers, json=queryLong).json()
        if(res["Code"] == 0):
            longPrice = float(res["Data"]['CommodityList'][0]['LeaseUnitPrice'])

        else:
            raise MyError(f"Get Long-Lease Price Failed. Response code:{res['Code']}, body:{res}")

        return {
            "shortPrice": shortPrice,
            "longPrice": longPrice,
        }
        # Query data sort by short / long lease price.

    def doPricing(self):
        if(not self.isLogin):
            raise MyError("Please Login first.")

        invNum = len(self.invData)
        price = [{} for i in range(invNum)] # Responding to each item in INV
        #itemTemp = {}
        for i in range(invNum):

            if(self.invData[i]['AssetInfo'] is None):
                price[i] = {"flag": False}
                continue
            itemFloat = str(self.invData[i]['AssetInfo']['Abrade'])
            assetId = self.invData[i]['SteamAssetID']
            itemId = self.invData[i]['TemplateInfo']['Id']
            if((itemFloat not in self.config.keys()) or (self.invData[i]['Tradable'] == False) ): #or (itemId in itemTemp.keys())
                price[i] = {"flag": False}
                continue
            #print(f"{i} {itemFloat} {self.invData[i]['OnSale']} {self.invData[i]}")

            time.sleep(self.timeSleep)
            marketPrice = self.__getMarketPrice__(itemId)
            shortMarketPrice = marketPrice['shortPrice']
            longMarketPrice = marketPrice['longPrice']
            # Do pricing.

            strategy = self.config[itemFloat]['strategy']
            if(strategy == "auto"):
                shortPrice = max(
                    self.config[itemFloat]['shortPrice'], shortMarketPrice*0.985-0.01)
                longPrice = max(
                    self.config[itemFloat]['longPrice'], longMarketPrice*0.985-0.01)
            elif(strategy == "short"):
                shortPrice = max(
                    self.config[itemFloat]['shortPrice'], shortMarketPrice*0.97-0.01)
                longPrice = max(
                    self.config[itemFloat]['longPrice'], longMarketPrice*1.015+0.01)

            elif(strategy == "long"):
                shortPrice = max(
                    self.config[itemFloat]['shortPrice'], shortMarketPrice*1.015+0.01)
                longPrice = max(
                    self.config[itemFloat]['longPrice'], longMarketPrice*0.97-0.01)

            elif(strategy == "fix"):
                # Fixed.
                shortPrice = self.config[itemFloat]['shortPrice']
                longPrice = self.config[itemFloat]['longPrice']
            else:
                
                self.printLog(
                    f"Unvalid strategy {strategy} ------ item float {itemFloat}", 2)
                price[i] = {"flag": False}
                continue
            shortPrice = round(shortPrice, 2)
            longPrice = round(longPrice, 2)
            valuePrice = self.config[itemFloat]['valuePrice']
            maxDay = max(self.config[itemFloat]['maxDay'], 8)
            message = self.config[itemFloat]['message']
            #itemTemp[itemId] = True
            price[i] = {"flag": True, "assetId": int(assetId), "templateId": int(
                itemId), "itemFloat": itemFloat, "shortPrice": shortPrice, "longPrice": longPrice, "valuePrice": valuePrice, "maxDay": maxDay, "message": message}
        self.price = price
        #return price

    def putOnSale(self):
        if(not self.isLogin):
            raise MyError("Please Login first.")
        
        itemInfos = []
        for item in self.price:
            if(item['flag'] == True):
                itemInfos.append(
                    {
                        "assetId": item['assetId'], "commodityTemplateId": item['templateId'], "remark": item['message'], "charge": item['valuePrice'], "price": item['valuePrice'],
                        "IsCanLease": True, "IsCanSold": True,
                        "LeaseMaxDays": item['maxDay'], "LeaseUnitPrice": item['shortPrice'], "LongLeaseUnitPrice": item['longPrice'], "LongLeaseDays": item['maxDay'], "LeaseDeposit": item['valuePrice']

                    }
                )

        num = len(itemInfos)
        if(num == 0):
            self.printLog(f"Nothing to be put onto sell.")
            return True

        # Apply App for Key
        url = f"https://api.youpin898.com/api/youpin/detect/detection/1/{self.userId}/0/app"
        #itemId = str(itemId)
        headers = {

            # "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:72.0) Gecko/20100101 Firefox/72.0 micromessenger",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.64 Safari/537.36",
            "accept": "application/json, text/plain, */*",
            "accept-encoding": "gzip, deflate, br",
            "accept-language": "zh-CN,zh;q=0.9",
            "apptype": '1',
            "authorization": f"Bearer {self.token}",
            'content-type': "application/json;charset=UTF-8",
            "origin": "https://www.youpin898.com",
            "referer": "https://www.youpin898.com/",
            "sec-ch-ua": '" Not A;Brand";v="99", "Chromium";v="101", "Google Chrome";v="101"',
            "sec-ch=-ua=mobile": "?0",
            "sec-ch-ua-platform": '"Windows"',
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-site"
            # "Connection": "keep-alive",

        }
        res = requests.get(url, headers=headers).json()
        if(res["code"] == 0):
            key = res['data']['key']
            self.printLog(f"Get App Key Succ. Key:{key}")
        else:
            raise MyError(f"Get App Key Failed. Response code:{res['Code']}, body:{res}")
            #return False

        # Sell items
        url = f"https://api.youpin898.com/api/commodity/Inventory/SellInventoryWithLease"

        payload = {
            "gameId": "730",  # Csgo
            "itemInfos": itemInfos,
            "key": key
        }


        res = requests.post(url, headers=headers, json=payload).json()

        if(res["Code"] == 0):
            self.printLog(f"Sell {num} items Succ.")
            return num
        else:
            raise MyError(f"Put on Sale Failed. Response code:{res['Code']}, body:{res}")


def loadConfigIndex(path = "configIndex.json"):
    with open(path, "r", encoding = "utf-8") as f:
        configIndex = json.load(f)
    return configIndex

def run():
    # Try for muiltiple times

    configIndex = loadConfigIndex()
    uu = AutoUU(maxInvPageIndex = configIndex['maxInvPage'])
    uu.printLog("Start !")
    retryTimes = configIndex["retryTimes"]
    retryInterval = configIndex["retryInterval"]
    userName = configIndex["userName"]
    userPwd = configIndex["userPwd"]

    flag = 0 # tried times

    while(flag < retryTimes and flag >= 0):
        if(flag > 0):
            uu.printLog("Retrying , time : " + str(flag) , 1)

        flag += 1
        uu.loadConfigs(pathList = configIndex["configPath"])
        try:
            uu.login(userName, userPwd)
            uu.printLog("Login Finished !")
            uu.operateSleep()
            uu.getInv()
            uu.printLog("Get INV Finished !")
            uu.operateSleep()
            uu.doPricing()
            uu.printLog("Do Pricing Finished !")
            uu.operateSleep()
            uu.putOnSale()
            uu.printLog("Put On Sale Finished !")
            uu.operateSleep()
            
        except MyError as e:
            uu.printLog(e.value , 1)
            uu.printLog(f"Retry after {retryInterval} seconds." , 0)
            time.sleep(retryInterval)
        
        except Exception as e:
            uu.printLog(e , 2)
            uu.printLog(f"Retry after {retryInterval} seconds." , 0)
            time.sleep(retryInterval)
        
        else:
            flag = -1 # Finish
            uu.printLog(f"Routine Finished !")
            break
        
if __name__ == "__main__":
    configIndex = loadConfigIndex()
    run()

    schedule.every().day.at(configIndex["runTime"]).do(run)
    while(True):
        schedule.run_pending()


