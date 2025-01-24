![image](https://github.com/user-attachments/assets/a1b9ea79-93a9-4971-b3a6-3bac2c5ef5b8)    
빨간부분에 설명 써주세요       


                     

<br>
12/31/2024   
노은하       
- pymunk_test_neh_0102.ipynb 업로드         
- pybullet_colab_test.ipynb 업로드          
- pybull_test.ipynb 업로드            
     
김지혜    
- best_pt_pymunk_Jihye.ipynb 업로드    
- best_pt_pybullet_Jihye.ipynb 업로드    
<br>

1/2/2025    
김지혜    
Yolov8_train_made_by_Mingoo_run_by_Jihye.ipynb 업로드    

강민구    
Yolov8_predict.ipynb 업로드    
<br>

1/3/2025    
노은하    
pymunk_test_neh_0102.ipynb 업로드    
<br>

1/6/2025    
김지혜    
- best_pt_January_6th_Jihye 업로드    
- best_pt_predict_tested_January_6th_Jihye 업로드    
<br>

1/7/2025    
노은하    
pymunk_test_neh_0102.ipynb 업로드    
- pymunk로 작업된 소스반영, 코멘트에 2025.01.03으로 되어 있는부분이 최종소스부분임    
- 해당부분과 그위의 파이썬 라이브러리 pip install 부분만 같이 실행하면 동일한 모습가능    
- 이미지는 본인의 이미지로 변경하고 테스트 요망    

임만순    
qfit_model&engine1(250103).ipynb 업로드    
<br>

1/8/2025    
노은하    
- pymunk_test_neh_0108_1.ipynb 업로드(스탭별로 경로표시)    
- pymunk_test_neh_0108_2.ipynb 업로드(수구기준으로 스탭별 경로표시)    
- pymunk_test_neh_0108_3.ipynb 업로드(수구와 목적공1개의 두공간의 경로를 표시, 최종소스)    
<br>

1/9/2025    
조규원    
pymunk_sim2.ipynb 업로드    
<br>

1/13/2025    
조규원    
pymunk_sim2.ipynb 주석 달아서 수정 업로드    

임만순    
- model_test_ims_0113_1.ipynb ((25년 1월 둘째 주) 물리엔진 시뮬레이션 테스트 소스 복구)    
- model_test_ims_0113_2.ipynb (다른 4구 이미지 변경 테스트)    
- model_test_ims_0113_3.ipynb (Yolov8을 학습 시킨 best_January_3rd_Jihye.pt로 테스트)    
<br>

1/14/2025    
윤석진    
YYY.ipynb 업로드    

조규원    
pymunk_sim3.ipynb 업로드    

임만순    
- model_test_ims_0114_1.ipynb (성공 이미지와 라벨로 위치 테스트)    
- model_test_ims_0114_2.ipynb (임팩트 포인트 테스트)    
- model_test_ims_0114_3.ipynb (성공 이미지와 라벨을 활용한 물리 테스트)    
<br>

1/15/2025    
윤석진    
YYY_0115.ipynb 업로드    
<br>

1/16/2025    
윤석진    
YYY_0116.ipynb 업로드    
<br>

1/21/2025    
임만순    
- 캐롬 3쿠션.RTF (3쿠션 용어 및 경기 규칙에 대한 내용)    
- cv_workflow01_02.ipynb (강민구님의 탑뷰 이미지 표시 소스코드에서 명확성, 가독성, 유지보수를 위해 다음과 같이 수정함)    
  - red → red_ball | white → white_ball | yellow → yellow_ball    
  - yellow_ball 인식률 개선을 위해 HSV 값 범위 조정 : ((20, 100, 100), (30, 255, 255)) → ((15, 100, 100), (40, 255, 255))    
  - table_with_balls_final.png 저장 경로 지정    
  - 명확성, 가독성, 유지보수를 위해 저장 경로를 재구성함 (명명 규칙을 폴더명은 Camel Case로, 파일명은 Snake Case로 표준화)    
```
　　Q-FitProj/
　　├── DataCollection&Preprocessing/
　　│   ├── DataCollection/
　　│   │   ├── MatchVideo/
　　│   │   │   ├── [동영상 파일 (145GB)]
　　│   │   ├── ViewImage/
　　│   │   │   ├── SideViewImage/
　　│   │   │   │   ├── side_view_image_01.jpg
　　│   │   │   │   ├── side_view_image_02.jpg
　　│   │   │   │   ├── side_view_image_03.jpg
　　│   │   │   │   ├── side_view_image_04.jpg
　　│   │   │   │   ├── side_view_image_05.jpg
　　│   │   │   │   ├── side_view_image_06.jpg
　　│   │   │   ├── TopViewImage/
　　│   │   │   │   ├── top_view_image_01.png
　　│   │   │   │   ├── top_view_image_02.png
　　│   │   │   │   ├── top_view_image_03.jpg
　　│   │   │   │   ├── top_view_image_04.jpg
　　│   ├── data_collection.mp4
　　│   ├── data_preprocessing.ipynb
　　├── DatasetConfiguration/
　　│   ├── test/
　　│   ├── train/
　　│   ├── valid/
　　│   ├── data.yaml
　　│   ├── readme_dataset.txt
　　│   ├── readme_roboflow.txt
　　│   ├── yolov8_q_fit_v1.0.zip
　　├── ModelTraining/
　　│   ├── CommonData/
　　│   │   ├── TableSourceImage/
　　│   │   │   ├── billiard_cloth.png
　　│   │   │   ├── red_ball.png
　　│   │   │   ├── table_frame.png
　　│   │   │   ├── white_ball.png
　　│   │   │   ├── yellow_ball.png
　　│   ├── Image&TextResult/
　　│   │   ├── billiard_label.txt
　　│   │   ├── billiard_result.png
　　│   ├── cv_workflow01_Mingoo_0106.ipynb
　　│   ├── cv_workflow02_(colab)_Mansoon_0121.ipynb
　　│   ├── cv_workflow03_(local)_Mansoon_0123.ipynb
　　├── (예정) ModelEvaluation&Optimization/
　　├── AppDevelopment&Integration/
　　│   ├── pymunk_simulation01.ipynb
　　└── (예정) Deployment&Maintenance/
```
- scenario01_ims_0120.ipynb ()    
  - 탑뷰 좌표인 label.txt과 result.png 값을 참고하여 경로 계산 및 시각화 (백색 수구 기준)    
  - PyBullet(물리 시뮬레이션 라이브러리)을 이용해 공의 움직임 확인    
<br>

1/22/2025    
임만순    
플러터 개발 환경 설정    
<br>

1/23/2025    
임만순)    
cv_workflow03_(local)_Mansoon_0123.ipynb    
<br>

