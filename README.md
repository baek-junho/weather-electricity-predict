# 📊 기상 데이터 기반 전력 소비량 예측 프로젝트

이 프로젝트는 기상청 및 전력공사 데이터를 활용하여 시간대별 전력 소비량을 예측하는 머신러닝 모델을 구축하고, Streamlit 기반 대시보드로 시각화하는 것을 목표로 합니다.

## 🔧 사용 기술
- Python (3.9 이상)
- Pandas / Numpy / Requests
- Matplotlib / Seaborn / Plotly
- XGBoost or Prophet
- Streamlit

## 📁 프로젝트 구조
```
weather-electricity-predict/
├── data/
│ ├── raw/
│ └── processed/
├── notebooks/
│ ├── 01_EDA.ipynb
│ ├── 02_Modeling.ipynb
│ └── 03_Dashboard.ipynb
├── app/
│ └── streamlit_app.py
├── README.md
└── requirements.txt
```


## ✅ 진행 계획
1. 공공데이터 Open API를 통해 날씨/전력 데이터를 수집
2. 전처리 및 시각화를 통해 데이터 통찰 도출
3. 머신러닝 모델을 활용한 전력소비 예측
4. Streamlit으로 결과 시각화 및 대시보드 제공

## 📌 데이터 출처
- 기상청 단기예보 API: [data.go.kr](https://www.data.go.kr/data/15084084/openapi.do)
- 한국전력공사 전력사용량: [data.go.kr](https://www.data.go.kr/data/15007122/openapi.do)
