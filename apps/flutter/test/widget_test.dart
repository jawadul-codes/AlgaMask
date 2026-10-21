import 'package:algamask/main.dart';
import 'package:algamask/src/algamask/api_client.dart';
import 'package:algamask/src/algamask/input_screen.dart';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';

class FailingClient extends ApiClient {
  @override
  Future<Map<String, dynamic>> run(Map<String, dynamic> input) async =>
      throw Exception('offline');
}

class SuccessfulClient extends ApiClient {
  @override
  Future<Map<String, dynamic>> run(Map<String, dynamic> input) async => {
    'status': 'report_ready',
    'trace': [
      {'agent': 'Profile', 'state': 'PROFILED', 'summary': 'Profile ready', 'status': 'mock'},
    ],
    'sensory_map': [
      {'category': 'Bitter', 'relative_risk': 0.6},
    ],
    'evidence': [
      {'title': 'Synthetic evidence example', 'status': 'assumed for demo'},
    ],
    'formulations': [
      {'name': 'Cocoa concept', 'total_g': 45, 'ingredients': []},
    ],
    'controls': [
      {'id': 'B0'}, {'id': 'A0'},
    ],
    'impact': {'nutrition_change_pct': null, 'sensory_change_pct': null},
    'limitations': ['Mock run only.'],
  };
}

void main() {
  testWidgets('form fits phone width', (tester) async {
    tester.view.physicalSize = const Size(390, 844);
    tester.view.devicePixelRatio = 1;
    addTearDown(tester.view.resetPhysicalSize);
    addTearDown(tester.view.resetDevicePixelRatio);
    await tester.pumpWidget(const AlgaMaskApp());
    expect(find.text('AlgaMask'), findsOneWidget);
    expect(find.text('DAY 1'), findsOneWidget);
    expect(tester.takeException(), isNull);
  });
  testWidgets('failed request releases loading state for retry', (
    tester,
  ) async {
    await tester.pumpWidget(
      MaterialApp(home: InputScreen(client: FailingClient())),
    );
    final button = find.text('Run Day 1 workflow');
    await tester.ensureVisible(button);
    await tester.tap(button);
    await tester.pumpAndSettle();
    expect(find.textContaining('Could not complete the run'), findsOneWidget);
    expect(button, findsOneWidget);
    expect(find.byType(LinearProgressIndicator), findsNothing);
  });

  testWidgets('shows the structured mock result after a run', (tester) async {
    await tester.pumpWidget(
      MaterialApp(home: InputScreen(client: SuccessfulClient())),
    );
    final button = find.text('Run Day 1 workflow');
    await tester.ensureVisible(button);
    await tester.tap(button);
    await tester.pumpAndSettle();
    expect(find.text('Agent trace'), findsOneWidget);
    expect(find.text('Profile · PROFILED'), findsOneWidget);
    expect(find.text('Evidence placeholders'), findsOneWidget);
    expect(find.textContaining('Controls: B0, A0'), findsOneWidget);
    expect(tester.takeException(), isNull);
  });
}
