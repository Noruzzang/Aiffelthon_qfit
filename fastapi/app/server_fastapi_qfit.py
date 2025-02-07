import uvicorn   # pip install uvicorn 
from fastapi import FastAPI, HTTPException, File, UploadFile  # pip install fastapi
#from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from upload_image_check import check_files_and_execute
import logging
import os
from pathlib import Path
import shutil
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles


# FastAPI 애플리케이션 생성
app = FastAPI()


# CORS configuration
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 로그설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 홈 디렉토리 설정
home_dir = os.path.expanduser("~")
upload_folder = os.path.join(home_dir, "aiffelthon_qfit", "model_src", "upload_image")
final_folder = os.path.join(home_dir, "aiffelthon_qfit", "model_src", "final_image")

app.mount("/images", StaticFiles(directory=home_dir+"/aiffelthon_qfit/model_src/final_image"), name="images")

# 폴더 생성 (없다면)
os.makedirs(upload_folder, exist_ok=True)

#------------------------------------------------------------#
# 웹페이지가 정상적으로 구동되는지 체크 하는 API
#------------------------------------------------------------#
@app.get("/",
         summary="당구검출 테스트 API",
         description="웹페이지가 정상적으로 구동되는지 체크 하는 API")
async def read_root():
    logger.info("Root URL was requested")
    return "당구검출 API 테스트 페이지입니다"

#------------------------------------------------------------#
# 앱에서 찍은 이미지를 upload_image 폴더에 두면, 
# 1) 그 파일을 읽어서 topview화면의 이미지와 좌표로 생성한다.
# 2) 생성된 정보를 기준으로 물리시뮬레이션 처리후 당구경로검출
#    당점이미지 및 최종경로화면을 저장한다.
# 3) 4개파일 저장폴더 -> result_image
#      - ball_labels.txt, table_with_balls.png
#      - best_shot.png, front_view.png
# 4) 최종 5개파일 이동폴더 -> final_image
#      - K_02.jpg             -> 20250131190155_1_K_02.jpg
#      - ball_labels.txt      -> 20250131190155_1_ball_labels.txt
#      - table_with_balls.png -> 20250131190155_1_table_with_balls.png
#      - best_shot.png        -> 20250131190155_1_best_shot.png
#      - front_view.png       -> 20250131190155_1_front_view.png
#------------------------------------------------------------#
@app.post("/upload_image/",
          summary="당구공기준 당구경로예측 API",
          description="앱에서 찍은 이미지 사진을 기준으로 탑뷰화면 및 당구공의 경로를 예측후 이미지로 제공하는 API")
#async def upload_image(file: UploadFile = File(...)):
async def upload_image():
    try:
        logger.info(f"==== upload_image 호출 =====")
        
        # 저장할 파일 경로 설정
        #file_path = os.path.join(upload_folder, file.filename)

        # 파일 저장
        #with open(file_path, "wb") as buffer:
        #    shutil.copyfileobj(file.file, buffer)
            
        # 파일 저장
        #with open(file_path, "wb") as buffer:
        #    buffer.write(await file.read())
                        

        #logger.info(f"파일 업로드 완료: {file.filename}")       
         
        # 업로드 후 처리 실행        
        result = check_files_and_execute()
        logger.info(f"result: {result}")
        
        if result.get('statusCode') == '200':
            logger.info(f"==== 파일 업로드 및 당구경로검출 처리 최종완료! ====")
        return result
    
    except Exception as e:
        logger.error(f"파일 업로드 중 오류 발생: {str(e)}")
        raise HTTPException(status_code=500, detail=f"업로드 실패: {str(e)}")


#------------------------------------------------------------#
# 3개의 이미지 파일명의 URL정보를 제공하는 API
#------------------------------------------------------------#
@app.get("/image_info/{image_prefix}")
async def get_image_info(image_prefix: str):
    try:
        api_base_url = "https://84d3-112-172-64-10.ngrok-free.app"  # FastAPI 서버 주소
        logger.info(f"API 요청 도착: image_prefix={image_prefix}")

        image_names = [
            f"{image_prefix}_best_shot.png",
            f"{image_prefix}_front_view.png",
        ]

        image_urls = {}
        for img in image_names:
            image_path = os.path.join(final_folder, img)
            logger.info(f"확인할 이미지: {image_path}")

            if os.path.exists(image_path):
                key = '_'.join(img.split('_')[-2:]).split('.')[0]
                image_urls[key] = f"{api_base_url}/images/{img}"
                logger.info(f"추가된 이미지 URL: {key} -> {image_urls[key]}")

        if not image_urls:
            logger.error(f"이미지가 존재하지 않음.")
            raise HTTPException(status_code=404, detail="이미지를 찾을 수 없습니다.")
        
        return {"statusCode": "200", "image_urls": image_urls}
    except Exception as e:
        logger.error(f"오류 발생: {str(e)}")
        raise HTTPException(status_code=500, detail=f"이미지 URL 생성 실패: {str(e)}")



#------------------------------------------------------------#
# 개별 이미지 제공 API (파일 전송)
#------------------------------------------------------------#
@app.get("/images/{image_name}")
async def get_image(image_name: str):
    try:
        image_path = os.path.join(final_folder, image_name)
        
        if os.path.exists(image_path):
            return FileResponse(image_path, media_type="image/png")
    except Exception as e:
        logger.error(f"이미지 미존재: {str(e)}")
        raise HTTPException(status_code=404, detail=f"개별 이미지화면 호출실패: {str(e)}")



IMAGE_DIR = "/home/eunhaday/aiffelthon_qfit/model_src/final_image"
#-----------------------------------------
#-----------------------------------------
@app.get("/image/{image_name}")
async def get_image(image_name: str):
    """지정된 이미지 파일을 반환하는 API"""
    image_path = os.path.join(IMAGE_DIR, image_name)
    
    # 이미지 파일이 존재하는지 확인
    if not os.path.exists(image_path):
        return {"error": "Image not found"}
    
    # 이미지 파일을 응답으로 반환
    return FileResponse(image_path, media_type="image/png")  # PNG 외 JPG 등도 가능


#------------------------------------------------------------#
# 서버 실행
#------------------------------------------------------------#
if __name__ == "__main__":
    uvicorn.run("server_fastapi_qfit:app",
            reload= True,   # Reload the server when code changes
            host="127.0.0.1",   # Listen on localhost 
            port=8000,   # Listen on port 5000 
            log_level="info"   # Log level
            )