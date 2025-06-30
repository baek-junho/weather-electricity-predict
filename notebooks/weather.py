from http.client import responses
import os
import pandas as pd
import numpy as np
import requests
from datetime import datetime
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm

# 윈도우 기본 한글 폰트 설정
plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False  # 음수 깨짐 방지

os.makedirs("data/raw", exist_ok=True)

def get_weather(api_key, base_date, base_time, nx=55, ny=124):
    url = "http://apis.data.go.kr/1360000/VilageFcstInfoService_2.0/getVilageFcst"
    params = {
        'serviceKey': api_key,
        'numOfRows': '1000',
        'pageNo': '1',
        'dataType': 'JSON',
        'base_date': base_date,  # 'YYYYMMDD'
        'base_time': base_time,  # '0500', '0800' 등 3시간 단위
        'nx': nx,  # 지역 X좌표 (서울: 60)
        'ny': ny,  # 지역 Y좌표 (서울: 127)
    }
    response = requests.get(url, params=params)
    items = response.json()['response']['body']['items']['item']
    df = pd.DataFrame(items)
    return df

if __name__ == "__main__":
    api_key = "FFQ3qS+8EfiOz0e8oCxBh3EXfR/SFLqU4wfYmnVCdNbEV1STR6grUYKyoTc8WWRvgYk+BY4F6HNuK+1gMuFT8A=="
    today = datetime.now().strftime('%Y%m%d')
    df = get_weather(api_key, today, "0500")
    df.to_csv("weather-electricity-predict/data/raw/weather_sample.csv", index=False)


### 카테고리별로 피벗테이블 만들기
pivot = df.pivot_table(
    index=["fcstDate", "fcstTime"],
    columns="category",
    values="fcstValue",
    aggfunc="first").reset_index()

pivot.head()

### 타입변환 + 시간 컬럼 만들기

pivot['datetime'] = pd.to_datetime(pivot['fcstDate'] + pivot['fcstTime'], format='%Y%m%d%H%M')
pivot = pivot.sort_values('datetime')

#숫자형 컬럼으로 변환
for col in pivot.columns[2:-1]: #TNP, POP등
    pivot[col] = pd.to_numeric(pivot[col], errors='coerce')

## 간단한 시각화

plt.figure(figsize=[10,5])
plt.plot(pivot['datetime'], pivot['TMP'], label="기온 (C)")
plt.plot(pivot["datetime"], pivot["POP"], label="강수확률 (%)")
plt.xticks(rotation=45)
plt.legend()
plt.title("시간대별 기온과 강수확률")
plt.tight_layout()
plt.show()