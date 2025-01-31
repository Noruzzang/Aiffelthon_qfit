import cv2
import numpy as np
import pymunk
from pymunk import Vec2d
import matplotlib.pyplot as plt
import os
import logging

############################################################################
# (A) 글로벌 설정
############################################################################

cue_choice = "white"  # "white" 또는 "yellow"
collision_log = []
frame_count = 0
last_collision_frame = -999
last_collision_type  = None

home_dir = os.path.expanduser("~")  # 홈 디렉토리 가져오기

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def load_ball_positions(label_file):
    bpos = {}
    try:
        with open(label_file, "r") as f:
            for line in f:
                parts = line.strip().split()
                if len(parts) >= 3:
                    bpos[parts[0]] = (int(parts[1]), int(parts[2]))
    except FileNotFoundError:
        print(f"[ERROR] 파일 '{label_file}'을 찾을 수 없습니다.")
    except ValueError:
        print(f"[ERROR] 파일 형식이 올바르지 않습니다. '공이름 x y' 형태여야 합니다.")
    return bpos

############################################################################
# (B) 충돌 이벤트 로깅 + 중복 쿠션 필터
############################################################################

def collision_logger(arbiter, space, data):
    global collision_log, cue_choice
    global frame_count, last_collision_frame, last_collision_type

    shapeA, shapeB = arbiter.shapes
    ctypeA = shapeA.collision_type
    ctypeB = shapeB.collision_type

    cue_ctype = 1 if cue_choice=="white" else 2

    collision_char = None
    # A가 큐볼
    if ctypeA == cue_ctype:
        if ctypeB == 99: collision_char = "C"
        elif ctypeB == 3: collision_char = "R"
        elif ctypeB == 1 and cue_ctype != 1: collision_char = "W"
        elif ctypeB == 2 and cue_ctype != 2: collision_char = "Y"
    # B가 큐볼
    elif ctypeB == cue_ctype:
        if ctypeA == 99: collision_char = "C"
        elif ctypeA == 3: collision_char = "R"
        elif ctypeA == 1 and cue_ctype != 1: collision_char = "W"
        elif ctypeA == 2 and cue_ctype != 2: collision_char = "Y"

    # 쿠션(C) 연속 충돌 필터
    if collision_char=="C":
        if last_collision_type=="C" and (frame_count - last_collision_frame)<3:
            return True

    if collision_char is not None:
        collision_log.append(collision_char)
        last_collision_type  = collision_char
        last_collision_frame = frame_count

    return True

############################################################################
# (C) 3쿠션 득점 판정 및 점수 매기기
############################################################################

def check_3cushion_score(log_list, cue_choice="white"):
    if cue_choice=="white":
        obj_balls = ["R","Y"]
    else:
        obj_balls = ["R","W"]

    cushion_count = 0
    hit_set = set()
    second_ball_hit = False

    for ch in log_list:
        if ch=="C":
            cushion_count+=1
        else:
            if ch in obj_balls:
                if ch not in hit_set:
                    hit_set.add(ch)
                    if len(hit_set)==2:
                        if cushion_count>=3:
                            second_ball_hit=True
                        else:
                            return False,"두 번째 목적구 전 쿠션 부족"
        if second_ball_hit:
            break

    if second_ball_hit:
        return True,"정상 득점(3쿠션)"
    else:
        if len(hit_set)==0:
            return False,"목적구 전혀 못 맞힘"
        elif len(hit_set)==1:
            return False,"목적구 1개만 맞힘"
        else:
            return False,"쿠션 3회 미만"

def first_collision_is_object_ball(log_list):
    for ch in log_list:
        if ch!="C":
            return True
    return False

def compute_shot_score(log_list, base_score=100):
    score=base_score
    if first_collision_is_object_ball(log_list):
        score+=50
    else:
        score-=30

    total_collisions=len(log_list)
    score-=(total_collisions*2)
    return score

############################################################################
# (D) 실제 시뮬레이션 (각도, 파워, 오프셋)
############################################################################

