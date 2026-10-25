import 'package:flutter/material.dart';

import 'api_client.dart';
import 'design.dart';
import 'report_view.dart';

class HistoryScreen extends StatefulWidget {
  const HistoryScreen({super.key, required this.client});
  final ApiClient client;
  @override
  State<HistoryScreen> createState() => _HistoryScreenState();
}

class _HistoryScreenState extends State<HistoryScreen> {
  List<Map<String, dynamic>> rows = [];
  Map<String, dynamic>? selected, execution;
  bool loading = false;
  String? error, status, algae;
  int offset = 0;
  DateTimeRange? dates;

  @override
  void initState() {
    super.initState();
    refresh();
  }

  Future<void> refresh({int page = 0}) async {
    setState(() {
      loading = true;
      error = null;
      selected = null;
      execution = null;
    });
    try {
      final data = await widget.client.history(
        offset: page,
        status: status,
        algae: algae,
        since: dates?.start.toIso8601String().split('T').first,
        until: dates?.end.toIso8601String().split('T').first,
      );
      if (mounted) {
        setState(() {
          rows = data;
          offset = page;
        });
      }
    } catch (e) {
      if (mounted) setState(() => error = '$e');
    } finally {
      if (mounted) setState(() => loading = false);
    }
  }

  void showResult(Map<String, dynamic> result) {
    if (!mounted) return;
    setState(() {
      selected = result;
      rows = [
        for (final row in rows)
          if (row['run_id'] == result['run_id'])
            {...row, 'state': 'completed', 'status': result['status']}
          else
            row,
      ];
    });
  }

  Future<void> open(Map<String, dynamic> row, {bool retry = false}) async {
    setState(() {
      loading = true;
      error = null;
      selected = null;
      execution = null;
    });
    try {
      final id = row['run_id'] as String;
      if (retry) {
        final result = await widget.client.retry(id, row['attempt'] as int);
        showResult(result);
      } else if (row['state'] == 'completed') {
        final result = await widget.client.loadRun(id);
        showResult(result);
      } else {
        final job = await widget.client.job(id);
        if (job['state'] == 'completed') {
          final result = await widget.client.loadRun(id);
          showResult(result);
        } else if (mounted) {
          setState(() => execution = job);
        }
      }
    } on ApiFailure catch (e) {
      if (mounted) {
        setState(() {
          error = e.message;
          execution = e.job;
        });
      }
    } catch (_) {
      if (mounted) {
        setState(
          () => error =
              'Could not open this experiment. Refresh history and retry.',
        );
      }
    } finally {
      if (mounted) setState(() => loading = false);
    }
  }

