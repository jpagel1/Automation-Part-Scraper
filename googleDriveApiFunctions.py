"""Automatic Downloading and Uploading of AD Scrape Items"""

from pydrive.drive import GoogleDrive
from pydrive.auth import GoogleAuth
import datetime
from gsheets import Sheets

from Google import Create_Service
from googleapiclient.http import MediaFileUpload

def downloadADcsv():
    """Function to use Sheets API to download the latest google sheet as a csv"""
    
    try:
        sheets = Sheets.from_files('client_secrets.json','storage.json')
        s=sheets['1TEzt8rlrxj1ooXn1sGQ3LKgcezShuF8E5KmwEEAn4ts']
        csv_name = "AutomationItemsRequested.csv"
        s.to_csv(make_filename=csv_name)
        
        return True
    except:
        return False

def uploadUpdatedADcsv():
    """Save and Upload the AD CSV Unused"""

    #Authorize Gdrive APi
    gauth = GoogleAuth()
    gauth.LoadCredentialsFile("mycred.txt")

    #Kept requiring new auth, this way it uses the last credentials
    if gauth.credentials is None: 
        gauth.LocalWebserverAuth()
    elif gauth.access_token_expired:
        gauth.Refresh()
    else:
        gauth.Authorize()
    gauth.SaveCredentialsFile("mycred.txt")

    #Create Google Drive Obect
    drive = GoogleDrive(gauth)

    file_list = drive.ListFile({'q': "'root' in parents and trashed=false"}).GetList()
    #for file1 in file_list:
    #  print('title: %s, id: %s' % (file1['title'], file1['id']))

    for file in file_list:
        # Get the folder ID that you want - destination folder
        if file['title'] == 'Scraper':
            folderId = file['id']
            break
    #print(folderId)
    #Build String now that we got the ID
    str = "\'" + folderId + "\'" + " in parents and trashed=false"  

    #Define Base FileName
    baseFile = 'AutomationItems'
    
    file_list1 = drive.ListFile({'q': str}).GetList()
    for file1 in file_list1:
        if file1['title'] == 'Historical Data':
            folderIDHistorical = file1['id']
        if file1['title'] == baseFile:
            folderIDADCSV = file1['id']

    #print(folderIDADCSV)
    #print(folderIDHistorical)
    
    #Lets get a nice format
    d = datetime.datetime.now()
    formattedT = d.strftime('%Y_%m_%d')
    TodaysFile = formattedT +'_'+ baseFile
    
    #Upload Updated File for the day
    nowfile = drive.CreateFile({'title': "AutomationItemsUpdated", 'mimeType':'text/csv'})
    nowfile['parents'] = [{"kind": "drive#parentReference", "id": folderId}]
    nowfile.SetContentFile('AutomationItems.csv')
    nowfile.Upload()
    
    #lets Also upload a historical file
    historicalFile = drive.CreateFile({'title': TodaysFile, 'mimeType':'text/csv'})
    historicalFile['parents'] = [{"kind": "drive#parentReference", "id": folderIDHistorical}]
    historicalFile.SetContentFile('AutomationItems.csv')
    historicalFile.Upload()


def export_to_gsheet(file_name, parents):
    """This function exports the filename to the google drive parents location"""
    
    CLIENT_SECRET_FILE = "client_secrets.json"
    API_NAME = 'drive'
    API_VERSION = 'v3'
    SCOPES = ['https://www.googleapis.com/auth/drive']

    service = Create_Service(CLIENT_SECRET_FILE,API_NAME,API_VERSION,SCOPES)
    
    #Just name file the hours
    filenameFolderRemoval = file_name.replace('HistoricalData/','')
    filenameOtherRemoval = filenameFolderRemoval.replace('_AutomationItemsRequested','')
    
    #Eventually check if file exists first
    file_metadata = {
        'name' : filenameOtherRemoval.replace('.csv',''),
        'mimeType': 'application/vnd.google-apps.spreadsheet',
        'parents' : parents
    }
    
    media = MediaFileUpload(filename = file_name, mimetype ='text/csv')
    response = service.files().create(
        media_body = media,
        body = file_metadata
    ).execute()
    #print(response)