# 실시간 데이터를 오픈 API 통해서 받기 위해 호출)  

import os, json, requests
import threading, time

# API 키는 .env에서 읽어오기
YOUTH_API_KEY = os.getenv("ONTONG_API_KEY")
GOV_API_KEY = os.getenv("GOV_API_KEY")

# 온통청년 API 호출
def get_youth_service_list(youth_api_key):
    url = "https://www.youthcenter.go.kr/go/ythip/getPlcy"
    all_data = []
    page = 1
    page_size = 100

    while True:
        params = {
            "apiKeyNm": youth_api_key,
            "pageNum": page,
            "pageSize": page_size,
            "rtnType": "json"
        }
        response = requests.get(url, params=params)
        result = response.json()
        data = result.get("result", {}).get("youthPolicyList", [])
        if not data:
            break
        all_data.extend(data)
        if len(data) < page_size:
            break
        page += 1

    return {"result": {"youthPolicyList": all_data}}  # seed_db.py 형식에 맞게 진행

# 정부24 API 호출
def get_gov24_service_list(gov_api_key, keyword="청년"):
    url = "https://api.odcloud.kr/api/gov24/v3/serviceList"
    all_data = []
    page = 1
    per_page = 100

    while True:
        params = {
            "serviceKey": gov_api_key,
            "page": page,
            "perPage": per_page,
            "cond[지원대상::LIKE]": keyword
        }
        response = requests.get(url, params=params)
        result = response.json()
        data = result.get('data', [])
        if not data:
            break
        all_data.extend(data)
        if len(data) < per_page:
            break
        page += 1

    return {"data": all_data}