  @override
  Widget build(BuildContext context) => AlgaShell(
    selected: 'history',
    onNew: () => Navigator.of(context).pop(),
    onHistory: selected == null ? null : () => setState(() => selected = null),
    child: SingleChildScrollView(
      key: ValueKey(selected == null ? 'history-list' : 'history-report'),
      padding: const EdgeInsets.fromLTRB(28, 32, 28, 64),
      child: Center(
        child: ConstrainedBox(
          constraints: const BoxConstraints(maxWidth: 1240),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              if (selected != null) ...[
                Align(
                  alignment: Alignment.centerLeft,
                  child: TextButton.icon(
                    onPressed: () => setState(() => selected = null),
                    icon: const Icon(Icons.arrow_back, size: 18),
                    label: const Text('Experiment history'),
                  ),
                ),
                ReportView(
                  result: selected!,
                  reportUri: widget.client.reportUrl(
                    selected!['run_id'] as String,
                  ),
                ),
              ] else ...[
                const Text(
                  'EXPERIMENTS',
                  style: TextStyle(
                    fontSize: 11,
                    fontWeight: FontWeight.w800,
                    letterSpacing: 2,
                    color: AlgaColors.green,
                  ),
                ),
                const SizedBox(height: 12),
                const Text(
                  'Experiment history',
                  style: TextStyle(
                    fontSize: 39,
                    fontWeight: FontWeight.w800,
                    letterSpacing: -1.7,
                  ),
                ),
                const SizedBox(height: 5),
                const Text(
                  'Reopen a report or inspect a saved attempt.',
                  style: TextStyle(fontSize: 14, color: AlgaColors.muted),
                ),
                const SizedBox(height: 24),
                AlgaCard(
                  child: Wrap(
                    spacing: 12,
                    runSpacing: 12,
                    children: [
                      DropdownButton<String>(
                        value: status ?? 'all',
                        items: [
                          for (final s in [
                            'all',
                            'queued',
                            'running',
                            'failed',
                            'interrupted',
                            'report_ready',
                            'insufficient_data',
                            'generation_failed',
                          ])
                            DropdownMenuItem(
                              value: s,
                              child: Text(
                                s == 'all'
                                    ? 'All statuses'
                                    : s.replaceAll('_', ' '),
                              ),
                            ),
                        ],
                        onChanged: loading
                            ? null
                            : (s) {
                                setState(() => status = s == 'all' ? null : s);
                                refresh();
                              },
                      ),
                      DropdownButton<String>(
                        value: algae ?? 'all',
                        items: [
                          for (final s in [
                            'all',
                            'spirulina',
                            'chlorella',
                            'blend',
                          ])
                            DropdownMenuItem(
                              value: s,
                              child: Text(s == 'all' ? 'All algae' : s),
                            ),
                        ],
                        onChanged: loading
                            ? null
                            : (s) {
                                setState(() => algae = s == 'all' ? null : s);
                                refresh();
                              },
                      ),
                      OutlinedButton(
                        onPressed: loading
                            ? null
                            : () async {
                                final range = await showDateRangePicker(
                                  context: context,
                                  firstDate: DateTime(2000),
                                  lastDate: DateTime.now().add(
                                    const Duration(days: 1),
                                  ),
                                  initialDateRange: dates,
                                );
                                if (range != null && mounted) {
                                  setState(() => dates = range);
                                  refresh();
                                }
                              },
                        child: Text(
                          dates == null
                              ? 'Filter dates (UTC)'
                              : '${dates!.start.toIso8601String().split('T').first} – ${dates!.end.toIso8601String().split('T').first} UTC',
                        ),
                      ),
                      if (dates != null)
                        TextButton(
                          onPressed: loading
                              ? null
                              : () {
                                  setState(() => dates = null);
                                  refresh();
                                },
                          child: const Text('Clear dates'),
                        ),
                      OutlinedButton(
                        onPressed: loading ? null : () => refresh(),
                        child: const Text('Refresh history'),
                      ),
                    ],
                  ),
                ),
                const SizedBox(height: 16),
                if (loading) const LinearProgressIndicator(),
                if (error != null)
                  Padding(
                    padding: const EdgeInsets.all(12),
                    child: Text(
                      error!,
                      style: TextStyle(
                        color: Theme.of(context).colorScheme.error,
                      ),
                    ),
                  ),
                if (!loading && error == null && rows.isEmpty)
                  const Text('No experiments match these filters.'),
                for (final row in rows)
                  AlgaCard(
                    padding: EdgeInsets.zero,
                    child: ListTile(
                      title: Text(
                        '${row['algae']} · ${row['status'].toString().replaceAll('_', ' ')}',
                      ),
                      subtitle: Text('${row['created_at']}\n${row['run_id']}'),
                      onTap: loading ? null : () => open(row),
                      trailing: const Icon(Icons.chevron_right),
                    ),
                  ),
                Wrap(
                  spacing: 12,
                  children: [
                    TextButton(
                      onPressed: loading || offset == 0
                          ? null
                          : () => refresh(page: offset - 20),
                      child: const Text('Previous'),
                    ),
                    Text('Page ${offset ~/ 20 + 1}'),
                    TextButton(
                      onPressed: loading || rows.length < 20
                          ? null
                          : () => refresh(page: offset + 20),
                      child: const Text('Next'),
                    ),
                  ],
                ),
                if (execution != null)
                  AlgaCard(
                    padding: const EdgeInsets.all(16),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.stretch,
                      children: [
                        Text(
                          'Execution ${execution!['state']} · attempt ${execution!['attempt']}',
                        ),
                        if (execution!['error_code'] != null)
                          Text('Reason: ${execution!['error_code']}'),
                        const Text(
                          'Refresh history to check progress. An execution stops being active after its heartbeat expires.',
                        ),
                        for (final attempt in execution!['attempts'] ?? [])
                          Text(
                            'Attempt ${attempt['attempt']}: ${attempt['state']} ${attempt['error_code'] ?? ''}',
                          ),
                        if ([
                          'failed',
                          'interrupted',
                        ].contains(execution!['state'])) ...[
                          const Text(
                            'Retry uses the saved inputs and the backend’s current configuration. The earlier attempt remains in history.',
                          ),
                          FilledButton(
                            onPressed: loading
                                ? null
                                : () => open({
                                    'run_id': execution!['job_id'],
                                    'attempt': execution!['attempt'],
                                  }, retry: true),
                            child: const Text('Retry saved experiment'),
                          ),
                        ],
                      ],
                    ),
                  ),
              ],
            ],
          ),
        ),
      ),
    ),
  );
}
