import 'dart:io';
import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'package:flutter/services.dart';
import 'package:image/image.dart' as img;
import 'package:image_picker/image_picker.dart';
import 'package:path/path.dart';
import 'package:mime/mime.dart';
import 'package:http_parser/http_parser.dart';
import 'main.dart';
import 'result.dart';

class SelectPage extends StatelessWidget {
  final String? cameraImagePath; //카메라로 찍은 사진정보
  final String? galleryImagePath; //조회한 갤러리의 이미지정보

  const SelectPage({
    super.key,
    this.cameraImagePath,
    this.galleryImagePath,
  });

  @override
  Widget build(BuildContext context) {
    WidgetsFlutterBinding.ensureInitialized();
    SystemChrome.setPreferredOrientations([
      DeviceOrientation.landscapeLeft,
      DeviceOrientation.landscapeRight,
    ]);

    return Scaffold(
      body: Padding(
        padding: EdgeInsets.only(top: MediaQuery.of(context).padding.top),
        child: Container(
          decoration: BoxDecoration(
            image: DecorationImage(
              image: AssetImage('images/bg_color.png'),
              fit: BoxFit.cover,
            ),
          ),
          child: Center(
            child: Row(
              children: [
                Expanded(
                  child: Column(
                    children: [
                      const SizedBox(height: 0),
                      const SizedBox(height: 0),
                      Expanded(
                        child: Center(
                          child: Column(
                            mainAxisAlignment: MainAxisAlignment.center,
                            crossAxisAlignment: CrossAxisAlignment.center,
                            children: [
                              if (cameraImagePath != null)
                                _buildImageSection('images/cameraImage_txt.png',
                                    cameraImagePath!, context),
                              if (galleryImagePath != null)
                                _buildImageSection(
                                    'images/galleryImage_txt.png',
                                    galleryImagePath!,
                                    context),
                            ],
                          ),
                        ),
                      ),
                    ],
                  ),
                ),
                _buildSideNavigationBar(context),
              ],
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildImageSection(
      String titleImage, String imagePath, BuildContext context) {
    return FutureBuilder<img.Image>(
      //비동기 작업(Future)이 완료될 때까지 대기 (완료되면 snapshot.data에 이미지가 저장됨)
      future: _loadImage(File(imagePath)), //비동기적으로 이미지 로드
      builder: (context, snapshot) {
        if (snapshot.connectionState == ConnectionState.done &&
            snapshot.hasData) {
          //이미지 로딩이 완료되었고, 데이터가 있는 경우 UI 렌더링 진행
          final img.Image image = snapshot.data!;
          final bool isPortrait = image.height >
              image.width; //세로 이미지인지 확인(true이면 세로 이미지, false이면 가로 이미지)

          return Column(
            //세로 방향으로 요소 배치
            crossAxisAlignment: CrossAxisAlignment.start, //왼쪽 정렬
            children: [
              Image.asset(titleImage,
                  width: 170), //제목(타이틀) 이미지를 표시하기 위한 이미지 경로(assets 폴더에서 불러와 표시)
              const SizedBox(height: 10), //간격 추가
              Container(
                decoration: BoxDecoration(
                  //그림자 효과 적용
                  boxShadow: [
                    BoxShadow(
                      color: Colors.black.withOpacity(0.3),
                      spreadRadius: 5,
                      blurRadius: 7,
                      offset: const Offset(5, 5),
                    ),
                  ],
                ),
                child: ClipRRect(
                  borderRadius: BorderRadius.circular(10), //모서리 둥글게
                  child: RotatedBox(
                    quarterTurns: isPortrait ? 1 : 0, //세로 사진이면 90도 회전
                    child: Image.file(
                      File(imagePath), //표시할 이미지의 파일 경로(파일에서 이미지 로드)
                      width: 550,
                      height: 270,
                      fit: BoxFit.cover, //이미지를 컨테이너 크기에 맞게 채우기
                    ),
                  ),
                ),
              ),
              const SizedBox(height: 30),
            ],
          );
        } else {
          return const Center(child: CircularProgressIndicator());
        }
      },
    );
  }

  Future<img.Image> _loadImage(File file) async {
    final bytes = await file.readAsBytes();
    final image = img.decodeImage(bytes)!;
    print('image: $image');
    return image;
  }

  //--------------------------------------------------------------
  // 사진을 찍은 이미지파일명을 가지고, 파일저장 및 당구대 경로이미지 3개의
  // 정보를 받음
  // 해당정보에서 사용하는것은 prefix정보만 이용함 -> 3개의 url정보 얻어오고
  // 개별 이미지에서 해당 url에 파일명을 추가하여 화면에 표시함
  //--------------------------------------------------------------
  Future<Map<String, String>> _uploadImage(String imagePath) async {
    print('====== [ Sending request to server... Start ] ========');

    //print('imagePath: $imagePath');
    //요청을 보낼 서버의 URL을 설정
    var uri =
        Uri.parse('https://22f0-112-172-64-10.ngrok-free.app/upload_image/');

    //POST 요청을 보낼 MultipartRequest 객체를 생성
    var request = http.MultipartRequest('POST', uri);
    print('request: $request');

    // MIME 타입 확인
    String? mimeType = lookupMimeType(imagePath);

    //이미지 파일을 요청에 추가(imagePath 경로의 이미지를 읽어와서 'file'이라는 이름으로 업로드)
    /*request.files.add(await http.MultipartFile.fromPath(
      'file',
      imagePath,
      contentType: mimeType != null ? MediaType.parse(mimeType) : null,
    ));*/

    try {
      //서버로 요청 전송
      var response = await request.send();

      String bestShot = '';
      String frontView = '';
      String powerGauge = '';
      String prefix = '';

      //서버 응답 처리
      if (response.statusCode == 200) {
        //요청 성공 여부 확인
        //응답 데이터를 문자열로 변환
        var responseData = await response.stream.bytesToString();
        //print('서버응답결과: $responseData');

        //JSON 형식으로 파싱
        var decodedData = json.decode(responseData);
        //print('decodedData: $decodedData');

        // 'data'가 존재하고 비어 있지 않은지 확인
        if (decodedData.containsKey('data') && decodedData['data'].isNotEmpty) {
          // 'data' 항목을 순회하여 처리
          for (var item in decodedData['data']) {
            bool isLast = item == decodedData['data'].last; //마지막 항목인경우

            // 각 항목에서 'upload_image', 'best_shot', 'front_view' 값을 확인
            if (item.containsKey('upload_image') &&
                item['upload_image'] != null) {
              print('Upload Image: ${item['upload_image']}');
            }
            if (item.containsKey('best_shot') && item['best_shot'] != null) {
              bestShot = item['best_shot'] ?? '';
              print('bestShot: ${bestShot}');
            }
            if (item.containsKey('front_view') && item['front_view'] != null) {
              frontView = item['front_view'] ?? '';
              print('frontView: ${frontView}');
            }
            if (item.containsKey('power_gauge') &&
                item['power_gauge'] != null) {
              powerGauge = item['power_gauge'] ?? '';
              print('powerGauge: ${powerGauge}');
            }

            if (isLast) {
              //마지막항목인 경우
              // `/` 기준으로 나눈 뒤 마지막 요소(파일명) 가져오기
              String filename = bestShot.split('/').last;
              print('filename: $filename');

              // "_" 기준으로 split 후 앞의 두 개를 합치기
              List<String> parts = filename.split('_');
              prefix = "${parts[0]}_${parts[1]}"; // "20250202093422_0"

              print(prefix); // 결과: 20250202093422_0
            }
          }

          // Map 형식으로 결과 반환
          return {
            'best_shot': bestShot,
            'front_view': frontView,
            'power_gauge': powerGauge,
            'image_prefix': prefix
          };
        } else {
          throw Exception('Data 항목이 없거나 비어 있습니다');
        }
      } else {
        //리턴값이 200이 아닌경우 처리
        throw Exception('Failed to get prediction from server');
      }
    } catch (e) {
      //예외 처리
      print('Exception: $e');
      throw Exception('서버와의 통신 중 오류발생.');
    }
  }

  // 사이드 네비게이션 바
  Widget _buildSideNavigationBar(BuildContext context) {
    return Container(
      width: 80,
      decoration: BoxDecoration(
        color: Colors.white,
        boxShadow: [
          BoxShadow(
            color: Colors.grey.withOpacity(0.5),
            spreadRadius: 2,
            blurRadius: 5,
            offset: const Offset(-3, 0),
          ),
        ],
      ),
      child: Column(
        mainAxisAlignment: MainAxisAlignment.spaceEvenly,
        children: [
          const SizedBox(height: 0),
          GestureDetector(
            onTap: () async {
              if (cameraImagePath != null) {
                final XFile? photo =
                    await ImagePicker().pickImage(source: ImageSource.camera);
                print('photo.path: $photo.path');

                if (photo != null) {
                  Navigator.pushReplacement(
                    context,
                    MaterialPageRoute(
                        builder: (context) =>
                            SelectPage(cameraImagePath: photo.path)),
                  );
                }
              } else if (galleryImagePath != null) {
                final XFile? image =
                    await ImagePicker().pickImage(source: ImageSource.gallery);
                if (image != null) {
                  Navigator.pushReplacement(
                    context,
                    MaterialPageRoute(
                        builder: (context) =>
                            SelectPage(galleryImagePath: image.path)),
                  );
                }
              }
            },
            child:
                Image.asset('images/icon/back_icon.png', width: 40, height: 40),
          ),
          const SizedBox(height: 40),
          // 로딩 인디케이터 추가된 부분
          IconButton(
            onPressed: () async {
              // 로딩 인디케이터 띄우기
              showDialog(
                context: context,
                barrierDismissible: false, // 다이얼로그 밖을 터치해도 닫히지 않도록 설정
                builder: (BuildContext context) {
                  return const Center(
                    child: CircularProgressIndicator(), // 로딩 인디케이터
                  );
                },
              );

              try {
                //==========================================================================
                // 카메라로 찍은 이미지를 서버로 보내고, 당구대 경로 탐색한 이미지정보를 받는 API호출
                //============================================================================
                print(
                    'cameraImagePath : $cameraImagePath, galleryImagePath: $galleryImagePath');

                Map<String, String> result =
                    await _uploadImage(cameraImagePath ?? galleryImagePath!);
                print('result: $result');

                // 'best_shot' 키가 없거나 null이면 예외 처리
                if (!result.containsKey('best_shot') ||
                    result['best_shot'] == null) {
                  throw Exception("best_shot 이미지 URL을 찾을 수 없습니다.");
                }

                // 'image_prefix' 키가 없거나 null이면 예외 처리
                if (!result.containsKey('image_prefix') ||
                    result['image_prefix'] == null) {
                  throw Exception("image_prefix 정보를 찾을 수 없습니다.");
                }

                // imagePrefix가 null일 경우 빈 문자열을 설정
                String imagePrefix = result['image_prefix']!; // null이 아님이 보장됨
                print('imagePrefix: $imagePrefix');

                // 로딩 인디케이터 닫기
                Navigator.pop(context);
                Navigator.push(
                  context,
                  MaterialPageRoute(
                    builder: (context) => ResultPage(
                      //api호출후 받은 당구관련 이미지 3개를 보내서 화면에 표시
                      imagePrefix: imagePrefix, // 이미지파일의 prefix값
                      //imagePath: cameraImagePath ?? galleryImagePath!, //카메라 혹은 갤러리의 사진이미지
                    ),
                  ),
                );
              } catch (e) {
                // 예측 요청 실패 시 로딩 인디케이터 닫고 오류 메시지 표시
                print('오류 발생: $e');
                Navigator.pop(context);
                ScaffoldMessenger.of(context).showSnackBar(
                  SnackBar(content: Text('이미지를 가져오는 중 오류 발생: [$e]')),
                );
              }
            },
            icon: Image.asset('images/icon/search_icon.png',
                width: 60, height: 60),
          ),
          const SizedBox(height: 40),
          GestureDetector(
            onTap: () {
              Navigator.pushReplacement(
                context,
                MaterialPageRoute(builder: (context) => const Main()),
              );
            },
            child:
                Image.asset('images/icon/home_icon.png', width: 40, height: 40),
          ),
          const SizedBox(height: 0),
        ],
      ),
    );
  }
}
