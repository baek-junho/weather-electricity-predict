from http.client import responses
import os
import pandas as pd
import numpy as np
import requests
import time
from datetime import datetime
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from tqdm import tqdm

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
        'base_date': base_date,
        'base_time': base_time,
        'nx': nx,
        'ny': ny,
    }
    try:
        response = requests.get(url, params=params, timeout=5)
        response.raise_for_status()
        items = response.json()['response']['body']['items']['item']
        df = pd.DataFrame(items)
        return df
    except Exception as e:
        print(f"❌ 에러 발생: {base_date} - {e}")
        return None

if __name__ == "__main__":
    api_key = "키 입력력"

    # 수집 기간: 2022-01-01 ~ 2025-06-30
    start_date = datetime.strptime("2022-01-01", "%Y-%m-%d")
    end_date = datetime.strptime("2025-06-30", "%Y-%m-%d")

    all_data = []

    for single_date in tqdm(pd.date_range(start=start_date, end=end_date)):
        base_date = single_date.strftime('%Y%m%d')
        df = get_weather(api_key, base_date, "0500", nx=55, ny=124)  # 부평 기준

        if df is not None:
            all_data.append(df)

        time.sleep(0.3)  # 요청 간 딜레이 (API rate 제한 방지용)

    # 모두 합치기
    if all_data:
        result_df = pd.concat(all_data, ignore_index=True)
        result_df.to_csv("weather-electricity-predict/data/raw/weather_all.csv", index=False)
        print("✅ 저장 완료: weather_all.csv")
    else:
        print("⚠️ 수집된 데이터가 없습니다.")


#
def get_weather(api_key, base_date, base_time, nx=55, ny=124):
    url = "http://apis.data.go.kr/1360000/VilageFcstInfoService_2.0/getVilageFcst"
    params = {
        'serviceKey': api_key,
        'numOfRows': '1000',
        'pageNo': '1',
        'dataType': 'JSON',
        'base_date': '20250709',  # 'YYYYMMDD'
        'base_time': '0500',  # '0500', '0800' 등 3시간 단위
        'nx': 55,  # 지역 X좌표 (서울: 60)
        'ny': 124,  # 지역 Y좌표 (서울: 127)
    }
    response = requests.get(url, params=params)
    items = response.json()['response']['body']['items']['item']
    df = pd.DataFrame(items)
    return df

if __name__ == "__main__":
    api_key = "키 입력력"
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


###### 데이터가 최근 3일치 밖에 없어서 재수집 #######



import os
from datetime import datetime, timedelta
import requests


# API Key 및 저장 경로 설정
API_KEY = "키 입력"  
SAVE_DIR = "weather-electricity-predict/data/raw/weather"  # 저장 경로
os.makedirs(SAVE_DIR, exist_ok=True)

# 날짜 범위 설정 (예: 2022-01-01 ~ 2022-12-31)
start_date = datetime.strptime("20230101", "%Y%m%d")
end_date = datetime.strptime("20250701", "%Y%m%d")


def download_weather_file(date_str, stn=112):
    url = f"https://apihub.kma.go.kr/api/typ01/url/kma_sfcdd.php"
    params = {
        "tm": date_str,         # 날짜 (YYYYMMDD)
        "stn": str(stn),        # 지점 코드 (예: 112 = 인천)
        "authKey": API_KEY
    }

    response = requests.get(url, params=params)

    if response.status_code == 200 and "#START7777" in response.text:
        filename = f"{SAVE_DIR}/{date_str}.txt"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(response.text)
        print(f"✅ {date_str} 저장 완료")
    else:
        print(f"❌ {date_str} - 데이터 없음 또는 응답 오류")

curr_date = start_date
while curr_date <= end_date:
    date_str = curr_date.strftime("%Y%m%d")
    download_weather_file(date_str, stn=112)  # 인천: 112번
    curr_date += timedelta(days=1)

import pandas as pd
import os


def parse_weather_txt(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    data_lines = [line for line in lines if not line.startswith('#') and line.strip() != '']

    if not data_lines:
        print(f"❌ 데이터 없음: {file_path}")
        return None

    cols = [
        "date", "stn", "ws_avg", "ws_day", "ws_max", "ws_tm1", "ws_max2", "ws_tm2", "ws_max3", "ws_tm3",
        "ta_avg", "ta_max", "ta_tm1", "ta_min", "ta_tm2",
        "td_avg", "ts_avg", "tg_min",
        "hm_avg", "hm_min", "hm_tm",
    ]

    values = data_lines[0].strip().split(',')
    if len(values) < len(cols):
        print(f"⚠️ 열 개수 부족: {file_path}")
        return None

    df = pd.DataFrame([values[:len(cols)]], columns=cols)
    return df


def parse_all_weather_files(directory):
    all_data = []

    for file in os.listdir(directory):
        if file.endswith(".txt"):
            file_path = os.path.join(directory, file)
            df = parse_weather_txt(file_path)
            if df is not None:
                all_data.append(df)

    if not all_data:
        print("📭 읽을 수 있는 데이터가 없습니다.")
        return pd.DataFrame()

    merged_df = pd.concat(all_data, ignore_index=True)

    # 날짜 정리
    merged_df["date"] = pd.to_datetime(merged_df["date"], format="%Y%m%d")
    merged_df["yyyymm"] = merged_df["date"].dt.strftime("%Y-%m")

    # 필요한 컬럼 숫자형 변환
    cols_to_float = ["ta_avg", "ta_min", "ta_max", "hm_avg"]
    for col in cols_to_float:
        merged_df[col] = pd.to_numeric(merged_df[col], errors="coerce")

    return merged_df


# 실행
if __name__ == "__main__":
    data_dir = "weather-electricity-predict/data/raw/weather"  # 여기에 txt 파일 모아놓은 폴더
    df_all = parse_all_weather_files(data_dir)

    # 월별 평균값으로 집계
    df_monthly = df_all.groupby("yyyymm")[["ta_avg", "ta_min", "ta_max", "hm_avg"]].mean().reset_index()

    # 저장
    df_monthly.to_csv("weather-electricity-predict/data/processed/weather_monthly.csv", index=False)
    print("✅ 월별 기상 데이터 저장 완료")

