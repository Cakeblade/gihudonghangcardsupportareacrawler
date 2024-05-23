# GihudonghangcardSupportAreaCrawler

### 동기
왜 기후동행카드는 쓰잘데기 없이 지역 제한을 걸어두었는가? 그 이유는 아무도 모르지 않다...  
  
### 설명
https://news.seoul.go.kr/traffic/climatecard-service 사이트를 크롤링해 DynamoDB에 저장하는 프로그램

### 사용 방법
- **(주의) OS와 chrome 버전에 맞는 webdriver가 같은 폴더에 있어야 함**
- ubuntu 22.04기준 venv 사용시
```
python -m venv [환경이름]

source ./[환경이름]/bin/activate

pip install -r requirements.txt

python crawller.py
```
- conda 사용시
```
conda create -n [환경이름] python=[python 버전] # python 버전은 3.10 이상을 권장

conda activate [환경이름]

pip install -r requirements.txt

python crawller.py
```

### 사용 package
- python-dotenv  
- selenium  
- boto3  

### LICENSE
LICENSE 참조
