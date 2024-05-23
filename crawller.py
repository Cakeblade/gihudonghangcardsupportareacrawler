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

# no need in ec2
# AWS_REGION = os.environ.get('AWS_REGION')
# AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
# AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')

# # initialize db
client = boto3.client(
    'dynamodb',
    # region_name=AWS_REGION,                         # no need in ec2
    # aws_access_key_id=AWS_ACCESS_KEY_ID,            # no need in ec2
    # aws_secret_access_key=AWS_SECRET_ACCESS_KEY     # no need in ec2
)
table_lists = client.list_tables()['TableNames']

if GIHU_TABLE not in table_lists:
    gihu_table = client.create_table(
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

waiter = client.get_waiter('table_exists')
waiter.wait(
    TableName=GIHU_TABLE,
    WaiterConfig={
        'Delay': 5,
        'MaxAttempts': 10
    }    
)

resource = boto3.resource(
    'dynamodb',
    # region_name=AWS_REGION,                         # no need in ec2
    # aws_access_key_id=AWS_ACCESS_KEY_ID,            # no need in ec2
    # aws_secret_access_key=AWS_SECRET_ACCESS_KEY     # no need in ec2
)

gihu_table = resource.Table(GIHU_TABLE)
gihu_table.put_item(
    Item={
        'name' : "test",
        'id' : 0
    }
)

# make webdriver options (ubuntu setting)
option = Options()
option.add_argument("--headless")
option.add_argument('--no-sandbox')
option.add_argument('--disable-dev-shm-usage')

# load webdriver
driver = webdriver.Chrome(options=option)

# subway
url = 'https://func.seoul.go.kr/climateCard/rangeList.do'
table_data = []
items = []

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

if len(table_data) > 0:
    print("Crawling Complete")
else:
    driver.quit()
    sys.exit()

# insert subway data
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

# bus
url = 'https://func.seoul.go.kr/climateCard/rangeList.do?gubun=2'
table_data = []
items = []

for i in range(1, 33):
    driver.get(url)
    driver.implicitly_wait(1)

    driver.execute_script('fnPagingMove(' + str(i) + ')')

    # load table
    tables = driver.find_elements(By.CLASS_NAME, 'pop_tableList_row')

    rows = tables[1].find_elements(By.TAG_NAME, 'tr')

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


# insert bus data
for row in table_data:    
    gihu_table.put_item(
        Item = {
            'id' : int(row[0]),
            'name' : row[1],
            'available' : True if row[2] == 'O' else False
        }
    )