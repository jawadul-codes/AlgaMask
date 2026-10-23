import 'dart:convert';

import 'package:http/http.dart' as http;

import 'submission_keys.dart';

class ApiFailure implements Exception {
  ApiFailure(this.message, {this.job});
  final String message;
  final Map<String, dynamic>? job;
  @override
  String toString() => message;
}

const apiBase = String.fromEnvironment(
  'API_BASE_URL',
  defaultValue: 'http://127.0.0.1:8000',
);

class ApiClient {
  ApiClient({http.Client? client, this.baseUrl = apiBase, SubmissionKeys? keys})
    : _client = client ?? http.Client(),
      _keys = keys ?? SubmissionKeys();
  final http.Client _client;
  final SubmissionKeys _keys;
  final Map<String, Future<Map<String, dynamic>>> _active = {};
  final String baseUrl;
  Uri reportUrl(String id) =>
      Uri.parse('$baseUrl/runs/${Uri.encodeComponent(id)}/report');
  void close() => _client.close();
  Future<Map<String, dynamic>> run(Map<String, dynamic> input) {
    final normalized = Map<String, dynamic>.from(input);
    if (normalized['exclusions'] is List) {
      normalized['exclusions'] = (List<String>.from(
        normalized['exclusions'],
      ).toSet().toList()..sort());
    }
    final names = normalized.keys.toList()..sort();
    final body = jsonEncode({for (final name in names) name: normalized[name]});
    return _active.putIfAbsent(
      body,
      () => _submit(body).whenComplete(() {
        _active.remove(body);
      }),
    );
  }

  Future<Map<String, dynamic>> _submit(String body) async {
    final key = await _keys.keyFor(baseUrl, body);
    final response = await _client
        .post(
          Uri.parse('$baseUrl/runs'),
          headers: {'Content-Type': 'application/json', 'Idempotency-Key': key},
          body: body,
        )
        .timeout(const Duration(seconds: 120));
    final result = decodeRun(response);
    // Keep the key for queued/running/failed responses and transport timeouts.
    // Cleanup failure must not hide an already saved result.
    try {
      await _keys.complete(baseUrl, body);
    } catch (_) {
      /* History can still reopen the saved run. */
    }
    return result;
  }

  Map<String, dynamic> decodeRun(http.Response response) {
    final data = jsonDecode(response.body) as Map<String, dynamic>;
    if (response.statusCode == 202) {
      throw ApiFailure(
        'Your experiment is still running. Open history to check its progress.',
        job: Map<String, dynamic>.from(data['job']),
      );
    }
    if (response.statusCode != 200) {
      final detail = data['detail'];
      throw ApiFailure(
        detail is Map
            ? '${detail['message'] ?? 'Request failed. Please retry.'}'
            : 'Request failed (${response.statusCode}).',
        job: detail is Map && detail['job'] is Map
            ? Map<String, dynamic>.from(detail['job'])
            : null,
      );
    }
    final result = data;
    if (result['run_id'] is! String ||
        ![
          'report_ready',
          'insufficient_data',
          'generation_failed',
        ].contains(result['status']) ||
        !['mock', 'rag_development', 'rag'].contains(result['mode']) ||
        [
          'trace',
          'formulations',
          'controls',
          'evidence',
          'limitations',
        ].any((key) => result[key] is! List) ||
        result['impact'] is! Map) {
      throw const FormatException('Unexpected run response');
    }
    return result;
  }

  Future<Map<String, dynamic>> loadRun(String id) async => decodeRun(
    await _client
        .get(Uri.parse('$baseUrl/runs/${Uri.encodeComponent(id)}'))
        .timeout(const Duration(seconds: 15)),
  );

  Future<Map<String, dynamic>> job(String id) async {
    final response = await _client
        .get(Uri.parse('$baseUrl/jobs/${Uri.encodeComponent(id)}'))
        .timeout(const Duration(seconds: 15));
    if (response.statusCode != 200) {
      throw ApiFailure('Could not load execution details.');
    }
    return jsonDecode(response.body) as Map<String, dynamic>;
  }

  Future<Map<String, dynamic>> retry(String id, int attempt) async => decodeRun(
    await _client
        .post(
          Uri.parse('$baseUrl/jobs/${Uri.encodeComponent(id)}/retry'),
          headers: {'Content-Type': 'application/json'},
          body: jsonEncode({'expected_attempt': attempt}),
        )
        .timeout(const Duration(seconds: 120)),
  );

  Future<List<Map<String, dynamic>>> history({
    int offset = 0,
    String? status,
    String? algae,
    String? since,
    String? until,
  }) async {
    final uri = Uri.parse('$baseUrl/runs').replace(
      queryParameters: {
        'limit': '20',
        'offset': '$offset',
        'status': ?status,
        'algae': ?algae,
        'since': ?since,
        'until': ?until,
      },
    );
    final response = await _client
        .get(uri)
        .timeout(const Duration(seconds: 15));
    if (response.statusCode != 200) {
      throw ApiFailure(
        'Could not load history. Check the connection and date range.',
      );
    }
    final data = jsonDecode(response.body) as Map<String, dynamic>;
    return (data['runs'] as List)
        .map((item) => Map<String, dynamic>.from(item))
        .toList();
  }
}
