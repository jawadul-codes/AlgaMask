import 'package:algamask/src/algamask/report_view.dart';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_test/flutter_test.dart';

Map<String, dynamic> result(String status) => {
  'run_id': 'test',
  'status': status,
  'mode': 'rag_development',
  'request': {'algae': 'blend'},
  'retrieval': {
    'dataset_version': 'candidate',
    'index_version': 'index',
    'dataset_hash': 'a' * 64,
  },
  'generation': {
    'method': 'extractive',
    'status': 'complete',
    'limitation': 'Exact notes only',
    'claims': [
      {
        'text': 'Source-scoped finding',
        'citation': {'chunk_id': 'C1', 'source_id': 'SRC1'},
      },
    ],
  },
  'trace': [
    {'agent': 'Critic', 'state': 'REJECTED', 'status': 'blocked'},
  ],
  'evidence': [],
  'controls': [],
  'formulations': [],
  'limitations': ['No scientific approval'],
  'impact': {
    'explanation': 'Estimated, not measured',
    'nutrition_change_pct': null,
    'screening': {
      'scope': 'Nine-point grid',
      'verdicts': {
        'S25-1': ['Cannot verify energy: unknown.'],
      },
    },
    'nutrition': {
      'S25-1': {
        'per_serving': {'energy_kcal': null, 'protein_g': 5.5},
        'per_100g': {'energy_kcal': null, 'protein_g': 12.222},
        'missing': {
          'energy_kcal': ['IF-CHL-PWD'],
          'protein_g': [],
        },
        'protein_g_per_100_kcal': null,
        'warnings': ['Development records'],
        'records': [],
      },
    },
  },
};

