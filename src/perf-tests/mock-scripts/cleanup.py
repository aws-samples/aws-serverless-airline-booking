import boto3
import csv
import os
import json
import time
from zipfile import ZipFile 

AWS_REGION = os.environ['AWS_REGION']
TOKEN_CSV = os.environ['FOLDERPATH'] + os.environ['TOKEN_CSV']
USER_CSV = os.environ['FOLDERPATH'] + os.environ['USER_CSV']
S3_BUCKET = os.environ['S3_BUCKET']
USER_POOL_ID = os.environ['USER_POOL_ID']
CLIENT_ID = os.environ['COGNITO_CLIENT_ID']
S3_BUCKET = os.environ['S3_BUCKET']
zipFileName = f'results-{int(time.time())}.zip' 

client = boto3.client('cognito-idp', region_name=AWS_REGION)
s3 = boto3.resource('s3')

def delete_cognito_users():

    with open(USER_CSV, mode='r') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        next(csv_reader, None)
        for row in csv_reader:
            response = client.admin_delete_user(
                UserPoolId= USER_POOL_ID,
                Username= row[0]
            )

def get_all_file_paths(directory): 
  
    # initializing empty file paths list 
    file_paths = [] 
  
    # crawling through directory and subdirectories 
    for root, directories, files in os.walk(directory): 
        for filename in files: 
            # join the two strings in order to form the full filepath. 
            filepath = os.path.join(root, filename) 
            file_paths.append(filepath) 
  
    # returning all file paths 
    return file_paths

def zip_files(filePath):
    file_paths = get_all_file_paths(filePath) 

    with ZipFile(zipFileName,'w') as zip: 
    # writing each file one by one 
        for file in file_paths: 
            zip.write(file) 

def download_reports(filePath):
    
    if not (os.path.exists(filePath)):
        os.makedirs("./results")    

    sync_command = f"aws s3 sync s3://{S3_BUCKET}/results {filePath}"
    os.system(sync_command)

    zip_files(filePath)

def upload_results_s3():
    print(zipFileName)  
    sync_command = f"aws s3 cp {zipFileName} s3://{S3_BUCKET}/"
    os.system(sync_command)

def delete_gatling_reports():
    sync_command = f"aws s3 rm s3://{S3_BUCKET}/results --recursive"
    os.system(sync_command)

def main():
    try:        
        ### delete users
        print("==begin: delete cognito users==")
        delete_cognito_users()
        print("==completed: delete cognito users==")
    
        ### copy the gatlin reports from S3 to local 
        print("==begin: download gatling reports==")
        download_reports("./results")
        print("==completed: download gatling reports==")

        ### upload zipped file to S3
        print("==begin: upload zipped reports to s3==")
        upload_results_s3()
        print("==begin: upload zipped reports to s3==")

        ### delete previous gatling reports
        print("==begin: deleting previous gatling reports==")
        delete_gatling_reports()
        print("==complete: deleting previous gatling reports==")


    except Exception as error:
        pass
        print(f'Error - {error}')

if __name__ == "__main__": 
    main()
