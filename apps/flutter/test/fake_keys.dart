import 'package:algamask/src/algamask/submission_keys.dart';

class FakeKeys extends SubmissionKeys {
  final Map<String, String> entries = {};
  int issued = 0;
  @override
  Future<String> keyFor(String host, String body) async => entries.putIfAbsent(
    '$host/$body',
    () => 'test-submission-${issued++}'.padRight(24, '0'),
  );
  @override
  Future<void> complete(String host, String body) async {
    entries.remove('$host/$body');
  }
}