void main() {
  testWidgets(
    'candidate summary fits a phone and shows missing sugar as unknown',
    (tester) async {
      tester.view.physicalSize = const Size(390, 844);
      tester.view.devicePixelRatio = 1;
      addTearDown(tester.view.resetPhysicalSize);
      addTearDown(tester.view.resetDevicePixelRatio);
      final data = result('report_ready');
      data['request'] = {'serving_g': 45};
      data['interpretation'] = {
        'ingredient_names': {'IF-OAT-DRY': 'Dry oats'},
      };
      data['formulations'] = [
        {
          'id': 'S25-1',
          'total_g': 45,
          'ingredients': [
            {'ingredient_id': 'IF-OAT-DRY', 'grams': 45},
          ],
        },
      ];
      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: SingleChildScrollView(
              child: ReportView(
                result: data,
                reportUri: Uri.parse('http://localhost/report'),
              ),
            ),
          ),
        ),
      );
      expect(find.text('Recipe option found'), findsOneWidget);
      expect(find.text('Total sugar'), findsOneWidget);
      expect(find.text('Unknown'), findsWidgets);
      expect(find.textContaining('Dry oats: 45.00 g'), findsOneWidget);
      expect(tester.takeException(), isNull);
    },
  );

  testWidgets('fixed comparison uses plain names and preserves stored IDs', (
    tester,
  ) async {
    tester.view.physicalSize = const Size(1280, 900);
    tester.view.devicePixelRatio = 1;
    addTearDown(tester.view.resetPhysicalSize);
    addTearDown(tester.view.resetDevicePixelRatio);
    final data = result('report_ready');
    data['request'] = {'experiment': 'spirulina-proof-v1', 'serving_g': 45};
    data['controls'] = [
      {'id': 'B0', 'total_g': 45, 'ingredients': []},
      {'id': 'A0', 'total_g': 45, 'ingredients': []},
    ];
    data['formulations'] = [
      {'id': 'A1', 'total_g': 45, 'ingredients': []},
    ];
    await tester.pumpWidget(
      MaterialApp(
        home: Scaffold(
          body: SingleChildScrollView(
            child: ReportView(
              result: data,
              reportUri: Uri.parse('http://localhost/report'),
            ),
          ),
        ),
      ),
    );
    expect(find.text('Recipe option found'), findsOneWidget);
    expect(find.text('Flavour version'), findsOneWidget);
    await tester.ensureVisible(find.text('How these recipes were compared'));
    await tester.tap(find.text('How these recipes were compared'));
    await tester.pumpAndSettle();
    expect(find.text('Base recipe'), findsWidgets);
    expect(find.text('Algae version'), findsWidgets);
    expect(find.text('B0'), findsOneWidget);
    expect(tester.takeException(), isNull);
  });

  testWidgets('mock result is marked illustrative', (tester) async {
    final data = result('report_ready');
    data['mode'] = 'mock';
    data['formulations'] = [
      {'id': 'S25-1', 'total_g': 45, 'ingredients': []},
    ];
    await tester.pumpWidget(
      MaterialApp(
        home: Scaffold(
          body: SingleChildScrollView(
            child: ReportView(
              result: data,
              reportUri: Uri.parse('http://localhost/report'),
            ),
          ),
        ),
      ),
    );
    expect(find.textContaining('synthetic fixtures'), findsOneWidget);
    expect(find.text('Recipe option found'), findsOneWidget);
    expect(tester.takeException(), isNull);
  });
  testWidgets(
    'candidate report distinguishes controls, precision and background evidence',
    (tester) async {
      final data = result('report_ready');
      data['formulations'] = [
        {
          'id': 'S25-1',
          'name': 'Test candidate',
          'total_g': 45,
          'ingredients': [
            {'ingredient_id': 'IF-COCOA-PWD', 'grams': 0.225},
            {'ingredient_id': 'IF-OAT-DRY', 'grams': 44.775},
          ],
        },
      ];
      data['controls'] = [
        {
          'id': 'B0',
          'name': 'Control',
          'total_g': 45,
          'ingredients': [
            {'ingredient_id': 'IF-OAT-DRY', 'grams': 45},
          ],
        },
      ];
      data['interpretation'] = {
        'ingredient_names': {
          'IF-COCOA-PWD': 'Cocoa powder',
          'IF-OAT-DRY': 'Dry oats',
        },
        'evidence': {
          'C1': {
            'label': 'Related-study background',
            'notes': ['The study does not cover all requested algae species.'],
          },
        },
      };
      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: SingleChildScrollView(
              child: ReportView(
                result: data,
                reportUri: Uri.parse('http://localhost/runs/test/report'),
              ),
            ),
          ),
        ),
      );
      expect(find.text('Recipe option found'), findsOneWidget);
      expect(find.text('Recipe option 1'), findsOneWidget);
      expect(find.text('Total sugar'), findsOneWidget);
      expect(find.text('Unknown'), findsWidgets);
      expect(find.text('Base recipe'), findsNothing);
      await tester.ensureVisible(find.text('How these recipes were compared'));
      await tester.tap(find.text('How these recipes were compared'));
      await tester.pumpAndSettle();
      expect(
        find.textContaining('targets apply to candidates only'),
        findsOneWidget,
      );
      expect(find.text('Cocoa powder 0.2250 g'), findsOneWidget);
      await tester.ensureVisible(
        find.text('Sources and what they can tell us'),
      );
      await tester.tap(find.text('Sources and what they can tell us'));
      await tester.pumpAndSettle();
      expect(find.text('Evidence context and limits'), findsOneWidget);
      expect(find.text('Related-study background'), findsOneWidget);
      expect(
        find.textContaining('The study does not cover all requested'),
        findsOneWidget,
      );
      expect(tester.takeException(), isNull);
    },
  );
  testWidgets('denied clipboard write shows recovery feedback', (tester) async {
    tester.binding.defaultBinaryMessenger.setMockMethodCallHandler(
      SystemChannels.platform,
      (call) async {
        if (call.method == 'Clipboard.setData') {
          throw PlatformException(code: 'denied');
        }
        return null;
      },
    );
    addTearDown(
      () => tester.binding.defaultBinaryMessenger.setMockMethodCallHandler(
        SystemChannels.platform,
        null,
      ),
    );
    await tester.pumpWidget(
      MaterialApp(
        home: Scaffold(
          body: SingleChildScrollView(
            child: ReportView(
              result: result('report_ready'),
              reportUri: Uri.parse('http://localhost/runs/test/report'),
            ),
          ),
        ),
      ),
    );
    await tester.ensureVisible(find.text('Full research details'));
    await tester.tap(find.text('Full research details'));
    await tester.pumpAndSettle();
    await tester.ensureVisible(find.text('Copy run JSON'));
    await tester.tap(find.text('Copy run JSON'));
    await tester.pumpAndSettle();
    expect(find.textContaining('Could not copy the report'), findsOneWidget);
    expect(find.text('Run JSON copied.'), findsNothing);
    expect(tester.takeException(), isNull);
  });
  for (final status in [
    'report_ready',
    'insufficient_data',
    'generation_failed',
  ]) {
    testWidgets('$status report renders on phone with unknown nutrients', (
      tester,
    ) async {
      tester.view.physicalSize = const Size(390, 844);
      tester.view.devicePixelRatio = 1;
      addTearDown(tester.view.resetPhysicalSize);
      addTearDown(tester.view.resetDevicePixelRatio);
      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: SingleChildScrollView(
              child: ReportView(
                result: result(status),
                reportUri: Uri.parse('http://localhost:8000/runs/test/report'),
              ),
            ),
          ),
        ),
      );
      expect(
        find.text(
          status == 'generation_failed'
              ? 'We couldn’t verify this result'
              : 'No recipe met your choices',
        ),
        findsOneWidget,
      );
      await tester.ensureVisible(
        find.text('Sources and what they can tell us'),
      );
      await tester.tap(find.text('Sources and what they can tell us'));
      await tester.pumpAndSettle();
      expect(
        find.text('Source-scoped finding'),
        status == 'generation_failed' ? findsNothing : findsOneWidget,
      );
      await tester.ensureVisible(find.text('Nutrition details'));
      await tester.tap(find.text('Nutrition details'));
      await tester.pumpAndSettle();
      final tile = find.text('S25-1 (S25-1) · composition estimate');
      await tester.ensureVisible(tile);
      await tester.tap(tile);
      await tester.pumpAndSettle();
      expect(find.text('energy_kcal: unknown per serving'), findsOneWidget);
      expect(find.textContaining('IF-CHL-PWD'), findsOneWidget);
      await tester.ensureVisible(find.text('Screening checks').first);
      await tester.tap(find.text('Screening checks').first);
      await tester.pumpAndSettle();
      expect(find.textContaining('Cannot verify energy'), findsOneWidget);
      expect(tester.takeException(), isNull);
    });
  }
}
