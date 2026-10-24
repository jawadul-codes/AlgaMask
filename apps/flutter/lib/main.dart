import 'package:flutter/material.dart';

import 'src/algamask/input_screen.dart';
import 'src/algamask/design.dart';

void main() => runApp(const AlgaMaskApp());

class AlgaMaskApp extends StatelessWidget {
  const AlgaMaskApp({super.key});
  @override
  Widget build(BuildContext context) => MaterialApp(
    title: 'AlgaMask',
    debugShowCheckedModeBanner: false,
    theme: ThemeData(
      useMaterial3: true,
      colorScheme: ColorScheme.fromSeed(
        seedColor: AlgaColors.forest,
        surface: Colors.white,
      ),
      scaffoldBackgroundColor: AlgaColors.canvas,
      fontFamily: 'Arial',
      textTheme: ThemeData.light().textTheme.apply(
        bodyColor: AlgaColors.ink,
        displayColor: AlgaColors.ink,
      ),
      inputDecorationTheme: InputDecorationTheme(
        filled: true,
        fillColor: Colors.white,
        border: OutlineInputBorder(
          borderRadius: BorderRadius.circular(8),
          borderSide: const BorderSide(color: AlgaColors.line),
        ),
        enabledBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(8),
          borderSide: const BorderSide(color: AlgaColors.line),
        ),
        contentPadding: const EdgeInsets.symmetric(
          horizontal: 13,
          vertical: 14,
        ),
      ),
      filledButtonTheme: FilledButtonThemeData(
        style: FilledButton.styleFrom(
          backgroundColor: AlgaColors.forest,
          foregroundColor: Colors.white,
          padding: const EdgeInsets.symmetric(horizontal: 22, vertical: 17),
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
        ),
      ),
    ),
    home: const InputScreen(),
  );
}
