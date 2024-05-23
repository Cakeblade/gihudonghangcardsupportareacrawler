import os
import sys
import boto3

from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options


# table
load_dotenv()
GIHU_TABLE = os.environ.get('GIHU_TABLE')

# make webdriver options (ubuntu setting)
option = Options()
option.add_argument("--headless")
option.add_argument('--no-sandbox')
option.add_argument('--disable-dev-shm-usage')

# load webdriver
driver = webdriver.Chrome(options=option)
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

if len(table_data) > 0:
    print("Crawling Complete")
else:
    sys.exit()

# # initialize db
db = boto3.resource(
    'dynamodb'
)

db_table_name = [table.name for table in db.tables.all()]

if GIHU_TABLE not in db_table_name:
    gihu_table = db.create_table(
        TableName=GIHU_TABLE,
        KeySchema=[
            {   
                'AttributeName': 'name',
                'KeyType': 'HASH'
            },
            {
                'AttributeName': 'id',
                'KeyType': 'RANGE'
            }
        ],
        AttributeDefinitions=[
            {
                'AttributeName': 'name',
                'AttributeType': 'S'
            },
            {
                'AttributeName': 'id',
                'AttributeType': 'N'
            }
        ],
        ProvisionedThroughput={
            'ReadCapacityUnits': 10,
            'WriteCapacityUnits': 10
        }
    )

gihu_table = db.Table(GIHU_TABLE)

# insert data
for row in table_data:    
    gihu_table.put_item(
        Item = {
            'id' : int(row[0]),
            'name' : row[1],
            'line' : row[2],
            'riding' : True if row[3] == 'O' else False,
            'quit' : True if row[4] == 'O' else False,
            'sell' : True if row[5] == 'O' else False,
            'charge' : True if row[6] == 'O' else False,
            'suspense' : True if row[7] == 'O' else False
        }
    )
