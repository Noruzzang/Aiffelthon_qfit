import 'package:flutter/material.dart';
import 'package:audioplayers/audioplayers.dart'; // 소리 재생을 위한 패키지
import 'main.dart';

void main() {
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return const MaterialApp(
      debugShowCheckedModeBanner: false, // 디버그 배너 비활성화
      home: HomePage(),
    );
  }
}

class HomePage extends StatefulWidget {
  const HomePage({super.key});

  @override
  State<HomePage> createState() => _HomePageState();
}

class _HomePageState extends State<HomePage>
    with SingleTickerProviderStateMixin {
  double _opacity = 0.0; // 초기 투명도 설정 (0: 완전 투명)
  final AudioPlayer _audioPlayer = AudioPlayer(); // 오디오 플레이어 인스턴스 생성

  @override
  void initState() {
    super.initState();
    _startAnimation();
    _navigateToNextPage();
  }

  @override
  void dispose() {
    _audioPlayer.dispose(); // 오디오 플레이어 해제
    super.dispose();
  }

  void _startAnimation() {
    // 애니메이션 효과 시작
    Future.delayed(const Duration(milliseconds: 500), () {
      setState(() {
        _opacity = 1.0; // 투명도를 점점 증가시킴
      });
    });
  }

  void _navigateToNextPage() async {
    // 5초 후에 당구 소리 재생 및 페이지 이동
    await Future.delayed(const Duration(seconds: 5));

    // 당구 소리 재생
    await _audioPlayer.play(AssetSource('sounds/ball_sound.mp3'));

    // 사운드 재생이 끝날 때까지 대기
    await _audioPlayer.onPlayerComplete.first;

    // 다음 페이지로 이동
    if (mounted) {
      Navigator.pushReplacement(
        context,
        MaterialPageRoute(builder: (context) => const Main()),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      // 배경색 설정
      backgroundColor: const Color.fromARGB(255, 226, 226, 224),
      body: Center(
        child: AnimatedOpacity(
          duration: const Duration(seconds: 5), // 애니메이션 지속 시간
          opacity: _opacity, // 현재 투명도
          curve: Curves.easeInOut, // 부드러운 애니메이션
          child: Image.asset(
            'images/load_image.png', // "load_image" 파일의 경로
            width: 250, // 이미지 너비
            height: 250, // 이미지 높이
          ),
        ),
      ),
    );
  }
}
