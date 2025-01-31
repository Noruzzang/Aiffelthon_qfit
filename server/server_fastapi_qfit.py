import uvicorn   # pip install uvicorn 
from fastapi import FastAPI, HTTPException   # pip install fastapi 
from fastapi.middleware.cors import CORSMiddleware
import upload_image_check
import logging

# Create the FastAPI application
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

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

#------------------------------------------------------------#
# 웹페이지가 정상적으로 구동되는지 체크 하는 API
#------------------------------------------------------------#
@app.get("/", summary="당구검출 테스트 API", description="웹페이지가 정상적으로 구동되는지 체크 하는 API")
async def read_root():
    logger.info("Root URL was requested")
    return "당구검출 API 테스트 페이지입니다"
       
           
#------------------------------------------------------------#
# 앱에서 찍은 이미지를 upload_image 폴더에 두면, 
# 그 파일을 읽어서 topview화면의 이미지와 좌표로 생성한다.
#------------------------------------------------------------#
@app.get("/upload", summary="당구공기준 당구경로예측 API", description="앱에서 찍은 이미지 사진을 기준으로 탑뷰화면 및 당구공의 경로를 예측후 이미지로 제공하는는 API")
async def upload_image_read():
    try:
        result = upload_image_check.check_files_and_execute()
        logger.info(f"result: {result}")
        
        if result.get('status') == 'success': 
            logger.info("탑뷰 이미지에 당구경로 추가한 최종이미지 생성완료")
        return result
    
    except Exception as e:
        logger.error("이미지파일이 없거나 탑뷰 및 경로예측시 에러 발생: %s", e)
        raise HTTPException(status_code=500, detail=f"Error details: {e}")


#------------------------------------------------------------#
# Run the server
#------------------------------------------------------------#
if __name__ == "__main__":
    uvicorn.run("server_fastapi_qfit:app",
            reload= True,   # Reload the server when code changes
            host="127.0.0.1",   # Listen on localhost 
            port=5000,   # Listen on port 5000 
            log_level="info"   # Log level
            )