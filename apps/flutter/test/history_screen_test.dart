import 'package:algamask/src/algamask/api_client.dart';
import 'package:algamask/src/algamask/history_screen.dart';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';

class HistoryClient extends ApiClient {
  String? requestedStatus;
  int requestedOffset = 0;
  int? retriedAttempt;
  bool fail = false;
  @override
  Future<List<Map<String, dynamic>>> history({
    int offset = 0,
    String? status,
    String? algae,
    String? since,
    String? until,
  }) async {
    requestedStatus = status;
    requestedOffset = offset;
    if (fail) throw ApiFailure('History offline');
    if (offset > 0) return [];
    return List.generate(
      20,
      (i) => {
        'run_id': '$i',
        'created_at': '2026-10-23',
        'status': i == 0 ? 'failed' : 'report_ready',
        'state': i == 0 ? 'failed' : 'completed',
        'algae': 'spirulina',
        'attempt': 1,
      },
    );
  }

  Map<String, dynamic> report() => {
    'run_id': '1',
    'status': 'report_ready',
    'mode': 'mock',
    'request': {},
    'impact': {'explanation': 'Saved estimate'},
    'controls': [],
    'formulations': [],
    'evidence': [],
    'trace': [],
    'limitations': [],
  };
  @override
  Future<Map<String, dynamic>> loadRun(String id) async => report();
  @override
  Future<Map<String, dynamic>> job(String id) async => {
    'job_id': id,
    'state': 'failed',
    'attempt': 2,
    'error_code': 'run_failed',
    'attempts': [],
  };
  @override
  Future<Map<String, dynamic>> retry(String id, int attempt) async {
    retriedAttempt = attempt;
    return {...report(), 'run_id': id};
  }
}

void main() {
  testWidgets('reopens stored report and retries the displayed attempt', (
    tester,
  ) async {
    final client = HistoryClient();
    await tester.pumpWidget(MaterialApp(home: HistoryScreen(client: client)));
    await tester.pumpAndSettle();
    await tester.tap(find.text('spirulina · report ready').first);
    await tester.pumpAndSettle();
    expect(find.text('Screening report'), findsOneWidget);
    await tester.tap(find.text('Experiment history').first);
    await tester.pumpAndSettle();
    await tester.ensureVisible(find.text('spirulina · failed'));
    await tester.tap(find.text('spirulina · failed'));
    await tester.pumpAndSettle();
    final retry = find.text('Retry saved experiment');
    await tester.ensureVisible(retry);
    await tester.tap(retry);
    await tester.pumpAndSettle();
    expect(client.retriedAttempt, 2);
    expect(find.text('spirulina · failed'), findsNothing);
    expect(find.text('Screening report'), findsOneWidget);
  });
  testWidgets('pagination and history error remain recoverable', (
    tester,
  ) async {
    final client = HistoryClient();
    await tester.pumpWidget(MaterialApp(home: HistoryScreen(client: client)));
    await tester.pumpAndSettle();
    await tester.ensureVisible(find.text('Next'));
    await tester.tap(find.text('Next'));
    await tester.pumpAndSettle();
    expect(client.requestedOffset, 20);
    expect(find.text('No experiments match these filters.'), findsOneWidget);
    client.fail = true;
    await tester.ensureVisible(find.text('Refresh history'));
    await tester.tap(find.text('Refresh history'));
    await tester.pumpAndSettle();
    expect(find.text('History offline'), findsOneWidget);
  });
}
