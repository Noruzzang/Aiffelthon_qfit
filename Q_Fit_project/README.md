
# Aiffelthon_qfit/Q_Fit_project/

📂 Q_Fit_project (프로젝트 디렉토리)   
    ├── 📂 model_src  (전처리 및 시뮬레이션 처리: 사용자가 전송한 이미지 전처리 후 경로 검출)   
    │    ├── 📂 upload_image  (앱 카메라로 찍은 이미지 저장)   
    │    │    ├── 📄 read.txt
    │    │
    │    ├── 📂 image  (기본 이미지 참조)    
    │    │    ├── 📄 Roboto-Regular.ttf   
    │    │    ├── 📄 frame.png   
    │    │    ├── 📄 hit_point.png   
    │    │    ├── 📄 red.png   
    │    │    ├── 📄 table-cloth.png   
    │    │    ├── 📄 white.png   
    │    │    ├── 📄 white_cue_ball.png   
    │    │    ├── 📄 yellow.png   
    │    │
    │    ├── 📂 result_image  (탑뷰 및 당구공 경로 검출 이미지 저장)     
    │    │    ├── 📄 ball_labels.txt     
    │    │    ├── 📄 table_with_balls.png     
    │    │
    │    ├── 📂 final_image  (작업 완료된 파일 이동 목록)     
    │    │    ├── 📄 read.txt
    │    │
    │    ├── 📄 topview.py  (📂 result_image에 탑뷰 및 공 위치 정보 저장)     
    │    ├── 📄 qfit_simulation_v0.0.1.py  (당구 앱 화면 표시용 3개 이미지 저장)     
    │
    ├── 📂 app  (모바일 앱 소스코드: components, Flutter UI 구성 요소)     
    │    ├── 📄 load.dart  (앱 진입점)    
    │    ├── 📄 main.dart   
    │    ├── 📄 select.dart   
    │    ├── 📄 result.dart   
    │    ├── 📄 pubspec.yaml   
    │
    ├── 📂 server  (AI 모델 서버: 앱 연동 및 Top-View, 시뮬레이션 처리)   
    │    ├── 📂 fastapi   
    │    │    ├── 📂 app   
    │    │    │    ├── 📄 server_fastapi_qfit.py (탑뷰 및 당구 경로 검출 API 호출, FastAPI 기반)   
    │    │    │    ├── 📄 upload_image_check.py   
    │    │    │
    │    │    ├── 📂 venv  
    │    │    │    ├── 📄 read.txt   
    │    │    │
    │    │    ├── 📄 requirements.txt     
    │
    ├── 📄 README.md          
          


# 📂 Q_Fit_project (프로젝트 디렉토리)  

## 📂 model_src  (전처리 및 시뮬레이션 처리: 사용자가 전송한 이미지 전처리 후 경로 검출)  
   
    ├── 📂 upload_image  (앱 카메라로 찍은 이미지 저장)  
        ├── 📄 read.txt  
 
    ├── 📂 image  (기본 이미지 참조)  
        ├── 📄 Roboto-Regular.ttf  
        ├── 📄 frame.png  
        ├── 📄 hit_point.png  
        ├── 📄 red.png  
        ├── 📄 table-cloth.png  
        ├── 📄 white.png  
        ├── 📄 white_cue_ball.png  
        ├── 📄 yellow.png  
   
    ├── 📂 result_image  (탑뷰 및 당구공 경로 검출 이미지 저장)  
        ├── 📄 ball_labels.txt  
        ├── 📄 table_with_balls.png  
  
    ├── 📂 final_image  (작업 완료된 파일 이동 목록)  
        ├── 📄 read.txt  
 
    ├── 📄 topview.py  (📂 result_image에 탑뷰 및 공 위치 정보 저장)  
    ├── 📄 qfit_simulation_v0.0.1.py  (당구 앱 화면 표시용 3개 이미지 저장)  


        
## 📂 app  (모바일 앱 소스코드: components, Flutter UI 구성 요소)  
 
    ├── 📄 load.dart  (앱 진입점)  
    ├── 📄 main.dart  
    ├── 📄 select.dart  
    ├── 📄 result.dart  
    ├── 📄 pubspec.yaml  


      
## 📂 server  (AI 모델 서버: 앱 연동 및 Top-View, 시뮬레이션 처리)  
 
    ├── 📂 fastapi  
        ├── 📂 app  
            ├── 📄 server_fastapi_qfit.py  (탑뷰 및 당구 경로 검출 API 호출, FastAPI 기반)  
            ├── 📄 upload_image_check.py  
       
        ├── 📂 venv  
            ├── 📄 read.txt  
        
        ├── 📄 requirements.txt  

## 📄 README.md  

          
