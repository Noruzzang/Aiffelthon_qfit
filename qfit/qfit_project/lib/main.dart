import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:image_picker/image_picker.dart';
import 'select.dart'; // 선택된 페이지 추가

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return const MaterialApp(
      debugShowCheckedModeBanner: false,
      home: Main(),
    );
  }
}

class Main extends StatelessWidget {
  const Main({super.key});

  @override
  Widget build(BuildContext context) {
    WidgetsFlutterBinding.ensureInitialized();
    SystemChrome.setPreferredOrientations([
      DeviceOrientation.landscapeLeft,
      DeviceOrientation.landscapeRight,
    ]);

    return Scaffold(
      body: SafeArea( // SafeArea로 감싸서 상단 시간표시바를 고려
        child: Container(
          decoration: const BoxDecoration(
            color: Color.fromARGB(255, 49, 143, 255), // 전체 배경색 추가
            image: DecorationImage(
              image: AssetImage('images/frame.png'),
              fit: BoxFit.fill, // 이미지를 비율에 상관없이 화면에 꽉 채움
            ),
          ),
          child: Center(
            child: Row(
              mainAxisAlignment: MainAxisAlignment.center, // 아이콘을 수평으로 중앙에 배치
              children: [
                Column(
                  mainAxisAlignment: MainAxisAlignment.center, // 수직 중앙 정렬
                  children: [
                    GestureDetector(
                      onTap: () {
                        _openCamera(context);
                      },
                      child: Image.asset(
                        'images/icon/camera_icon.png',
                        width: 100,
                        height: 100,
                      ),
                    ),
                    const SizedBox(height: 0),
                    Image.asset(
                      'images/camera_txt.png',
                      width: 80,
                    ),
                  ],
                ),
                const SizedBox(width: 120),
                Column(
                  mainAxisAlignment: MainAxisAlignment.center, // 수직 중앙 정렬
                  children: [
                    GestureDetector(
                      onTap: () {
                        _openGallery(context);
                      },
                      child: Image.asset(
                        'images/icon/gallery_icon.png',
                        width: 90,
                        height: 90,
                      ),
                    ),
                    const SizedBox(height: 9),
                    Image.asset(
                      'images/gallery_txt.png',
                      width: 75,
                    ),
                  ],
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }

  void _openCamera(BuildContext context) async {
    final ImagePicker picker = ImagePicker();
    final XFile? image = await picker.pickImage(source: ImageSource.camera);

    if (image != null) {
      Navigator.push(
        context,
        MaterialPageRoute(
          builder: (context) => SelectPage(cameraImagePath: image.path),
        ),
      );
    } else {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('사진 찍기 취소됨.')),
      );
    }
  }

  void _openGallery(BuildContext context) async {
    final ImagePicker picker = ImagePicker();
    final XFile? image = await picker.pickImage(source: ImageSource.gallery);

    if (image != null) {
      Navigator.push(
        context,
        MaterialPageRoute(
          builder: (context) => SelectPage(galleryImagePath: image.path),
        ),
      );
    } else {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('갤러리 선택 취소됨.')),
      );
    }
  }
}