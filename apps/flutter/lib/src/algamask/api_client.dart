import 'dart:async';
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
  ApiClient({
    http.Client? client,
    this.baseUrl = apiBase,
    SubmissionKeys? keys,
    this.readTimeout = const Duration(seconds: 15),
    this.writeTimeout = const Duration(seconds: 120),
  }) : _client = client ?? http.Client(),
       _keys = keys ?? SubmissionKeys();
  final http.Client _client;
  final SubmissionKeys _keys;
  final Map<String, Future<Map<String, dynamic>>> _active = {};
  final String baseUrl;
  final Duration readTimeout, writeTimeout;

  Future<http.Response> _send(
    Future<http.Response> Function() request, {
    bool write = false,
  }) async {
    try {
      return await request().timeout(write ? writeTimeout : readTimeout);
    } on TimeoutException {
      throw ApiFailure(
        write
            ? 'The backend took too long to respond. Your experiment may still be running. Check history first, or retry with the same inputs.'
            : 'The backend took too long to respond. Please try again.',
      );
    } on http.ClientException {
      throw ApiFailure(
        'Cannot connect to the backend at $baseUrl. Check that it is running and the address is correct. For a submitted experiment, check history or retry with the same inputs.',
      );
    }
  }

  ApiFailure _unexpected() => ApiFailure(
    'The backend returned an unreadable or unexpected response. Check that the app and backend versions match. Check history before retrying with the same inputs.',
  );

  Map<String, dynamic> _decode(http.Response response) {
    Map<String, dynamic>? data;
    try {
      final decoded = jsonDecode(response.body);
      if (decoded is Map<String, dynamic>) data = decoded;
    } on FormatException {
      // Proxy error pages are often HTML, not API JSON.
    }
    if (response.statusCode != 200 && response.statusCode != 202) {
      final detail = data?['detail'];
      if (response.statusCode == 422 &&
          detail is Map &&
          detail['code'] == 'configuration_blocked' &&
          detail['preflight'] is Map) {
        final reasons = detail['preflight']['messages'];
        throw ApiFailure(
          'Adjust the configuration before running. ${reasons is List ? reasons.join(' ') : ''}',
        );
      }
      final message = switch (response.statusCode) {
        404 => 'This saved experiment could not be found. Refresh history.',
        409 =>
          'The experiment state has changed. Refresh history before retrying.',
        422 => 'Some inputs or filters are invalid. Check their values and try again.',
        429 => 'The backend is busy. Wait briefly, then check history before retrying.',
        >= 500 => 'The backend could not complete this request. Check history before retrying with the same inputs.',
        _ =>
          'Request failed (${response.statusCode}). Please check your connection and inputs.',
      };
      throw ApiFailure(
        message,
        job: detail is Map && detail['job'] is Map<String, dynamic>
            ? detail['job'] as Map<String, dynamic>
            : null,
      );
    }
    if (data == null) throw _unexpected();
    return data;
  }

  Uri reportUrl(String id) =>
      Uri.parse('$baseUrl/runs/${Uri.encodeComponent(id)}/report');
  void close() => _client.close();
  Future<Map<String, dynamic>> preflight(Map<String, dynamic> input) async {
    final response = await _send(
      () => _client.post(
        Uri.parse('$baseUrl/runs/preflight'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode(input),
      ),
    );
    final data = _decode(response);
    if (response.statusCode != 200 ||
        data['can_run'] is! bool ||
        data['messages'] is! List ||
        data['margins'] is! Map ||
        data['notes'] is! List) {
      throw _unexpected();
    }
    return data;
  }

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
    final response = await _send(
      () => _client.post(
        Uri.parse('$baseUrl/runs'),
        headers: {'Content-Type': 'application/json', 'Idempotency-Key': key},
        body: body,
      ),
      write: true,
    );
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
    final data = _decode(response);
    if (response.statusCode == 202) {
      throw ApiFailure(
        'Your experiment is still running. Open history to check its progress.',
        job: data['job'] is Map<String, dynamic>
            ? data['job'] as Map<String, dynamic>
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
      throw _unexpected();
    }
    return result;
  }

  Future<Map<String, dynamic>> loadRun(String id) async => decodeRun(
    await _send(
      () => _client.get(Uri.parse('$baseUrl/runs/${Uri.encodeComponent(id)}')),
    ),
  );

  Future<Map<String, dynamic>> job(String id) async {
    final response = await _send(
      () => _client.get(Uri.parse('$baseUrl/jobs/${Uri.encodeComponent(id)}')),
    );
    final data = _decode(response);
    if (response.statusCode != 200 || data['state'] is! String) {
      throw _unexpected();
    }
    return data;
  }

  Future<Map<String, dynamic>> retry(String id, int attempt) async => decodeRun(
    await _send(
      () => _client.post(
        Uri.parse('$baseUrl/jobs/${Uri.encodeComponent(id)}/retry'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({'expected_attempt': attempt}),
      ),
      write: true,
    ),
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
    final response = await _send(() => _client.get(uri));
    final data = _decode(response);
    if (response.statusCode != 200 ||
        data['runs'] is! List ||
        (data['runs'] as List).any((row) => row is! Map<String, dynamic>)) {
      throw _unexpected();
    }
    return (data['runs'] as List)
        .map((item) => Map<String, dynamic>.from(item))
        .toList();
  }
}
