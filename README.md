# DE-1st-Project 텍스트 마이닝

## 프로젝트 목표
- 텍스트 마이닝을 통해 개발자 채용 공고의 키워드를 추출하고, 이를 통해 채용 공고의 특징을 파악합니다.
- FastAPI를 통해 API 서버를 구축하고, 이를 통해 데이터를 제공합니다.

## Project 환경
- Python 3.10.12 (venv)

## Project 구조
```
.
├── README.md
├── crawler.ipynb
├── simple_fastapi_server.py
└── requirements.txt
```

## Pre-requisite (사전 준비)
1. Python 3.10.12 설치 (venv 사용 권장)
```bash
# venv 생성
python -m venv ./
# venv 활성화
source ./bin/activate
```
2. ``requirements.txt`` 를 통해 필요한 라이브러리 설치
```bash
pip install -r requirements.txt
```
3. crawler.ipynb 실행
4. simple_fastapi_server.py 실행

## 실행 방법
### 1. crawler.ipynb 실행
각 셀을 실행하여 데이터를 수집합니다.
수집된 데이터는 pickle 파일로 저장되고 이후 DB에 저장됩니다.
### 2. simple_fastapi_server.py 실행
```bash 
# simple_fastapi_server.py가 있는 디렉토리에서
uvicorn simple_fastapi_server:app --host 0.0.0.0 --port 8023 --reload
# 현재 PC의 IP주소와 8023번 포트로 서버를 실행합니다.
```
를 통해 서버를 실행하고, 브라우저에서 ``http://localhost:8023/docs`` 에 접속하여 API를 확인할 수 있습니다.

> **알림**  
> 위 방법으로는 로컬 환경에서만 접속이 가능하므로 외부에서 접속하려면 외부 공유기, 클라우드 네트워크 설정 등에서 인바운드 포트를 열어주어야 합니다.