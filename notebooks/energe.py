import requests
import json
import pandas as pd
import time

def fetch_monthly_power_data(year: int, month: int, api_key: str):
    url = "https://bigdata.kepco.co.kr/openapi/v1/powerUsage/contractType.do"

    params = {
        "year": str(year),
        "month": str(month).zfill(2),
        "cntrCd": "100",  # 주택용
        "apiKey": api_key,
        "returnType": "json"
        # metroCd와 cityCd는 생략하여 전체 데이터 요청
    }

    try:
        response = requests.get(url, params=params)
        response.encoding = 'utf-8'

        if response.status_code != 200:
            print(f"❌ 요청 실패: {response.status_code}")
            return []

        raw_text = response.text.strip()

        # JSON 객체가 2개 붙어 있을 경우 분리
        if '}{' in raw_text:
            json_1, json_2 = raw_text.split('}{', 1)
            json_1 = json_1 + '}'
            json_2 = '{' + json_2
        else:
            print(f"❌ 예상과 다른 응답 형식: {raw_text[:300]}")
            return []

        detail_data = json.loads(json_2).get("data", [])

        # 데이터 구조화
        rows = []
        for item in detail_data:
            rows.append({
                "yyyymm": f"{year}-{str(month).zfill(2)}",
                "metro": item.get("metro"),
                "city": item.get("city"),
                "custCnt": item.get("custCnt"),
                "powerUsage": item.get("powerUsage"),
                "bill": item.get("bill"),
                "unitCost": item.get("unitCost")
            })

        print(f"✅ {year}-{month:02d} 데이터 수집 완료 (건수: {len(rows)})")
        return rows

    except Exception as e:
        print(f"❌ 에러 발생: {year}-{month:02d} {e}")
        return []

# --- 실행 파트 ---
# ✅ API 키
api_key = "88dNSlK6CNcC6aZz64Rz9jY3H6Hzkqx03ZhoHkxp"

all_data = []
for y in range(2022, 2024):  # 예: 2022년~2023년
    for m in range(1, 13):
        data = fetch_monthly_power_data(y, m, api_key)
        all_data.extend(data)
        time.sleep(1)  # API 호출 간격

# pandas DataFrame으로 저장
df = pd.DataFrame(all_data)

# 부평구 데이터만 필터링 (선택)
df_bupyeong = df[df["city"] == "부평구"]

# 저장
df.to_csv("weather-electricity-predict/data/raw/power_usage_all.csv", index=False)
df_bupyeong.to_csv("weather-electricity-predict/data/raw/power_usage_bupyeong.csv", index=False)


