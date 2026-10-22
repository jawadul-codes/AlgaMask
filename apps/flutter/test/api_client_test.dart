import 'dart:convert';

import 'package:algamask/src/algamask/api_client.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;
import 'package:http/testing.dart';

void main() {
  test(
    'POST /runs with exact payload; report shares configured host',
    () async {
      final client = ApiClient(
        baseUrl: 'http://localhost:8123',
        client: MockClient((request) async {
          expect(request.url.path, '/runs');
          expect(request.method, 'POST');
          expect(jsonDecode(request.body), {
            'algae': 'blend',
            'max_sugar_g': 5,
          });
          return http.Response(
            jsonEncode({
              'run_id': 'abc',
              'status': 'insufficient_data',
              'mode': 'rag_development',
              'trace': [],
              'formulations': [],
              'controls': [],
              'evidence': [],
              'limitations': [],
              'impact': {},
            }),
            200,
          );
        }),
      );
      final result = await client.run({'algae': 'blend', 'max_sugar_g': 5});
      expect(result['status'], 'insufficient_data');
      expect(
        client.reportUrl('abc').toString(),
        'http://localhost:8123/runs/abc/report',
      );
      client.close();
    },
  );
  for (final status in [422, 503]) {
    test('HTTP $status is not a successful report', () async {
      final client = ApiClient(
        client: MockClient((_) async => http.Response('{}', status)),
      );
      await expectLater(client.run({}), throwsException);
      client.close();
    });
  }
  test('legacy preview response is rejected', () async {
    final client = ApiClient(
      client: MockClient((_) async => http.Response('{}', 200)),
    );
    await expectLater(client.run({}), throwsFormatException);
    client.close();
  });
}
