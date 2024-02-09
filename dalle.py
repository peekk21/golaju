import os
import json
import requests

def dalle(prompt, shot_name):
    # API KEY 가져오기
    OPENAI_API_KEY = "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"

    # API 엔드포인트(API에서 제공하는 서비스의 특정 부분) 요청
    api_url = 'https://api.openai.com/v1/images/generations'

    # 헤더 정의
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {OPENAI_API_KEY}'
    }

    # 요청 데이터 정의
    data = {
        "model": "dall-e-3",
        "prompt": prompt,
        "n": 1,
        "size": "1024x1024"
    }

    # API 요청 수행
    response = requests.post(api_url, headers=headers, data=json.dumps(data))

    # 응답처리
    if response.status_code == 200:
        result = response.json()
        print("Generated image URL:", result['data'][0]['url'])

        # 이미지 다운로드 요청
        image_response = requests.get(result['data'][0]['url'])

        # 다운로드 성공 여부 확인
        if image_response.status_code == 200:

            # 이미지를 저장 경로 설정
            path = 'static/myapp/shots/'+shot_name+'.jpg'
            with open(path, "wb") as file:
                file.write(image_response.content)
            print("이미지가 성공적으로 다운로드되었습니다.")

        else:
            print("이미지 다운로드 실패. HTTP Status Code:", image_response.status_code)

    else:
        print("Error:", response.status_code, response.text)