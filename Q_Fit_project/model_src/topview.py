import numpy as np
import cv2
import matplotlib.pyplot as plt  # 최종 표시용
import os
import sys
import logging

home_dir = os.path.expanduser("~")  # 홈 디렉토리 가져오기

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 설정 값
WIDTH = 840  # 출력될 테이블 이미지 너비
HEIGHT = 420  # 출력될 테이블 이미지 높이
TABLE_WIDTH_MM= 800  # 테이블 실제 너비(mm)
TABLE_HEIGHT_MM = 400  # 테이블 실제 높이(mm)

# HSV 색상 범위 정의 (각 공의 색상을 감지하는 임계값)
color_range = {
    "red": ((0, 120, 70),  (10, 255, 255)),  # 기존 값
    "red2": ((170, 120, 70), (180, 255, 255)),  # 추가 값
    "white": ((0, 0, 160), (180, 80, 255)),
    "yellow" : ((15, 100, 100), (35, 255, 255))
}

# 공 이미지 경로
ball_image = {
    "red": os.path.join(home_dir, "aiffelthon_qfit", "model_src", "image", "red.png"),
    "white": os.path.join(home_dir, "aiffelthon_qfit", "model_src", "image", "white.png"),
    "yellow": os.path.join(home_dir, "aiffelthon_qfit", "model_src", "image", "yellow.png")
}


def overlay_frame(base_image, frame_image_path):
    # 프레임 이미지 로드 (4채널, BGRA)
    frame_image = cv2.imread(frame_image_path, cv2.IMREAD_UNCHANGED)
    if frame_image is None:
        print(f"[오류] 프레임 이미지 불러오기 실패: {frame_image_path}")
        return base_image  # 프레임 이미지가 없을 경우 원본을 그대로 반환

    h_b, w_b = base_image.shape[:2]  # 당구대 테이블 크기
    h_f, w_f = frame_image.shape[:2]  # 프레임 크기

    # 프레임이 더 크면 공이 배치된 이미지를 중앙에 배치
    x_offset = (w_f - w_b) // 2
    y_offset = (h_f - h_b) // 2

    # 프레임의 복사본 생성
    result = frame_image.copy()

    # base_image(공이 배치된 테이블 이미지)를 프레임 중앙에 배치
    result[y_offset:y_offset + h_b, x_offset:x_offset + w_b, :3] = base_image

    # 알파 블렌딩 (프레임 투명도 적용)
    if frame_image.shape[2] == 4:
        alpha = frame_image[:, :, 3] / 255.0  # 알파 채널 정규화
        alpha = cv2.merge((alpha, alpha, alpha))

        # 프레임과 base_image를 혼합하여 최종 이미지 생성
        result = (alpha * frame_image[:, :, :3] + (1 - alpha) * result[:, :, :3]).astype(np.uint8)

    return result

