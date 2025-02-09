import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:flutter/material.dart';
import 'dart:io';
import 'package:image_picker/image_picker.dart';
import 'main.dart';
import 'dart:typed_data';

class ResultPage extends StatefulWidget {
  //final String? imagePath; //카메라 혹은 갤러리의 이미지정보(path까지 포함된)
  //final String? cameraImagePath;
  final String imagePrefix; // 이미지 파일명의 prefix (ex: "20250202093422_0")

  const ResultPage({super.key, required this.imagePrefix});

  @override
  _ResultPageState createState() => _ResultPageState();
}

class _ResultPageState extends State<ResultPage> {

  String bestShotImage = '';  // Best Shot 이미지 URL 저장
  String frontViewImage = ''; // Front View 이미지 URL 저장
  String powerGaugeImage = ''; // power Gauge 이미지 URL 저장


  @override
  void initState() {
    super.initState();
    fetchAndSetImageUrls(); // 이미지 URL 가져오기
  }

  Future<void> fetchAndSetImageUrls() async {
    try {
      Map<String, dynamic> imageUrls = await fetchImageUrls(widget.imagePrefix);

      print("API 응답: $imageUrls");

      setState(() {
        bestShotImage = imageUrls['best_shot'] ?? '';
        frontViewImage = imageUrls['front_view'] ?? '';
        powerGaugeImage = imageUrls['power_gauge'] ?? '';
      });

      print("Best Shot Image: $bestShotImage");
      print("Front View Image: $frontViewImage");
      print("Power Gauge Image: $powerGaugeImage");
    } catch (e) {
      print("API 요청 실패: $e");
    }
  }

  //FastAPI에서 3개의 이미지 URL 가져오기
  Future<Map<String, dynamic>> fetchImageUrls(String imagePrefix) async {
    try {
      var apiBaseUrl = 'https://7a3f-112-172-64-10.ngrok-free.app/image_info/'; // FastAPI 서버 주소
      //var url = Uri.parse('$apiBaseUrl/image_info/$imagePrefix'); // 20250204201549_0
      //print('API 요청 URL: $url'); // 요청 URL 확인

      var response = await http.get(
        Uri.parse(apiBaseUrl + imagePrefix), // 입력된 URL 사용
        headers: {
          'Accept': 'application/json',
          'Content-Type': 'application/json',
          'ngrok-skip-browser-warning': '69420',
        },
      );

      // 서버 응답이 JSON이 맞는지 확인
      print("서버 응답 상태 코드: ${response.statusCode}");
      print("서버 응답 본문: ${response.body}");

      if (response.statusCode == 200) {
        //Map<String, dynamic> jsonResponse = jsonDecode(response.body);
        final jsonResponse = jsonDecode(response.body);

        // JSON 구조 확인
        if (jsonResponse.containsKey("image_urls")) {

          return jsonResponse["image_urls"];
        } else {
          throw Exception("서버 응답에 'image_urls' 키가 없음: ${jsonResponse}");
        }
      } else {
        throw Exception("API 요청 실패: 상태 코드 ${response.statusCode}");
      }
    } catch (e) {
      throw Exception('API 요청 오류: $e');
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Container(
        decoration: BoxDecoration(
          image: DecorationImage(
            image: AssetImage('images/bg_color.png'), // 백그라운드 이미지 설정
            fit: BoxFit.cover, // BoxFit.cover로 화면에 맞게 이미지가 확장되도록 설정
          ),
        ),
        child: Padding(
          padding: EdgeInsets.only(top: MediaQuery.of(context).padding.top),
          child: Row(
            children: [
              // 왼쪽 부분: 위/아래로 두 부분 나누기
              Expanded(
                flex: 1, // 왼쪽 영역 크기
                child: Column(
                  children: [
                    // 위쪽 부분: flex 값을 2로 설정하여 크기 조정
                    Expanded(
                      flex: 1,  // 왼쪽 상단을 두 배 크게 설정
                      child: Center(  // Center 위젯 추가하여 중앙 배치
                        child: Container(
                          alignment: Alignment.center,  // 이미지를 정확히 중앙에 배치
                          decoration: BoxDecoration(
                            image: DecorationImage( //예측 당점 이미지
                              image: frontViewImage.isNotEmpty
                                  ? NetworkImage(frontViewImage, headers: {'Accept': 'application/json',
                                'ngrok-skip-browser-warning': '69420'}, ) // FastAPI에서 받은 이미지 적용
                                  : AssetImage('images/jellyfish.png') as ImageProvider, // 기본 이미지
                              fit: BoxFit.scaleDown, // BoxFit을 사용하여 이미지를 맞춤
                            ),
                          ),
                          width: 170, // 이미지의 가로 크기 설정
                          height: 300, // 이미지의 세로 크기 설정
                        ),
                      ),
                    ),
                    // 아래쪽 부분: flex 값을 1로 설정하여 크기 조정
                    Expanded(
                      flex: 1,  // 왼쪽 하단은 기본 크기 설정
                      child: Center(  // Center 위젯 추가하여 중앙 배치
                        child: Container(
                          alignment: Alignment.center,  // 이미지를 정확히 중앙에 배치
                          decoration: BoxDecoration(
                            image: DecorationImage( //파워 게이지 이미지 (width: 250, height: 318)
                              image: powerGaugeImage.isNotEmpty
                                  ? NetworkImage(powerGaugeImage, headers: {'Accept': 'application/json',
                                'ngrok-skip-browser-warning': '69420'},) // FastAPI에서 받은 이미지 적용
                                  : AssetImage('images/jellyfish.png') as ImageProvider, // 기본 이미지
                              fit: BoxFit.scaleDown, // BoxFit을 사용하여 이미지를 맞춤
                            ),
                          ),
                          width: 170, // 이미지의 가로 크기 설정
                          height: 300, // 이미지의 세로 크기 설정
                        ),
                      ),
                    ),
                  ],
                ),
              ),

              // 오른쪽 화면: 하나의 화면
              Expanded(
                flex: 3, // 오른쪽 영역 크기
                child: Center(  // Center 위젯 추가하여 중앙 배치
                  child: Container(
                    alignment: Alignment.center,  // 이미지를 정확히 중앙에 배치
                    decoration: BoxDecoration(
                      image: DecorationImage(
                        image: bestShotImage.isNotEmpty
                            ? NetworkImage(bestShotImage, headers: {'Accept': 'application/json',
                          'ngrok-skip-browser-warning': '69420'},)
                            : AssetImage('images/with_ball.png'), // 임시 이미지
                        fit: BoxFit.scaleDown, // BoxFit을 사용하여 이미지를 맞춤
                      ),
                    ),
                    width: 590, // 이미지의 가로 크기 설정
                    height: 400, // 이미지의 세로 크기 설정
                  ),
                ),
              ),

              // 사이드 네비게이션 바 (오른쪽으로 이동)
              _buildSideNavigationBar(context),
            ],
          ),
        ),
      ),
    );
  }


