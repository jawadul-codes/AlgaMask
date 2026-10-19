import 'dart:convert';

import 'package:http/http.dart' as http;

const apiBase = String.fromEnvironment(
  'API_BASE_URL',
  defaultValue: 'http://127.0.0.1:8000',
);

class ApiClient {
  Future<Map<String, dynamic>> run(Map<String, dynamic> input) async {
    final response = await http
        .post(
          Uri.parse('$apiBase/runs'),
          headers: {'Content-Type': 'application/json'},
          body: jsonEncode(input),
        )
        .timeout(const Duration(seconds: 20));
    if (response.statusCode != 200) {
      throw Exception('Request failed (${response.statusCode}).');
    }
    return jsonDecode(response.body) as Map<String, dynamic>;
  }
}
