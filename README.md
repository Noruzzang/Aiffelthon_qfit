# Aiffelthon_qfit
아이펠톤 큐피트팀 레포지토리  
├── data/                     # 데이터 준비 및 전처리  
├── models/                   # 학습된 모델 저장   
├── app/                      # 모바일 앱 소스코드  
├── scripts/                  # 데이터 전처리 및 모델 학습 스크립트  
├── server/                   # AI 모델 서버  
└── README.md                 # 프로젝트 설명  




```bash
📂 프로젝트 디렉토리
│
├── 📂 model_src  (전처리 및 시뮬레이션 처리:사용자가 전송한 이미지 전처리 후 경로 검출)
│   ├── 📂 upload_image  (앱 카메라로 찍은 이미지 저장)
│   ├── 📂 image  (기본 이미지 참조)
│   ├── 📂 result_image  (탑뷰 및 당구공 경로 검출 이미지 저장)
│   │   ├── 📄 ball_labels.txt
│   │   ├── 📄 table_with_balls.png
│   ├── 📂 final_image  (작업 완료된 파일 이동 목록)
│   ├── 📄 topview.py  (📂 result_image에 탑뷰 및 공 위치 정보 저장)
│   ├── 📄 qfit_simulation_v0.0.1.py  (당구 앱 화면 표시용 3개 이미지 저장)
│
├── 📂 app  (모바일 앱 소스코드:components flutter UI 구성요서)
│   ├── 📄 load.dart  (앱 진입점)
│
├── 📂 server  (AI 모델 서버:앱 연동 및 Top-View, 시뮬레이션 처리)
    ├── 📄 server_fastapi_qfit.py  (탑뷰 및 당구 경로 검출 API 호출, FastAPI 기반)

```
