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
  Map<String, dynamic>? submitted;
  @override
  Future<Map<String, dynamic>> run(Map<String, dynamic> input) async {
    submitted = input;
    return {
      'run_id': 'test-run',
      'status': 'report_ready',
      'mode': 'rag_development',
      'request': input,
      'trace': [],
      'controls': [],
      'formulations': [],
      'limitations': ['Test limitation'],
      'impact': {
        'explanation': 'Source-traceable estimates',
        'nutrition_change_pct': null,
      },
      'evidence': [
        {
          'source_title': 'Real source shape',
          'chunk_id': 'C1',
          'source_id': 'SRC1',
          'claim_summary': 'Extracted context',
          'review_status': 'extracted',
        },
      ],
    };
  }
}

void main() {
  testWidgets('fixed proof submits exact settings and keeps constraints', (
    tester,
  ) async {
    final client = SuccessfulClient();
    await tester.pumpWidget(MaterialApp(home: InputScreen(client: client)));
    await tester.tap(find.byType(SwitchListTile));
    await tester.pumpAndSettle();
    expect(find.byType(Slider), findsNothing);
    expect(find.textContaining('45 g ingredient input'), findsOneWidget);
    await tester.enterText(find.byType(TextFormField).first, '5');
    final button = find.text('Run experiment');
    await tester.ensureVisible(button);
    await tester.tap(button);
    await tester.pumpAndSettle();
    expect(client.submitted!['experiment'], 'spirulina-proof-v1');
    expect(client.submitted!['algae'], 'spirulina');
    expect(client.submitted!['inclusion_pct'], 2);
    expect(client.submitted!['serving_g'], 45);
    expect(client.submitted!['flavour'], 'cocoa-spice');
    expect(client.submitted!['min_protein_g'], 5);
    expect(tester.takeException(), isNull);
  });
  testWidgets('form fits phone width', (tester) async {
    tester.view.physicalSize = const Size(390, 844);
    tester.view.devicePixelRatio = 1;
    addTearDown(tester.view.resetPhysicalSize);
    addTearDown(tester.view.resetDevicePixelRatio);
    await tester.pumpWidget(const AlgaMaskApp());
    expect(find.text('AlgaMask'), findsOneWidget);
    expect(find.text('Design an algae-bar experiment'), findsOneWidget);
    expect(tester.takeException(), isNull);
  });
  testWidgets('failed request releases loading state for retry', (
    tester,
  ) async {
    await tester.pumpWidget(
      MaterialApp(home: InputScreen(client: FailingClient())),
    );
    final button = find.text('Run experiment');
    await tester.ensureVisible(button);
    await tester.tap(button);
    await tester.pumpAndSettle();
    expect(find.textContaining('Could not complete the run'), findsOneWidget);
    expect(button, findsOneWidget);
    expect(find.byType(LinearProgressIndicator), findsNothing);
  });

  testWidgets('submits runs contract and displays real evidence shape', (
    tester,
  ) async {
    final client = SuccessfulClient();
    await tester.pumpWidget(MaterialApp(home: InputScreen(client: client)));
    await tester.enterText(find.byType(TextFormField).first, '5');
    final button = find.text('Run experiment');
    await tester.ensureVisible(button);
    await tester.tap(button);
    await tester.pumpAndSettle();
    expect(client.submitted!['min_protein_g'], 5);
    expect(client.submitted!['serving_g'], 45);
    expect(client.submitted!.containsKey('max_sugar_g'), isFalse);
    expect(find.text('Your experimental report'), findsOneWidget);
    expect(find.text('LOCAL RAG · development data'), findsOneWidget);
    expect(find.text('Real source shape'), findsOneWidget);
    expect(tester.takeException(), isNull);
  });

  testWidgets('invalid target prevents a request', (tester) async {
    final client = SuccessfulClient();
    await tester.pumpWidget(MaterialApp(home: InputScreen(client: client)));
    await tester.enterText(find.byType(TextFormField).first, 'NaN');
    final button = find.text('Run experiment');
    await tester.ensureVisible(button);
    await tester.tap(button);
    await tester.pumpAndSettle();
    expect(client.submitted, isNull);
    expect(find.textContaining('or leave blank'), findsOneWidget);
  });
}