def simulate_shot(table_img, ball_positions, angle_deg, power_gauge, spin_offset):
    global collision_log, frame_count
    global last_collision_frame, last_collision_type

    collision_log=[]
    frame_count=0
    last_collision_frame=-999
    last_collision_type=None

    H,W=table_img.shape[:2]
    space=pymunk.Space()
    space.gravity=(0,0)
    space.damping=0.99

    cb=pymunk.Body(body_type=pymunk.Body.STATIC)
    rad=5.0
    ms=1.0
    left,right=rad,W-rad
    top,bottom=rad,H-rad

    segs=[]
    for pt1,pt2 in [((left,top),(right,top)),((left,bottom),(right,bottom)),
                    ((left,top),(left,bottom)),((right,top),(right,bottom))]:
        s=pymunk.Segment(cb,pt1,pt2,0.0)
        s.elasticity=0.90
        s.friction=0.05
        s.collision_type=99
        segs.append(s)
    space.add(cb,*segs)

    bod={}
    for ccol,(cx,cy) in ball_positions.items():
        bd=pymunk.Body(ms,pymunk.moment_for_circle(ms,0,rad))
        bd.position=(cx,cy)
        bd.angular_damping=0.1
        sh=pymunk.Circle(bd,rad)
        sh.elasticity=0.90
        sh.friction=0.05
        if ccol=="white":
            sh.collision_type=1
        elif ccol=="yellow":
            sh.collision_type=2
        elif ccol=="red":
            sh.collision_type=3
        else:
            sh.collision_type=10
        space.add(bd,sh)
        bod[ccol]=bd

    # 큐볼
    cue_ctype=1 if cue_choice=="white" else 2
    if cue_choice=="white":
        cue_ball_body=bod["white"]
    else:
        cue_ball_body=bod["yellow"]

    handler_any=space.add_wildcard_collision_handler(cue_ctype)
    handler_any.post_solve=collision_logger

    dt=1/60
    mx=1200
    friction_factor=0.02
    st_t=1.2

    # 파워가 10 초과하지 않도록 clamp
    power_gauge = min(power_gauge, 10.0)
    if power_gauge<0:
        power_gauge=0

    max_sp=200.0
    rads=np.deg2rad(angle_deg)
    dx,dy=np.cos(rads),-np.sin(rads)
    spd=(power_gauge/10)*max_sp

    imp_vec=Vec2d(dx,dy)*(spd*ms)

    offx,offy=spin_offset
    ip=cue_ball_body.position+Vec2d(offx,offy)
    cue_ball_body.apply_impulse_at_world_point(imp_vec,ip)

    traj={c:[] for c in bod}

    for _ in range(mx):
        frame_count+=1
        space.step(dt)

        all_stop=True
        for ccx,bb in bod.items():
            bb.velocity*=(1-friction_factor*dt)
            traj[ccx].append((bb.position.x,bb.position.y))
            if bb.velocity.length>st_t:
                all_stop=False

        if all_stop:
            break

    scored, reason=check_3cushion_score(collision_log,cue_choice)
    return scored, reason, traj, collision_log

############################################################################
# (E) Adaptive Search
############################################################################

def adaptive_search(table_img, ball_positions):
    """
    1) 초기 탐색(각도: 10도 간격, 파워: 1~10 정수, 오프셋: (0,0))
    2) 세밀 탐색(초기 탐색 결과 근처)
    """
    # 1단계
    initial_angles  = range(0,360,10)
    initial_powers  = np.arange(1,11,1.0)  # 1~10 정수
    initial_offsets = [(0,0)]

    best_shots=[]
    for ang in initial_angles:
        for pwr in initial_powers:
            for off in initial_offsets:
                # pwr이 이미 10 안에서만 탐색됨
                scored, reason, trj, clog=simulate_shot(table_img, ball_positions, ang, pwr, off)
                if scored:
                    shot_score=compute_shot_score(clog,base_score=100)
                    best_shots.append((shot_score, ang, pwr, off, reason, trj, clog))
    if not best_shots:
        print("[초기 탐색] 득점 샷 없음.")
        return None

    best_shot = max(best_shots, key=lambda x:x[0])
    bscore, bang, bpwr, boff, *etc = best_shot
    print(f"[초기 탐색 결과] Angle={bang}, Power={bpwr}, Offset={boff}, Score={bscore}")

    # 2단계
    fine_angles  = range(int(bang)-30, int(bang)+31, 5)
    # 파워 범위를 [1,10]로 제한
    min_power = max(bpwr-5, 1)
    max_power = min(bpwr+5, 10)
    fine_powers = np.arange(min_power, max_power+1, 1.0)

    fine_offsets= [(ox,oy)
                   for ox in range(boff[0]-1,boff[0]+2)
                   for oy in range(boff[1]-1,boff[1]+2)]

    best_fine=[]
    for ang2 in fine_angles:
        ang_mod=ang2%360
        for pw2 in fine_powers:
            pw2_clamped = min(pw2,10.0)
            for off2 in fine_offsets:
                scored, reason, trj, clog=simulate_shot(table_img, ball_positions, ang_mod, pw2_clamped, off2)
                if scored:
                    shot_score=compute_shot_score(clog,base_score=100)
                    best_fine.append((shot_score, ang_mod, pw2_clamped, off2, reason, trj, clog))

    if not best_fine:
        print("[세밀 탐색] 득점 샷 추가 발견 못함 → 초기 탐색 결과 사용")
        return best_shot

    best_fine_shot = max(best_fine, key=lambda x:x[0])
    return best_fine_shot

############################################################################
# (F) 시각화 함수(강도 바 포함)
############################################################################