  // 사이드 네비게이션 바 (오른쪽으로 이동)
  Widget _buildSideNavigationBar(BuildContext context) {
    return Container(
      width: 80, // 사이드 메뉴바의 고정 크기
      decoration: BoxDecoration(
        color: Colors.white,
        boxShadow: [
          BoxShadow(
            color: Colors.grey.withOpacity(0.5),
            spreadRadius: 2,
            blurRadius: 5,
            offset: const Offset(-3, 0), // 사이드 바를 오른쪽으로 이동
          ),
        ],
      ),
      child: Column(
        mainAxisAlignment: MainAxisAlignment.spaceEvenly,
        children: [
          const SizedBox(height: 0),
          GestureDetector(
            onTap: () {
              Navigator.pop(context); // 뒤로 가기
            },
            child: Image.asset('images/icon/back_icon.png', width: 40, height: 40),
          ),
          const SizedBox(height: 30),
          // 카메라 버튼 클릭 시 카메라 페이지로 이동
          GestureDetector(
            onTap: () {
              //_openCamera(context);
            },
            child: Image.asset(
              'images/icon/camera_icon.png',
              width: 70,
              height: 70,
            ),
          ),
          const SizedBox(height: 30),
          GestureDetector(
            onTap: () {
              Navigator.pushReplacement(
                context,
                MaterialPageRoute(builder: (context) => const Main()),
              );
            },
            child: Image.asset('images/icon/home_icon.png', width: 40, height: 40),
          ),
          const SizedBox(height: 0),
        ],
      ),
    );
  }

  /*
  // 카메라로 사진을 찍기 위한 함수
  void _openCamera(BuildContext context) async {
    final ImagePicker picker = ImagePicker();
    final XFile? image = await picker.pickImage(source: ImageSource.camera);

    if (image != null) {
      Navigator.push(
        context,
        MaterialPageRoute(
          //builder: (context) => ResultPage(cameraImagePath: image.path, predictionResult: '',),
          builder: (context) => ResultPage(cameraImagePath: image.path, result:{}, imagePath: image.path,),
        ),
      );
    } else {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('사진 찍기 취소됨.')),
      );
    }
  } */
}


