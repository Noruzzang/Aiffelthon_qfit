import os
import glob
import subprocess
import logging
import shutil
from datetime import datetime
import re
import json


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

home_dir = os.path.expanduser("~")  # 홈 디렉토리 가져오기

#-------------------------------------------------------#
# 앱에서 찍어서 보낸 이미지가 upload폴더에 있는지 체크
#-------------------------------------------------------#
def upload_file_check():
    folder_path = os.path.join(home_dir, "aiffelthon_qfit", "model_src", "upload_image")  #앱에서 제공한 이미지 파일위치
    logger.info(f"홈 디렉토리: {home_dir}")
    logger.info(f"폴더 경로: {folder_path}")
 
    # 폴더 내 파일 존재 여부 확인 (이미지 확장자: jpg, png, bmp 등)
    extensions = ["jpg", "jpeg", "png", "bmp", "gif"]        
    image_files = [f for ext in extensions for f in glob.glob(os.path.join(folder_path, f"*.{ext}"))] #여러건의 파일이 존재(full path)
    
    if not image_files:  # 파일이 없는 경우
        raise FileNotFoundError("이미지 파일이 해당폴더에 존재하지 않습니다.")

    logger.info(f"확인된 파일 {len(image_files)}개: {image_files}")
    
    logger.info(f"==== [ upload폴더내 이미지 파일 존재여부 체크완료 ] ====")
    
    return image_files

#----------------------------------------------------------------------------------#
# upload_image 폴더내 해당파일만 ---> final_image 폴더로 이동
# 파일명은 기존파일명_년월일시분초.확장자 형태로 수정함
# 폴더내 파일이 존재하는지 체크해야 하므로, 작업완료된 파일은 이동(move)하여 폴더를 비운다.
#----------------------------------------------------------------------------------#
def upload_image_move(source_folder, dest_folder, src_fullname, current_time, idx):
    source_path = None
    dest_path = None
    old_path = None
    file_name = None
    
    # 절대 경로로 대상 폴더 설정
    source_path = os.path.join(home_dir, "aiffelthon_qfit", "model_src", source_folder)  # upload_image폴더
    dest_path = os.path.join(home_dir, "aiffelthon_qfit", "model_src", dest_folder)      # final_image폴더    
        
    # 대상 폴더가 존재하지 않으면 생성
    if not os.path.exists(dest_path):
        os.makedirs(dest_path)   

    # 현재 시간 추가
    #current_time = datetime.now().strftime('%Y%m%d%H%M%S')

    # 기존 파일 경로 및 새 파일명 생성
    old_path = src_fullname
    
    # 파일 이름만 추출
    file_name = os.path.basename(src_fullname)
    
    name, ext = os.path.splitext(file_name)
    #new_filename = f"{name}_{current_time}{ext}"
    new_filename = f"{current_time}_{idx}_{name}{ext}"
    new_path = os.path.join(dest_path, new_filename)

    # 파일 이동
    shutil.move(old_path, new_path)
    logger.info(f"==== 파일 이동 완료: {old_path} -> {new_path}")


#----------------------------------------------------------------------------------#
# result_image 폴더내 모든파일 ---> final_image 폴더로 이동
# 파일명은 기존파일명_년월일시분초.확장자 형태로 수정함
# topview 및 경로검출시 생성한 파일명이 동일하여, 덮어 써는것을 방지하기 위하여 이동해줌
#----------------------------------------------------------------------------------#
def result_image_image_move(source_folder, dest_folder, current_time, idx):
    
    source_path = None
    dest_path = None
    
    # 절대 경로로 대상 폴더 설정
    source_path = os.path.join(home_dir, "aiffelthon_qfit", "model_src", source_folder)  #2개의 폴더가 존재
    dest_path = os.path.join(home_dir, "aiffelthon_qfit", "model_src", dest_folder) #final_image 폴더    
        
    # 대상 폴더가 존재하지 않으면 생성
    if not os.path.exists(dest_path):
        os.makedirs(dest_path)   

    # 각 소스 폴더의 파일 처리
    filename = []
    for filename in os.listdir(source_path):
        
        # 대상파일 종류
        if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp', 'txt')):
            # 현재 시간 추가
            #current_time = datetime.now().strftime('%Y%m%d%H%M%S')

            # 기존 파일 경로 및 새 파일명 생성
            old_path = os.path.join(source_path, filename)
            name, ext = os.path.splitext(filename)
            #new_filename = f"{name}_{current_time}{ext}"
            new_filename = f"{current_time}_{idx}_{name}{ext}"
            new_path = os.path.join(dest_path, new_filename)

            # 파일 이동
            shutil.move(old_path, new_path)
            logger.info(f"==== 파일 이동 완료: {old_path} -> {new_path}")