def draw_power_bar(img, power_gauge):
    # 파워를 0~10 사이로 clamp
    power_gauge = min(power_gauge, 10.0)
    if power_gauge<0: 
        power_gauge=0

    bar_w=150
    bar_h=20
    x0,y0=20,20
    cv2.rectangle(img,(x0,y0),(x0+bar_w,y0+bar_h),(80,80,80),-1)
    fill_w=int(bar_w*(power_gauge/10))
    cv2.rectangle(img,(x0,y0),(x0+fill_w,y0+bar_h),(0,200,0),-1)
    txt=f"{power_gauge}/10"
    cv2.putText(img,txt,(x0+bar_w+5,y0+bar_h-5),
                cv2.FONT_HERSHEY_SIMPLEX,0.5,(255,255,255),1)

def draw_trajectory_on_table(table_img, traj, power_gauge):
    out_img=table_img.copy()
    col_map={"white":(255,255,255),"yellow":(0,255,255),"red":(0,0,255)}
    step=5
    for cname, points in traj.items():
        color_bgr=col_map.get(cname,(0,255,0))
        for i in range(0,len(points),step):
            x,y=points[i]
            cv2.circle(out_img,(int(x),int(y)),3,color_bgr,-1)

    draw_power_bar(out_img,power_gauge)
    return out_img

def show_front_hit_point(angle_deg, offset_xy):
    w,h=200,200
    center=(w//2,h//2)
    radius=80
    view=np.full((h,w,3),220,dtype=np.uint8)

    cv2.circle(view,center,radius,(200,200,200),-1)
    cv2.circle(view,center,radius,(0,0,0),2)
    rad=np.deg2rad(angle_deg)
    dx,dy=np.cos(rad),-np.sin(rad)
    scale_offset=0.1
    tx=center[0]+dx*radius*0.8+offset_xy[0]*scale_offset
    ty=center[1]+dy*radius*0.8+offset_xy[1]*scale_offset
    cv2.circle(view,(int(tx),int(ty)),8,(0,0,255),-1)
    cv2.putText(view,"HitHere",(int(tx)+10,int(ty)-10),
                cv2.FONT_HERSHEY_SIMPLEX,0.5,(0,0,0),2)

    out_rgb=cv2.cvtColor(view,cv2.COLOR_BGR2RGB)
    plt.figure(figsize=(3,3))
    plt.imshow(out_rgb)
    plt.axis("off")
    plt.title("Front View: Angle/Offset")
    plt.show()
    
    # Front View 저장
    front_view_path = os.path.join(home_dir, "aiffelthon_qfit", "model_src", "result_image", "front_view.png")
    cv2.imwrite(front_view_path, view)
    logger.info(f"Front View 이미지 [{front_view_path}] 저장")
    

############################################################################
# (G) 메인 함수
############################################################################

def main():  
    #topview에서 저장한 3개볼 이미지
    table_img_path = os.path.join(home_dir, "aiffelthon_qfit", "model_src", "result_image", "table_with_balls.png")
    label_file_path = os.path.join(home_dir, "aiffelthon_qfit", "model_src", "result_image", "ball_labels.txt")

    table_img=cv2.imread(table_img_path)
    if table_img is None:
        print(f"[ERROR] 테이블 이미지 불러오기 실패: {table_img_path}")
        return
    ball_positions=load_ball_positions(label_file_path)
    if not ball_positions:
        print("[ERROR] 공 위치 정보가 없습니다.")
        return

    result=adaptive_search(table_img, ball_positions)
    if result is None:
        print("득점 가능한 샷을 찾지 못했습니다.")
        return

    # 언패킹
    best_score, best_angle, best_power, best_offset, best_reason, best_traj, best_log = result
    print("\n[최종 결과]")
    print(f"Score={best_score}, Angle={best_angle}, Power={best_power}, Offset={best_offset}")
    print(f"Reason : {best_reason}")
    print(f"Collision Log : {best_log}")

    # 시각화
    out_img = draw_trajectory_on_table(table_img, best_traj, best_power)
    out_rgb = cv2.cvtColor(out_img, cv2.COLOR_BGR2RGB)
    plt.figure(figsize=(10,5))
    plt.imshow(out_rgb)
    plt.title(f"Best Shot: A={best_angle}, P={best_power}, Off={best_offset}, Score={best_score}")
    plt.axis("off")
    plt.show()

    # Best-Shot 저장
    best_shot_path = os.path.join(home_dir, "aiffelthon_qfit", "model_src", "result_image", "best_shot.png")
    cv2.imwrite(best_shot_path, out_img)
    logger.info(f"Best Shot 이미지 [{best_shot_path}] 저장")
    
    # 정면 타점 뷰
    show_front_hit_point(best_angle,best_offset)

if __name__=="__main__":
    main()
