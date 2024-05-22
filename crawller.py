import pandas as pd
import os
import csv
import boto3

from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By


# aws key
load_dotenv()

AWS_REGION = os.environ.get('AWS_REGION')
AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
GIHU_TABLE = os.environ.get('GIHU_TABLE')

# load webdriver
driver = webdriver.Chrome()
url = 'https://func.seoul.go.kr/climateCard/rangeList.do'
table_data = []
items = []

# make table
for i in range(1, 36):
    driver.get(url)
    driver.implicitly_wait(1)

    driver.execute_script('fnPagingMove(' + str(i) + ')')

    # load table
    tables = driver.find_element(By.CLASS_NAME, 'pop_tableList_row')

    rows = tables.find_elements(By.TAG_NAME, 'tr')

    flag = False
    for row in rows:
        # skip th
        if not flag:
            flag = True
        else:
            cell_data = [cell.text for cell in row.find_elements(By.TAG_NAME, 'td')]
            table_data.append(cell_data)

# driver quit
driver.quit()


# initialize db
db = boto3.resource(
    'dynamodb',
    region_name=AWS_REGION,
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY
)

# gihu_table = db.create_table(
#     TableName=GIHU_TABLE,
#     KeySchema=[
#         {   
#             'AttributeName': 'name',
#             'KeyType': 'HASH'
#         },
#         {
#             'AttributeName': 'index',
#             'KeyType': 'RANGE'
#         }
#     ],
#     AttributeDefinitions=[
#         {
#             'AttributeName': 'name',
#             'AttributeType': 'S'
#         },
#         {
#             'AttributeName': 'index',
#             'AttributeType': 'N'
#         }
#     ],
#     ProvisionedThroughput={
#         'ReadCapacityUnits': 10,
#         'WriteCapacityUnits': 10
#     }
# )

gihu_table = db.Table(GIHU_TABLE)

for row in table_data:    
    gihu_table.put_item(
        Item = {
            'index' : int(row[0]),
            'name' : row[1],
            'line' : row[2],
            'riding' : True if row[3] == 'O' else False,
            'quit' : True if row[4] == 'O' else False,
            'sell' : True if row[5] == 'O' else False,
            'charge' : True if row[6] == 'O' else False,
            'suspense' : True if row[7] == 'O' else False
        }
    )
