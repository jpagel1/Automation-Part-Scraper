"""3/11/23 Automation Part Scraper - JSP"""

import requests
from bs4 import BeautifulSoup
import re
import csv
import datetime
from os import path
from time import sleep,strftime, localtime
import json
from random import randint
import googleDriveApiFunctions as googs


def get_part_info_ifm(part = None, discount = 0):
    """This takes in an IFM part number and returns the cost, and lead time info"""
    
    datareturned = {}
    datareturned['Cost'] = 0
    datareturned['In Stock'] = 0
    datareturned['Backorder Info'] = 'Unknown'

    #Sleep for a bit to not bother ifm
    sleep(randint(1,5))

    try:
        #Get price
        price_url = 'https://www.ifm.com/restservices/us/en/productdetail/'
        combined_url = price_url+part

        #Get Requests
        header = {'User-Agent': 'Mozilla/5.0'}
        raw_html = requests.get(combined_url,headers=header)

        #check if valid response
        if (raw_html.status_code == 200):
            #Load Response
            priceResponse = json.loads(raw_html.content)
            #print(priceResponse['price'])
            finalprice = float(priceResponse['price']) * (1-(int(discount)/100))
            #print(str(finalprice))

            datareturned['Cost'] = '{0:.2f}'.format(finalprice)

        else:
            return datareturned
        
        try:
            #Lets ask for just 1, and get the lead time
            getquantityurl = 'https://www.ifm.com/restservices/us/en/availability/'
            qtyyend = '/availability/1/ST'
            getquantityurlfull = getquantityurl+part+qtyyend

            #Sleep for a bit to not bother ifm
            sleep(randint(1,5))

            raw_htmlqty = requests.get(getquantityurlfull,headers=header)
            
            if (raw_html.status_code == 200):
                qtyJson = json.loads(raw_htmlqty.content)

                #Format Into Datetime
                tempval = (int(qtyJson['availabilityDate']))/1000
                dateformatted = strftime('%m/%d/%Y', localtime(tempval))

                datareturned['In Stock'] = int(qtyJson['availableQuantity'])
                
                #Only put the date if it is not today
                d = datetime.datetime.now()
                formattedT = d.strftime('%m/%d/%Y')
                
                if (formattedT == dateformatted):
                    datareturned['Backorder Info']=''
                else:
                    datareturned['Backorder Info']=dateformatted
            else:
                return datareturned
        
        except:
            return datareturned

    except:
        return datareturned

    return datareturned

def get_part_info_AD(url = None,part = None, discount=0):
    """Takes in Base URL and Part # and scrapes automation direct for cost, stock count, and lead time info"""
    
    #Build Dict to Return
    datareturned = {}
    datareturned['Cost'] = 0
    datareturned['In Stock'] = 0
    datareturned['Backorder Info'] = ''

    if ((url is not None) or (part is not None)):

        #Sleep for a bit to not bother AD
        sleep(randint(1,5))

        #Build url
        combined_url = url+part.lower()

        header = {'User-Agent': 'Mozilla/5.0'}
        raw_html = requests.get(combined_url,headers=header)
        
        #check if valid response
        if (raw_html.status_code == 200):

            data = BeautifulSoup(raw_html.text, 'html.parser')

            #Store data
            availableInStock = 0
            backorderString = ''
            Cost=0

            #Get the Backorder or In Stock Count
            stockCount = data.find(id='stockStatus-0')

            #Get the Cost
            fis = data.findAll('div',class_='adc-green')
            #print(fis)
            if (len(fis) > 1):
                costRaw = fis[1].text.strip()
                costRawRemove = costRaw.replace('$','')
                Cost = float(costRawRemove) * (1-(int(discount)/100))
            else:
                costRaw = fis[0].text.strip()
                costRawRemove = costRaw.replace('$','')
                Cost = float(costRawRemove) * (1-(int(discount)/100))

            try:
                #print(stockCount.prettify())
                fi = stockCount.find("span",class_='adc-green')

                if (fi==None):
                    #Backordered
                    backInfo = stockCount.find(id=re.compile('itemBackorderInfo'))
                    backInfoL = backInfo.text.split()
                    backorderString = f"There will be {backInfoL[0]} available {backInfoL[3]}"

                else:
                    #In Stock
                    listItem = fi.text.split()
                    for item in listItem:
                        if (item.isnumeric()):
                            availableInStock = int(item)

                #print(f"There are {availableInStock} in stock")
            except:
                backorderString = 'Item is not Currently Orderable'
                #print("Part is Unavailable")
            
            #Build Dict
            datareturned['Cost'] = Cost
            datareturned['In Stock'] = availableInStock
            datareturned['Backorder Info'] = backorderString

        return datareturned
    
    else:
        return datareturned

def ScrapeDatatoCSV():
    
    #Read In CSV
    fileName = 'AutomationItemsRequested.csv'
    file = open(fileName, "r")
    data = list(csv.reader(file, delimiter=","))
    file.close()

    #Updated CSV
    newList = []
    header = data[0]
    newList.append(header)

    i=0
    for item in data:
        if (i != 0):
            print(f"Loading Component #{i}")
            newItem = []

            Component = item[0]
            Description = item[1]
            Vender = item[2]
            BaseURL = item[3]
            Discount = item[4]

            if (Vender == 'Automation Direct'):
                dictreturn = get_part_info_AD(url=BaseURL,part=Component,discount=Discount)
            elif (Vender == 'IFM'):
                dictreturn = get_part_info_ifm(part = Component,discount=Discount)
            else:
                dictreturn = {'Cost':0,'In Stock':0,'Backorder Info':None}
            Price = dictreturn['Cost']
            InStock = dictreturn['In Stock']
            ExpectedString = dictreturn['Backorder Info']
            newItem = [Component,Description,Vender,BaseURL,Discount,Price,InStock,ExpectedString]
            newList.append(newItem)
        i+=1

    #Update Todays CSV
    with open(fileName, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerows(newList)

    #Save the CSV as Year, Month, Day. Can Get Trends Later On
    d = datetime.datetime.now()
    formattedT = d.strftime('%Y_%m_%d')
    historicalfilename = 'HistoricalData/'+formattedT+'_'+fileName

    if (path.exists(historicalfilename) is False):

        with open(historicalfilename, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerows(newList)

if __name__ == '__main__':
    
    #First Grab New Automation Direct Items.csv List
    success = googs.downloadADcsv()
    
    #If no issues grabbing latest data. otherwise just end
    if (success):
        #Use Downloaded CSV to Calculate Values
        ScrapeDatatoCSV()
        
        #Upload the new Historical Data file to Google Sheets
        fileName = 'AutomationItemsRequested.csv'
        d = datetime.datetime.now()
        formattedT = d.strftime('%Y_%m_%d')
        historicalfilename = 'HistoricalData/'+formattedT+'_'+fileName
        googs.export_to_gsheet(historicalfilename,parents=['1kiyGWEhbrNMqWPIfApWREKetGFbm-fh3'])
