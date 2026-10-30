import 'package:flutter/material.dart';

import 'src/algamask/landing_screen.dart';
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
        primary: AlgaColors.ink,
        surface: AlgaColors.paper,
      ),
      scaffoldBackgroundColor: AlgaColors.sage,
      fontFamily: 'Urbanist',
      textTheme: ThemeData.light().textTheme.apply(
        fontFamily: 'Urbanist',
        bodyColor: AlgaColors.ink,
        displayColor: AlgaColors.ink,
      ),
      inputDecorationTheme: InputDecorationTheme(
        filled: true,
        fillColor: AlgaColors.pale,
        border: OutlineInputBorder(
          borderRadius: BorderRadius.circular(14),
          borderSide: BorderSide.none,
        ),
        focusedBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(14),
          borderSide: const BorderSide(color: AlgaColors.ink, width: 1.5),
        ),
        errorBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(14),
          borderSide: const BorderSide(color: Color(0xffb3261e), width: 1.5),
        ),
        contentPadding: const EdgeInsets.symmetric(
          horizontal: 16,
          vertical: 16,
        ),
      ),
      filledButtonTheme: FilledButtonThemeData(
        style: ButtonStyle(
          backgroundColor: WidgetStateProperty.resolveWith(
            (s) => s.contains(WidgetState.disabled)
                ? const Color(0xffc9d1c8)
                : s.contains(WidgetState.hovered)
                ? AlgaColors.green
                : AlgaColors.ink,
          ),
          foregroundColor: WidgetStateProperty.resolveWith(
            (s) => s.contains(WidgetState.disabled)
                ? AlgaColors.muted
                : Colors.white,
          ),
          padding: WidgetStateProperty.all(
            const EdgeInsets.symmetric(horizontal: 26, vertical: 20),
          ),
          shape: WidgetStateProperty.all(const StadiumBorder()),
          textStyle: WidgetStateProperty.all(algaType(16, weight: 600)),
        ),
      ),
      textButtonTheme: TextButtonThemeData(
        style: TextButton.styleFrom(
          foregroundColor: AlgaColors.ink,
          shape: const StadiumBorder(),
        ),
      ),
      sliderTheme: const SliderThemeData(
        activeTrackColor: AlgaColors.ink,
        inactiveTrackColor: Color(0xffd3dbd1),
        thumbColor: AlgaColors.ink,
        overlayColor: Color(0x220f2a1f),
      ),
      switchTheme: SwitchThemeData(
        trackColor: WidgetStateProperty.resolveWith(
          (s) => s.contains(WidgetState.selected)
              ? AlgaColors.ink
              : const Color(0xffd3dbd1),
        ),
        thumbColor: WidgetStateProperty.all(Colors.white),
        trackOutlineColor: WidgetStateProperty.all(Colors.transparent),
      ),
      progressIndicatorTheme: const ProgressIndicatorThemeData(
        color: AlgaColors.ink,
        linearTrackColor: Color(0xffd3dbd1),
      ),
    ),
    home: const LandingScreen(),
  );
}
