import os
import sys
import glob
import numpy as np
import cv2
import matplotlib.pyplot as plt
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 설정 값
WIDTH = 840  # 출력될 테이블 이미지의 너비
HEIGHT = 420  # 출력될 테이블 이미지의 높이
TABLE_WIDTH_MM = 800  # 테이블의 실제 너비 (mm)
TABLE_HEIGHT_MM = 400  # 테이블의 실제 높이 (mm)

# 색깔별 HSV 범위
color_ranges = {
    "red": ((0, 120, 70), (10, 255, 255)),
    "yellow": ((20, 100, 100), (30, 255, 255)),
    "white": ((0, 0, 180), (180, 80, 255)),
}

# 공 이미지 경로
ball_images = {
    "red": "/home/eunhaday/aiffelthon_qfit/model_src/image/red.png",
    "yellow": "/home/eunhaday/aiffelthon_qfit/model_src/image/yellow.png",
    "white": "/home/eunhaday/aiffelthon_qfit/model_src/image/white.png"
}

#result_success = 0  #해당 기능이 정상적으로 수행시 리턴결과 값은 성공으로 판단하기 위한 변수값

def find_corners(src, debug=False):
    """
    이미지에서 테이블의 모서리를 찾습니다.

    Args:
        src (np.ndarray): 입력 이미지.
        debug (bool): 디버그 모드 여부.

    Returns:
        np.ndarray: 모서리 좌표 배열.
    """
    src_hsv = cv2.cvtColor(src, cv2.COLOR_BGR2HSV)  # HSV 색 공간으로 변환

    # 파란색과 녹색 범위에 대한 마스크 생성
    table_img_blue = cv2.inRange(src_hsv, (100, 100, 100), (120, 255, 255))
    table_img_green = cv2.inRange(src_hsv, (40, 40, 40), (90, 255, 255))
    table_img = cv2.bitwise_or(table_img_blue, table_img_green)  # 마스크 합치기

    # 모폴로지 연산 (닫기)
    k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
    table_img_closing = cv2.morphologyEx(table_img, cv2.MORPH_CLOSE, k)

    # 외곽선 찾기
    contours, _ = cv2.findContours(table_img_closing, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if not contours:
        print("컨투어를 찾을 수 없습니다!")
        return None

    contour = max(contours, key=lambda x: cv2.contourArea(x))  # 가장 큰 컨투어 선택

    # 다각형 근사화
    epsilon = 0.02 * cv2.arcLength(contour, True)
    approx = cv2.approxPolyDP(contour, epsilon, True)

    if len(approx) != 4:
        print('테이블 인식 실패! 충분한 점을 찾을 수 없습니다.')
        return None

    return approx  # 모서리 좌표 반환


def get_warped_table(src, approx):
    """
    원근 변환을 적용하여 테이블 이미지를 워프합니다.

    Args:
        src (np.ndarray): 입력 이미지.
        approx (np.ndarray): 모서리 좌표 배열.

    Returns:
        np.ndarray: 워프된 테이블 이미지.
    """
    if approx is None:
        print("유효한 모서리가 없으므로 테이블을 워프할 수 없습니다.")
        return None

    # 원근 변환을 위한 소스 및 대상 점 설정
    side_length = [np.linalg.norm(approx[i][0] - approx[i + 1][0]) for i in range(-1, 3)]
    upper_left_point_idx = min(range(4), key=lambda i: approx[i][0][0] + approx[i][0][1])

    if side_length[upper_left_point_idx] > side_length[(upper_left_point_idx + 1) % 4]:
        si = upper_left_point_idx
    else:
        si = (upper_left_point_idx + 1) % 4

    src_point = np.array([approx[si][0], approx[(si + 1) % 4][0], approx[(si + 2) % 4][0], approx[(si + 3) % 4][0]],
                        dtype=np.float32)
    dst_point = np.array([[0, 0], [0, HEIGHT - 1], [WIDTH - 1, HEIGHT - 1], [WIDTH - 1, 0]], dtype=np.float32)

    # 원근 변환 행렬 계산 및 적용
    matrix = cv2.getPerspectiveTransform(src_point, dst_point)
    dst = cv2.warpPerspective(src, matrix, (WIDTH, HEIGHT))[10:-10, 20:-20]

    return dst  # 워프된 테이블 이미지 반환


def find_balls(img):
    """
    이미지에서 공을 찾고 위치를 반환합니다.

    Args:
        img (np.ndarray): 입력 이미지.

    Returns:
        dict: 공의 색깔별 좌표.
    """
    ball_positions = {}
    for color, (lower, upper) in color_ranges.items():
        img_hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(img_hsv, lower, upper)
        kernel = np.ones((5, 5), np.uint8)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        if contours:
            largest_contour = max(contours, key=cv2.contourArea)
            M = cv2.moments(largest_contour)
            if M["m00"] != 0:
                cx = int(M["m10"] / M["m00"])
                cy = int(M["m01"] / M["m00"])
                ball_positions[color] = (cx, cy)
    return ball_positions


def place_balls_on_table(table_img, ball_positions):
    """
    테이블 이미지에 공을 배치합니다.

    Args:
        table_img (np.ndarray): 테이블 이미지.
        ball_positions (dict): 공의 색깔별 좌표.

    Returns:
        np.ndarray: 공이 배치된 테이블 이미지.
    """
    result_img = table_img.copy()
    for color, path in ball_images.items():
        ball_img = cv2.imread(path, cv2.IMREAD_UNCHANGED)
        if color in ball_positions:
            cx, cy = ball_positions[color]
            bh, bw = ball_img.shape[:2]
            y1, y2 = max(0, cy - bh // 2), min(result_img.shape[0], cy + bh // 2)
            x1, x2 = max(0, cx - bw // 2), min(result_img.shape[1], cx + bw // 2)
            ball_region = ball_img[0:y2 - y1, 0:x2 - x1]

            if ball_img.shape[2] == 4:
                alpha_ball = ball_img[:, :, 3] / 255.0
                alpha_ball = alpha_ball[0:y2 - y1, 0:x2 - x1]
                for c in range(3):
                    result_img[y1:y2, x1:x2, c] = (1 - alpha_ball) * result_img[y1:y2, x1:x2, c] + alpha_ball * \
                                                   ball_region[:, :, c]
            else:
                result_img[y1:y2, x1:x2] = ball_region
    return result_img


def main(image_file):
    """
    전체 프로세스를 실행합니다.
    """
    # 이미지 불러오기 및 전처리
    src = cv2.imread(image_file) #upload_image 폴더내 이미지 파일명(full path형태임)
    #src = cv2.imread('/home/eunhaday/aiffelthon_qfit/model_src/upload_image/K_12.jpg')
    
    if src is None:
        print("오류: 이미지를 불러올 수 없습니다. 파일 경로와 권한을 확인하세요.")
        exit()
    src = cv2.resize(src, (int(src.shape[1] * 0.15), int(src.shape[0] * 0.15)))

    # 테이블 모서리 찾기 및 원근 변환
    approx = find_corners(src)
    warped_table = get_warped_table(src, approx)

    # 공 찾기
    ball_positions = find_balls(warped_table)

    # 라벨 데이터 저장
    label_file = '/home/eunhaday/aiffelthon_qfit/model_src/result_image/ball_labels.txt'
    with open(label_file, 'w') as f:
        for color, (cx, cy) in ball_positions.items():
            f.write(f"{color} {cx} {cy}\n")
    print(f"라벨 데이터 [{label_file}] 저장")


    # 원본 이미지 출력 (공 위치 표시 없음)
    ###cv2_imshow(src)   #소스막음(2015.01.19,neh)
    # cv2.imwrite('original_image.png', src)  # 원본 이미지 저장

    #기존소스 막고 소스수정한 부분(2015.01.19,neh)
    src_cpy = cv2.cvtColor(src, cv2.COLOR_BGR2RGB)  # OpenCV는 BGR 형식이므로 RGB로 변환(2015.01.19,neh 수정)
    # 이미지 표시
    plt.imshow(src_cpy)
    plt.axis('off')  # 축 숨기기
    plt.show()
    

    # 탑뷰 이미지에 공 위치 표시
    for color, (cx, cy) in ball_positions.items():
        cv2.circle(warped_table, (cx, cy), 9, (30, 200, 255), 2)  # 탑뷰 이미지에 공 위치에 원 그리기
        cv2.putText(warped_table, f'{color} ({cx}, {cy})', (cx - 60, cy - 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6,
                    (30, 200, 255), 2)  # 텍스트 추가

   
    ###cv2_imshow(warped_table)   #소스막음(2015.01.19,neh)

    #기존소스 막고 소스수정한 부분(2015.01.19,neh)
    warped_table_cpy = cv2.cvtColor(warped_table, cv2.COLOR_BGR2RGB)  # OpenCV는 BGR 형식이므로 RGB로 변환(2015.01.19,neh 수정)    
    # 이미지 표시
    plt.imshow(warped_table_cpy)
    plt.axis('off')  # 축 숨기기
    plt.show()
    
    # cv2.imwrite('topview_with_ball_positions.png', warped_table)  # 탑뷰 이미지 저장

    # 테이블 이미지에 공 배치
    table_image_path = '/home/eunhaday/aiffelthon_qfit/model_src/image/table-cloth.png'
    table_image = cv2.imread(table_image_path)
    result_image = place_balls_on_table(table_image, ball_positions)

    # 결과 출력 및 저장
    ###cv2_imshow(result_image)  #소스막음(2015.01.19,neh)
    result_image_cpy = cv2.cvtColor(result_image, cv2.COLOR_BGR2RGB)  # OpenCV는 BGR 형식이므로 RGB로 변환(2015.01.19,neh 수정)    
    # 이미지 표시
    plt.imshow(result_image_cpy)
    plt.axis('off')  # 축 숨기기
    plt.show()    

    result_path = '/home/eunhaday/aiffelthon_qfit/model_src/result_image/table_with_balls.png'
    cv2.imwrite(result_path, result_image)
    print(f"결과 이미지 [{result_path}] 저장완료")

    logger.info(f"프로세스 성공적으로 완료처리")
    #return result_success

    
if __name__ == "__main__":
    
    if len(sys.argv) != 2:
        print("실행내용: python topview.py <image_file>")
        sys.exit(1)

    image_file = sys.argv[1]
    main(image_file)    