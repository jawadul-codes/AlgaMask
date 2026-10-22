import 'dart:convert';

import 'package:http/http.dart' as http;

const apiBase = String.fromEnvironment(
  'API_BASE_URL',
  defaultValue: 'http://127.0.0.1:8000',
);

class ApiClient {
  ApiClient({http.Client? client, this.baseUrl = apiBase})
    : _client = client ?? http.Client();
  final http.Client _client;
  final String baseUrl;
  Uri reportUrl(String id) =>
      Uri.parse('$baseUrl/runs/${Uri.encodeComponent(id)}/report');
  void close() => _client.close();
  Future<Map<String, dynamic>> run(Map<String, dynamic> input) async {
    final response = await _client
        .post(
          Uri.parse('$baseUrl/runs'),
          headers: {'Content-Type': 'application/json'},
          body: jsonEncode(input),
        )
        .timeout(const Duration(seconds: 120));
    if (response.statusCode != 200) {
      throw Exception('Request failed (${response.statusCode}).');
    }
    final result = jsonDecode(response.body) as Map<String, dynamic>;
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
}
