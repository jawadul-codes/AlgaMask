import 'dart:async';
import 'dart:convert';

import 'package:algamask/src/algamask/api_client.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;
import 'package:http/testing.dart';

import 'fake_keys.dart';

void main() {
  test(
    'POST /runs with exact payload; report shares configured host',
    () async {
      final client = ApiClient(
        keys: FakeKeys(),
        baseUrl: 'http://localhost:8123',
        client: MockClient((request) async {
          expect(request.url.path, '/runs');
          expect(request.method, 'POST');
          expect(request.headers['Idempotency-Key'], isNotEmpty);
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
        keys: FakeKeys(),
        client: MockClient((_) async => http.Response('{}', status)),
      );
      await expectLater(client.run({}), throwsException);
      client.close();
    });
  }
  test('legacy preview response is rejected', () async {
    final client = ApiClient(
      keys: FakeKeys(),
      client: MockClient((_) async => http.Response('{}', 200)),
    );
    await expectLater(client.run({}), throwsA(isA<ApiFailure>()));
    client.close();
  });
  test(
    'transport retry across client recreation reuses submission key',
    () async {
      final keys = FakeKeys();
      final headers = <String>[];
      final transport = MockClient((request) async {
        headers.add(request.headers['Idempotency-Key']!);
        throw http.ClientException('offline');
      });
      await expectLater(
        ApiClient(keys: keys, client: transport).run({'algae': 'blend'}),
        throwsException,
      );
      await expectLater(
        ApiClient(keys: keys, client: transport).run({'algae': 'blend'}),
        throwsException,
      );
      expect(headers[0], headers[1]);
      expect(keys.issued, 1);
    },
  );
  test('running response preserves key and exposes job', () async {
    final keys = FakeKeys();
    final client = ApiClient(
      keys: keys,
      client: MockClient(
        (_) async => http.Response(
          jsonEncode({
            'job': {'job_id': 'j', 'state': 'running'},
          }),
          202,
        ),
      ),
    );
    await expectLater(
      client.run({}),
      throwsA(
        isA<ApiFailure>().having((e) => e.job!['state'], 'state', 'running'),
      ),
    );
    expect(keys.entries, isNotEmpty);
    client.close();
  });

  for (final response in [
    http.Response('<html>Bad gateway</html>', 502),
    http.Response('not json', 200),
    http.Response('[]', 200),
    http.Response('{"detail":[{"msg":"invalid"}]}', 422),
    http.Response('{"job":null}', 202),
  ]) {
    test('safe failure for ${response.statusCode}: ${response.body}', () async {
      final keys = FakeKeys();
      final client = ApiClient(
        keys: keys,
        client: MockClient((_) async => response),
      );
      await expectLater(client.run({}), throwsA(isA<ApiFailure>()));
      expect(keys.entries, isNotEmpty);
      client.close();
    });
  }

  test(
    'timeout retains original key and does not automatically resubmit',
    () async {
      final keys = FakeKeys();
      final requests = <String>[];
      final client = ApiClient(
        keys: keys,
        writeTimeout: const Duration(milliseconds: 1),
        client: MockClient((request) {
          requests.add(request.headers['Idempotency-Key']!);
          return Completer<http.Response>().future;
        }),
      );
      for (var i = 0; i < 2; i++) {
        await expectLater(
          client.run({}),
          throwsA(
            isA<ApiFailure>().having(
              (e) => e.message,
              'recovery guidance',
              contains('may still be running'),
            ),
          ),
        );
        expect(requests.length, i + 1);
      }
      expect(requests.first, requests.last);
      expect(keys.issued, 1);
      client.close();
    },
  );

  test('offline history has actionable message', () async {
    final client = ApiClient(
      client: MockClient((_) async {
        throw http.ClientException('internal transport details');
      }),
    );
    await expectLater(
      client.history(),
      throwsA(
        isA<ApiFailure>().having(
          (e) => e.message,
          'connection guidance',
          contains('Cannot connect'),
        ),
      ),
    );
    client.close();
  });

  test('malformed history and job shapes are rejected', () async {
    final client = ApiClient(
      client: MockClient((_) async => http.Response('{"runs":[42]}', 200)),
    );
    await expectLater(client.history(), throwsA(isA<ApiFailure>()));
    await expectLater(client.job('j'), throwsA(isA<ApiFailure>()));
    client.close();
  });

  test('retry conflict keeps job details without exposing server internals', () async {
    final client = ApiClient(
      client: MockClient(
        (_) async => http.Response(
          '{"detail":{"message":"internal detail","job":{"state":"running"}}}',
          409,
        ),
      ),
    );
    await expectLater(
      client.retry('j', 1),
      throwsA(
        isA<ApiFailure>()
            .having((e) => e.job?['state'], 'job', 'running')
            .having((e) => e.message, 'guidance', contains('Refresh history')),
      ),
    );
    client.close();
  });
}
