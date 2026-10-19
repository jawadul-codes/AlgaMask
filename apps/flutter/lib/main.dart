import 'package:flutter/material.dart';

import 'src/algamask/input_screen.dart';

void main() => runApp(const AlgaMaskApp());

class AlgaMaskApp extends StatelessWidget {
  const AlgaMaskApp({super.key});
  @override
  Widget build(BuildContext context) => MaterialApp(
    title: 'AlgaMask',
    debugShowCheckedModeBanner: false,
    theme: ThemeData(
      useMaterial3: true,
      colorScheme: ColorScheme.fromSeed(seedColor: const Color(0xff226149)),
      scaffoldBackgroundColor: const Color(0xfff4f6f0),
    ),
    home: const InputScreen(),
  );
}