def find_corners(input_image, debug = False):
    input_hsv = cv2.cvtColor(input_image, cv2.COLOR_BGR2HSV)  # HSV 변환
    table_image_blue = cv2.inRange(input_hsv, (100, 100, 100), (120, 255, 255))
    table_image_green = cv2.inRange(input_hsv, (40,  40,  40),  (90, 255, 255))
    table_image = cv2.bitwise_or(table_image_blue, table_image_green)

    k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
    table_image_closing = cv2.morphologyEx(table_image, cv2.MORPH_CLOSE, k)

    contours, _ = cv2.findContours(table_image_closing, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        print("컨투어를 찾을 수 없음")
        return None

    contour = max(contours, key = lambda x: cv2.contourArea(x))
    epsilon = 0.02 * cv2.arcLength(contour, True)
    approx = cv2.approxPolyDP(contour, epsilon, True)

    if len(approx) != 4:
        print('테이블을 인식할 수 없어 사각형 모서리 4개를 찾지 못함')
        return None

    return approx

def get_warped_table(input_image, approx):
    if approx is None:
        print("유효한 모서리가 없어 테이블 워프 불가")
        return None

    side_length = [np.linalg.norm(approx[i][0] - approx[i + 1][0]) for i in range(-1, 3)]
    upper_left_point_idx = min(range(4), key = lambda i: approx[i][0][0] + approx[i][0][1])

    if side_length[upper_left_point_idx] > side_length[(upper_left_point_idx + 1) % 4]:
        si = upper_left_point_idx
    else:
        si = (upper_left_point_idx + 1) % 4

    src_point = np.array([approx[si][0],
                          approx[(si + 1) % 4][0],
                          approx[(si + 2) % 4][0],
                          approx[(si + 3) % 4][0]], dtype = np.float32)
    dst_point = np.array([[0, 0],[0, HEIGHT - 1], [WIDTH - 1, HEIGHT - 1],[WIDTH - 1, 0]], dtype = np.float32)

    matrix = cv2.getPerspectiveTransform(src_point, dst_point)
    dst = cv2.warpPerspective(input_image, matrix, (WIDTH, HEIGHT))
    # 끝부분 자르는 동작
    dst = dst[10:-10, 20:-20]  # 필요에 따라 조정
    return dst

def find_ball(image):
    ball_position = {}
    
    logger.info(f">>>>> find_ball()  cvtColor 호출전 ")
    image_hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    logger.info(f">>>>> find_ball()  cvtColor 호출후 ")

    for color, (lower, upper) in color_range.items():
        mask = cv2.inRange(image_hsv, np.array(lower, dtype=np.uint8), np.array(upper, dtype=np.uint8))
        
        # 빨간 공 감지를 위해 두 개의 마스크를 병합
        if color == "red":
            mask2 = cv2.inRange(image_hsv, np.array(color_range["red2"][0], dtype=np.uint8), 
                                            np.array(color_range["red2"][1], dtype=np.uint8))
            mask = cv2.bitwise_or(mask, mask2)  # 두 개의 빨간색 마스크 병합

        # 모폴로지 연산을 사용하여 노이즈 제거
        kernel = np.ones((5, 5), np.uint8)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
        mask = cv2.dilate(mask, kernel, iterations=2)  # 팽창 연산 추가 (흰 공을 더 뚜렷하게 인식)
        
        # 컨투어(윤곽선) 탐색
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        if not contours:
            continue

        # 가장 큰 contour만 선택하여 잡음 제거
        largest_contour = max(contours, key=cv2.contourArea)
        area = cv2.contourArea(largest_contour)

        # 공 크기 임계값 설정 (너무 작은 객체 제거)
        if area < 50:  # 작은 공도 감지 가능하도록 수정
            continue

        M = cv2.moments(largest_contour)
        if M["m00"] != 0:
            cx = int(M["m10"] / M["m00"])
            cy = int(M["m01"] / M["m00"])
            
            # 빨간 공은 병합된 마스크에서 좌표 저장
            if color in ["red", "red2"]:
                ball_position["red"] = (cx, cy)
            else:
                ball_position[color] = (cx, cy)

    return ball_position

def place_ball_on_table(table_image, ball_position):
    result_image = table_image.copy()
    
    for color, path in ball_image.items():
        if color not in ball_position:
            continue  # 감지되지 않은 공은 건너뛴다.

        ball_texture = cv2.imread(path, cv2.IMREAD_UNCHANGED)
        if ball_texture is None:
            print(f"[오류] 공 이미지 불러오기 실패 : {path}")
            continue

        cx, cy = ball_position[color]
        bh, bw = ball_texture.shape[:2]

        # 테두리를 벗어나지 않도록 조정
        cx = max(bw // 2, min(result_image.shape[1] - bw // 2, cx))
        cy = max(bh // 2, min(result_image.shape[0] - bh // 2, cy))

        y1, y2 = max(0, cy - bh // 2), min(result_image.shape[0], cy + bh // 2)
        x1, x2 = max(0, cx - bw // 2), min(result_image.shape[1], cx + bw // 2)

        ball_region = ball_texture[0:(y2 - y1), 0:(x2 - x1)]

        if ball_texture.shape[2] == 4:
            # 알파 채널이 있는 경우 (배경 유지)
            alpha_ball = ball_texture[:, :, 3] / 255.0
            alpha_ball = alpha_ball[0:(y2 - y1), 0:(x2 - x1)]
            for c in range(3):
                result_image[y1:y2, x1:x2, c] = (1 - alpha_ball) * result_image[y1:y2, x1:x2, c] + alpha_ball * ball_region[:, :, c]
        else:
            result_image[y1:y2, x1:x2] = ball_region

    return result_image

def main(image_file):
    
    # 1) 원본 이미지 불러오기
    input_image = cv2.imread(image_file) #upload_image 폴더내 이미지 파일명(full path형태임)        
    #logger.info(f"input_image: {input_image}")
    
    if input_image is None:
        print("[오류] 이미지 불러오기 실패")
        return

    # 1.1) 크기 조정
    input_image = cv2.resize(input_image, (int(input_image.shape[1] * 0.15), int(input_image.shape[0] * 0.15)))

    # 2) 테이블 모서리 찾고 원근 변환
    approx = find_corners(input_image)
    warped_table = get_warped_table(input_image, approx)
    logger.info(f">>>>> get_warped_table() 찾은 이후")

    # 3) 공 찾기
    ball_position = find_ball(warped_table)
    logger.info(f">>>>> find_ball() 처리 이후")

    # 4) 라벨 데이터 저장
    label_text_path = os.path.join(home_dir, "aiffelthon_qfit", "model_src", "result_image", "ball_labels.txt")
    
    with open(label_text_path, 'w') as f:
        for color, (cx, cy) in ball_position.items():
            f.write(f"{color} {cx} {cy}\n")
    print(f"라벨 데이터 '{label_text_path}'에 저장")

    # 5) 디버그 표시 (원본)
    input_image_cpy = cv2.cvtColor(input_image, cv2.COLOR_BGR2RGB)
    plt.imshow(input_image_cpy)
    plt.title("Original Image (Resized)")
    plt.axis('off')
    plt.show()

    # 6) 탑뷰에 공 위치 시각적 표시
    if warped_table is not None:
        for color, (cx, cy) in ball_position.items():
            cv2.circle(warped_table, (cx, cy), 9, (30, 200, 255), 2)
            cv2.putText(warped_table,f'{color} ({cx},{cy})',(cx - 60,cy - 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (30, 200, 255), 2)

        warped_table_cpy = cv2.cvtColor(warped_table, cv2.COLOR_BGR2RGB)
        plt.imshow(warped_table_cpy)
        plt.title("Top-View Table with Ball Positions")
        plt.axis('off')
        plt.show()

    # 7) 테이블 천 이미지 경로
    # 테이블 바탕 이미지(천) 불러와서 공 배치
    cloth_image_path = os.path.join(home_dir, "aiffelthon_qfit", "model_src", "image", "table-cloth.png")
    
    table_image = cv2.imread(cloth_image_path)
    if table_image is None:
        print("[오류] 테이블 천 이미지 불러오기 실패")
        return

    result_image = place_ball_on_table(table_image, ball_position)
    result_image_cpy = cv2.cvtColor(result_image, cv2.COLOR_BGR2RGB)
    plt.imshow(result_image_cpy)
    plt.title("Result - Table with Ball Positions")
    plt.axis('off')
    plt.show()

    # 7.1) 원하는 경로에 저장 (옵션)
    #billiard_result_path = os.path.join(home_dir, "aiffelthon_qfit", "model_src", "image", "billiard_result.png")
    # 이미지 저장
    #cv2.imwrite(billiard_result_path, result_image)
    #logger.info(f"결과 이미지: [{billiard_result_path}] 저장")

    # 8) 프레임 이미지 합성 (핵심)
    frame_image_path = os.path.join(home_dir, "aiffelthon_qfit", "model_src", "image", "frame.png")
    final_image = overlay_frame(result_image, frame_image_path)

    # 9) 최종 결과 표시
    final_image_cpy = cv2.cvtColor(final_image, cv2.COLOR_BGR2RGB)
    plt.figure(figsize = (10, 5))
    plt.imshow(final_image_cpy)
    plt.title("Final - Billiard Table with Frame Overlay")
    plt.axis("off")
    plt.show()

    # 최종 합성본 파일 저장 (옵션)
    result_path = os.path.join(home_dir, "aiffelthon_qfit", "model_src", "result_image", "table_with_balls.png")
    cv2.imwrite(result_path, result_image)
    logger.info(f"프레임 이미지가 합성된 최종 이미지: [{result_path}] 저장")


if __name__ == "__main__": 
    
    if len(sys.argv) != 2:
        print("실행내용: python topview.py <image_file>")
        sys.exit(1)

    image_file = sys.argv[1]  
    main(image_file) 