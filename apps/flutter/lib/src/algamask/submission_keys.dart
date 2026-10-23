import 'dart:convert';
import 'dart:math';

import 'package:shared_preferences/shared_preferences.dart';

/// Convenience recovery on this device; the server enforces key uniqueness.
class SubmissionKeys {
  late final SharedPreferencesAsync preferences = SharedPreferencesAsync();
  String storageKey(String host, String body) =>
      'algamask.pending.$host.${base64Url.encode(utf8.encode(body))}';
  Future<String> keyFor(String host, String body) async {
    final slot = storageKey(host, body);
    final existing = await preferences.getString(slot);
    if (existing != null) return existing;
    final random = Random.secure();
    final key = List.generate(
      24,
      (_) => random.nextInt(256).toRadixString(16).padLeft(2, '0'),
    ).join();
    await preferences.setString(slot, key);
    return key;
  }

  Future<void> complete(String host, String body) =>
      preferences.remove(storageKey(host, body));
}