#----------------------------------------------------------------------------#   
# 파일 이름에서 current_time, idx, name, ext 정보를 추출
#----------------------------------------------------------------------------#
def parse_file_info(file_name):
    pattern = r"(\d{14})_(\d+)_(.*?)\.(\w+)"  # new파일의 형식 => f"{current_time}_{idx}_{name}{ext}"
    match = re.match(pattern, file_name)
    
    if match:
        return match.groups()  # (current_time, idx, name, ext)
    return None


#----------------------------------------------------------------------------#
# final_image 폴더에서 파일 이름을 읽어 그룹화된 데이터를 생성하는 함수
#----------------------------------------------------------------------------#
def generate_data_from_folder(dest_folder):    
    
    # 절대 경로로 대상 폴더 설정
    dest_path = os.path.join(home_dir, "aiffelthon_qfit", "model_src", dest_folder)  #final_image 폴더
            
    if not os.path.isdir(dest_path):
        raise ValueError(f"폴더 경로가 유효하지 않습니다: {dest_path}")
    
    # 제외해야 할 이름 정의(해당파일 2개는 제외, 대상파일(3개)=best_shot, front_view, xxx.jpg)
    excluded_names = ["ball_labels", "table_with_balls"]

    # 폴더 내 파일 목록 읽기 및 정렬
    files = sorted(os.listdir(dest_path))
    #logger.info(f"files: {files}")
       
    # 파일 정보 파싱 및 필터링
    file_info = []
    for file_name in files:
        parsed = parse_file_info(file_name) #파일이름에서 current_time, idx, name, ext 정보를 추출       
        
        #파일이름 구조: {current_time}_{idx}_{name}.{ext} => 20250126182140_0_K_04.jpg
        if parsed and not any(excluded in parsed[2] for excluded in excluded_names):
            file_info.append({
                "file_name": file_name,      #파일이름
                "current_time": parsed[0],   #현재시간일시
                "idx": parsed[1],            #파일순번
                "name": parsed[2],           #파일이름
                "ext": parsed[3],            #확장자
                "full_path": os.path.join(dest_path, file_name) #파일전체경로
            })
            
            #logger.info(f"file_info: {file_info}")
    
    # current_time과 idx로 그룹화
    grouped_data = {}
    group_key = []
    
    for info in file_info:
        group_key = f"{info['current_time']}_{info['idx']}"  #이부분이 실제 1개 row정보단위
        if group_key not in grouped_data: #동일한 데이타의 중복등록을 제한하기 위하여
            #그룹데이타의 초기화
            grouped_data[group_key] = {
                "index": info["idx"],
                #"upload_image": [],
                "upload_image": None,
                "best_shot": None,
                "front_view": None
            }
            
        # 파일 종류에 따라 필드 설정
        if "best_shot" in info["name"]:
            grouped_data[group_key]["best_shot"] = info["full_path"]
        elif "front_view" in info["name"]:
            grouped_data[group_key]["front_view"] = info["full_path"]
        else:
            #grouped_data[group_key]["upload_image"].append(info["full_path"])
            grouped_data[group_key]["upload_image"] = info["full_path"]
    
    # 데이터 리스트 생성
    data_list = []
    for group_key, group_value in grouped_data.items():
        #group_value["upload_image"] = group_value["upload_image"][0] if group_value["upload_image"] else None
        group_value["upload_image"] = group_value["upload_image"] if group_value["upload_image"] else None
        data_list.append(group_value)
    
    return data_list

#----------------------------------------------------------------------------#
#데이터를 JSON 파일로 저장하는 함수
#----------------------------------------------------------------------------#
def save_json_to_folder(data, dest_folder, current_time):
        
    dest_path = os.path.join(home_dir, "aiffelthon_qfit", "model_src", dest_folder)  #final_image 폴더    
    
    if not os.path.isdir(dest_path):
        os.makedirs(dest_path)
    
    # 파일 이름: 현재 시간 기반
    current_time_json = datetime.now().strftime("%Y%m%d%H%M%S")
    json_file_path = os.path.join(dest_path, f"{current_time}_result_{current_time_json}.json")

    # JSON 파일 저장
    with open(json_file_path, "w", encoding="utf-8") as json_file:
        json.dump(data, json_file, ensure_ascii=False, indent=4)
    
    return json_file_path


