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
    final button = find.text('Show placeholder');
    await tester.ensureVisible(button);
    await tester.tap(button);
    await tester.pumpAndSettle();
    expect(find.textContaining('Could not complete the run'), findsOneWidget);
    expect(button, findsOneWidget);
    expect(find.byType(LinearProgressIndicator), findsNothing);
  });
}
