import 'dart:async';

import 'package:algamask/src/algamask/api_client.dart';
import 'package:algamask/src/algamask/input_screen.dart';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';

class FailingClient extends ApiClient {
  @override
  Future<Map<String, dynamic>> preflight(Map<String, dynamic> input) async => {
    'can_run': true,
    'messages': [],
    'margins': {},
    'notes': [],
  };
  @override
  Future<Map<String, dynamic>> run(Map<String, dynamic> input) async =>
      throw Exception('offline');
}

class SuccessfulClient extends ApiClient {
  Map<String, dynamic>? submitted;
  @override
  Future<Map<String, dynamic>> preflight(Map<String, dynamic> input) async => {
    'can_run': true,
    'messages': [],
    'margins': {},
    'notes': [],
  };
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

class PendingClient extends SuccessfulClient {
  final checks = <Completer<Map<String, dynamic>>>[];
  @override
  Future<Map<String, dynamic>> preflight(Map<String, dynamic> input) {
    final pending = Completer<Map<String, dynamic>>();
    checks.add(pending);
    return pending.future;
  }
}

class ExclusionClient extends SuccessfulClient {
  Map<String, dynamic>? checked;
  @override
  Future<Map<String, dynamic>> preflight(Map<String, dynamic> input) async {
    checked = input;
    final blocked =
        (input['exclusions'] as List).isNotEmpty &&
        input['exclusion_mode'] == 'verified_free_from';
    return {
      'can_run': !blocked,
      'messages': blocked ? ['Supplier verification is missing.'] : [],
      'margins': {},
      'notes': [],
    };
  }
}

void main() {
  testWidgets('new experiment from history clears the previous report', (
    tester,
  ) async {
    final client = SuccessfulClient();
    await tester.pumpWidget(MaterialApp(home: InputScreen(client: client)));
    await tester.pumpAndSettle(const Duration(milliseconds: 400));
    await tester.ensureVisible(find.text('Run screening'));
    await tester.tap(find.text('Run screening'));
    await tester.pumpAndSettle();
    expect(find.text('Screening report'), findsOneWidget);
    await tester.tap(find.byTooltip('Experiment history'));
    await tester.pumpAndSettle();
    await tester.tap(find.byTooltip('New experiment'));
    await tester.pumpAndSettle(const Duration(milliseconds: 400));
    expect(find.text('Design a better algae bar'), findsOneWidget);
    expect(find.text('Screening report'), findsNothing);
  });
  testWidgets(
    'exclusion modes are explicit, recheck and appear on saved report',
    (tester) async {
      final client = ExclusionClient();
      await tester.pumpWidget(MaterialApp(home: InputScreen(client: client)));
      final chip = find.widgetWithText(FilterChip, 'tree nut');
      await tester.ensureVisible(chip);
      await tester.tap(chip);
      await tester.pumpAndSettle(const Duration(milliseconds: 400));
      expect(client.checked!['exclusions'], ['tree_nut']);
      expect(client.checked!['exclusion_mode'], 'ingredient_preference');
      final button = find.widgetWithText(FilledButton, 'Run screening');
      expect(tester.widget<FilledButton>(button).onPressed, isNotNull);
      final dropdown = find.byKey(const Key('exclusion-mode'));
      await tester.ensureVisible(dropdown);
      await tester.tap(dropdown);
      await tester.pumpAndSettle();
      await tester.tap(find.text('Require verified free-from').last);
      await tester.pumpAndSettle(const Duration(milliseconds: 400));
      expect(client.checked!['exclusion_mode'], 'verified_free_from');
      expect(tester.widget<FilledButton>(button).onPressed, isNull);
      await tester.ensureVisible(dropdown);
      await tester.tap(dropdown);
      await tester.pumpAndSettle();
      await tester.tap(find.text('Omit ingredients (preference)').last);
      await tester.pumpAndSettle(const Duration(milliseconds: 400));
      await tester.ensureVisible(button);
      await tester.tap(button);
      await tester.pumpAndSettle();
      expect(client.submitted!['exclusion_mode'], 'ingredient_preference');
      expect(
        find.textContaining(
          'Ingredient preferences (allergy safety not verified): tree nut',
        ),
        findsOneWidget,
      );
      expect(tester.takeException(), isNull);
    },
  );
  testWidgets('blocked and stale checks never submit a run; edits recheck', (
    tester,
  ) async {
    final client = PendingClient();
    await tester.pumpWidget(MaterialApp(home: InputScreen(client: client)));
    await tester.pump(const Duration(milliseconds: 400));
    await tester.enterText(find.byType(TextFormField).first, '12');
    await tester.pump(const Duration(milliseconds: 400));
    client.checks[1].complete({
      'can_run': false,
      'messages': ['Protein maximum 5.01 g; adjust target.'],
      'margins': {},
      'notes': [],
    });
    await tester.pump();
    client.checks[0].complete({
      'can_run': true,
      'messages': [],
      'margins': {},
      'notes': [],
    });
    await tester.pump();
    expect(find.textContaining('Protein maximum'), findsOneWidget);
    final button = find.widgetWithText(FilledButton, 'Run screening');
    expect(tester.widget<FilledButton>(button).onPressed, isNull);
    expect(client.submitted, isNull);
    await tester.enterText(find.byType(TextFormField).first, '5');
    await tester.pump(const Duration(milliseconds: 400));
    client.checks[2].complete({
      'can_run': true,
      'messages': [],
      'margins': {},
      'notes': [],
    });
    await tester.pump();
    expect(tester.widget<FilledButton>(button).onPressed, isNotNull);
  });
  testWidgets('fixed proof submits exact settings and keeps constraints', (
    tester,
  ) async {
    final client = SuccessfulClient();
    await tester.pumpWidget(MaterialApp(home: InputScreen(client: client)));
    await tester.ensureVisible(find.byType(SwitchListTile));
    await tester.tap(find.byType(SwitchListTile));
    await tester.pumpAndSettle();
    expect(find.byType(Slider), findsNothing);
    expect(find.textContaining('45 g ingredient input'), findsWidgets);
    await tester.enterText(find.byType(TextFormField).first, '5');
    await tester.pumpAndSettle(const Duration(milliseconds: 400));
    final button = find.text('Run screening');
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
    await tester.pumpWidget(
      MaterialApp(home: InputScreen(client: SuccessfulClient())),
    );
    await tester.pumpAndSettle(const Duration(milliseconds: 400));
    expect(find.text('AlgaMask'), findsOneWidget);
    expect(find.text('Design a better algae bar'), findsOneWidget);
    expect(tester.takeException(), isNull);
  });
  testWidgets('failed request releases loading state for retry', (
    tester,
  ) async {
    await tester.pumpWidget(
      MaterialApp(home: InputScreen(client: FailingClient())),
    );
    await tester.pumpAndSettle(const Duration(milliseconds: 400));
    final button = find.text('Run screening');
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
    await tester.pumpAndSettle(const Duration(milliseconds: 400));
    final button = find.text('Run screening');
    await tester.ensureVisible(button);
    await tester.tap(button);
    await tester.pumpAndSettle();
    expect(client.submitted!['min_protein_g'], 5);
    expect(client.submitted!['serving_g'], 45);
    expect(client.submitted!.containsKey('max_sugar_g'), isFalse);
    expect(find.text('Screening report'), findsOneWidget);
    expect(find.textContaining('LOCAL RAG · development data'), findsOneWidget);
    expect(find.textContaining('Real source shape'), findsOneWidget);
    expect(tester.takeException(), isNull);
  });

  testWidgets('invalid target prevents a request', (tester) async {
    final client = SuccessfulClient();
    await tester.pumpWidget(MaterialApp(home: InputScreen(client: client)));
    await tester.enterText(find.byType(TextFormField).first, 'NaN');
    await tester.pumpAndSettle(const Duration(milliseconds: 400));
    final button = find.text('Run screening');
    await tester.ensureVisible(button);
    await tester.tap(button);
    await tester.pumpAndSettle();
    expect(client.submitted, isNull);
    expect(find.textContaining('or leave blank'), findsOneWidget);
  });
}