#----------------------------------------------------------------------------#
# upload_image 폴더에 파일이 존재하는지 체크, 
# 파일이 존재시 topview변환, 경로검출처리를 수행후 최종이미지 생성
#----------------------------------------------------------------------------#
def check_files_and_execute():
    try:
        result = upload_file_check() #upload폴더 파일존재여부 체크(full path형태로 반환)
        logger.info(f"result : {result}")
        
        # 현재 시간 추가
        current_time = datetime.now().strftime('%Y%m%d%H%M%S')
                            
        for index, image_filename in enumerate(result):         
            logger.info(f"==== index:{index}, 이미지파일명: {image_filename}")
            
            #------------------------------------------------#
            # 파일이 있는 경우 topview.py 스크립트 실행
            #------------------------------------------------#
            topview_file = os.path.join(home_dir, "aiffelthon_qfit", "model_src", "topview.py")    #앱이미지 존재시 실행할 탑뷰처리하는 파일명
            logger.info(f"파이썬 파일 경로: {topview_file}")
            
            logger.info(f"==== [ topview.py 스크립트 실행 ] ====")               
            top_result = subprocess.run(["python", topview_file, image_filename], check=True, capture_output=True, text=True)
            logger.info(f"top_result: {top_result}")
        
            logger.info(f"==== [ TopView 이미지로 변환작업 완료 ] ====")
            
            #------------------------------------------------------#
            # 성공한 경우 당구경로검출 pymunk_sim6.py 스크립트 실행
            #------------------------------------------------------#
            qfit_simulation_v1_file = os.path.join(home_dir, "aiffelthon_qfit", "model_src", "qfit_simulation_v1.py")            

            logger.info(f"==== [ qfit_simulation_v1.py 스크립트 실행 ] ====")
            sim_v1_result = subprocess.run(["python", qfit_simulation_v1_file], check=True)
            logger.info(f"pym_result: {sim_v1_result}")
            
            logger.info(f"==== [ 당구공 경로검출 작업 완료 ]  ====")
                            
            #-----------------------------------------------------------------------------#
            # upload_image 폴더내 image_filename 파일만 -> final_image 폴더로 이동(한개파일)
            #-----------------------------------------------------------------------------#
            src_folder = "upload_image" # 원본 폴더 목록
            dest_folder = "final_image" # 이동할 폴더
            
            logger.info(f"==== [ upload_image 폴더내 파일 이동 작업 시작 ]  ====")
            upload_image_move(src_folder, dest_folder, image_filename, current_time, index)
            logger.info(f"==== upload_image 폴더의 [{image_filename}] -> final_image 폴더로 이동완료(move)")                  
            
            #-----------------------------------------------------------------------------#
            # result_image 폴더내 모든파일 -> final_image 폴더로 이동 (여러건 파일존재)
            #-----------------------------------------------------------------------------#
            src_folder = "result_image" # 원본 폴더 목록
            dest_folder = "final_image"  # 이동할 폴더
            
            logger.info(f"==== [ result_image 폴더내 모든파일 이동 작업 시작 ]  ====")
            result_image_image_move(src_folder, dest_folder, current_time, index)
            logger.info(f"==== result_image 폴더내 모든파일 -> final_image 폴더로 이동완료(move)")
            

        logger.info(f"==== [ topview 및 당구경로 검출작업 완료 ]  ====")
        
        #--------------------------------------------------------------------------------#
        # upload_image 폴더에 있는 이미지 파일건수 기준으로
        # 건수만큼 loop돌면서 final_image 폴더내 파일을 우선 sort하고
        # 각 파일의 _idx_ 기준으로 파일의 정보를 찾아서 각 파일을 구성한다.
        # json형태로 자료를 저장하고 저장된 이미지건에 맞게 정보를 넘긴다.
        #--------------------------------------------------------------------------------#
        logger.info(f"==== [ JSON 파일 생성시작  ]  ====")
               
        data = generate_data_from_folder("final_image")
        logger.info(f"data: {data}")
        
        # JSON 파일로 저장
        json_path = save_json_to_folder(data, "final_image", current_time)
        
        # 결과 로그
        logger.info(f"===== [ JSON 파일 저장 완료: {json_path} ] ====")
        
        # 결과 반환
        #return {
        #    "statusCode": "200",
        #    "data": data
        #}
        return {"statusCode": "200", "message": "파일 업로드 및 당구경로검출 처리완료", "json_file": json_path, "data": data}
    except FileNotFoundError as e:
        logger.error(f"{e}")
        return {"statusCode": "error", "message": "No image files found in the folder."}
    except subprocess.CalledProcessError as e:
        logger.error(f"스크립트 실행 중 오류 발생: {e}")
        return {"statusCode": "error", "message": f"Script execution error: {str(e)}"}
    except Exception as e:
        logger.error(f"알 수 없는 오류 발생: {e}")
        return {"statusCode": "error", "message": f"Unexpected error: {str(e)}"}