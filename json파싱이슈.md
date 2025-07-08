## ⚠️ 한국전력공사(KEPCO) API JSON 파싱 이슈

### ❗ 문제 상황
한국전력공사(OpenAPI)에서 전력 사용량 데이터를 `returnType=json` 형식으로 요청한 경우,  
응답이 표준 JSON이 아닌 **두 개의 JSON 객체가 붙어 있는 형태**로 반환되었습니다:

```json
{"totData":[...]}{"data":[...]}
'''
이로 인해 json.loads() 실행 시 아래와 같은 에러가 발생했습니다:

json.decoder.JSONDecodeError: Extra data: line 1 column XXX

✅ 해결 방법
response.text를 '}{' 기준으로 나누고, 각각 따로 json.loads()로 파싱했습니다:

python
복사
편집
raw_text = response.text.strip()
json_1, json_2 = raw_text.split('}{', 1)
json_1 += '}'
json_2 = '{' + json_2

tot_data = json.loads(json_1).get("totData", [])
detail_data = json.loads(json_2).get("data", [])
이 방식으로 정상적으로 데이터를 구조화하고 pandas DataFrame에 저장할 수 있었습니다.
