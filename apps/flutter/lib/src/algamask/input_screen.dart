import 'package:flutter/material.dart';

import 'api_client.dart';

class InputScreen extends StatefulWidget {
  const InputScreen({super.key, this.client});
  final ApiClient? client;
  @override
  State<InputScreen> createState() => _InputScreenState();
}

class _InputScreenState extends State<InputScreen> {
  String flavour = 'cocoa';
  double inclusion = 5;
  final exclusions = <String>{};
  bool loading = false;
  String? error;
  Map<String, dynamic>? result;

  Future<void> submit() async {
    setState(() {
      loading = true;
      error = null;
      result = null;
    });
    try {
      final response = await (widget.client ?? ApiClient()).run({
        'inclusion_pct': inclusion,
        'flavour': flavour,
        'exclusions': exclusions.toList(),
      });
      if (mounted) {
        setState(() => result = response);
      }
    } catch (_) {
      if (mounted) {
        setState(
          () => error =
              'Could not complete the run. Check that the local backend is running at $apiBase, then retry.',
        );
      }
    } finally {
      if (mounted) {
        setState(() => loading = false);
      }
    }
  }

  @override
  Widget build(BuildContext context) => Scaffold(
    appBar: AppBar(
      title: const Text('AlgaMask'),
      actions: const [
        Padding(
          padding: EdgeInsets.all(16),
          child: Chip(label: Text('DAY 1')),
        ),
      ],
    ),
    body: SingleChildScrollView(
      padding: const EdgeInsets.all(24),
      child: Center(
        child: ConstrainedBox(
          constraints: const BoxConstraints(maxWidth: 1120),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                'Spirulina protein bar',
                style: Theme.of(context).textTheme.headlineLarge,
              ),
              const SizedBox(height: 12),
              const Text(
                'Day 1 skeleton. One baseline, serving size 45 g, example spirulina levels 2% and 5%.',
              ),
              const SizedBox(height: 20),
              const Card(
                child: Padding(
                  padding: EdgeInsets.all(16),
                  child: Text(
                    'Placeholder result. The cards below are hard-coded. Sample rows are not approved.',
                  ),
                ),
              ),
              const SizedBox(height: 24),
              Card(
                child: Padding(
                  padding: const EdgeInsets.all(24),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        'Design your experiment',
                        style: Theme.of(context).textTheme.titleLarge,
                      ),
                      const SizedBox(height: 20),
                      const Text('Product · spirulina protein bar'),
                      const SizedBox(height: 8),
                      const Text('Baseline · oats, dried dates, unsweetened cocoa · 45 g'),
                      const SizedBox(height: 16),
                      const Text('Example spirulina levels'),
                      Wrap(
                        spacing: 8,
                        children: [
                          for (final level in [2.0, 5.0])
                            ChoiceChip(
                              label: Text('${level.round()}%'),
                              selected: inclusion == level,
                              onSelected: loading
                                  ? null
                                  : (_) => setState(() => inclusion = level),
                            ),
                        ],
                      ),
                      const SizedBox(height: 16),
                      Text('Spirulina inclusion · ${inclusion.round()}%'),
                      Slider(
                        value: inclusion,
                        min: 1,
                        max: 15,
                        divisions: 14,
                        label: '${inclusion.round()}%',
                        onChanged: loading
                            ? null
                            : (v) => setState(() => inclusion = v),
                      ),
                      DropdownButtonFormField<String>(
                        initialValue: flavour,
                        decoration: const InputDecoration(
                          labelText: 'Flavour direction',
                        ),
                        items: [
                          for (final value in [
                            'cocoa',
                            'vanilla',
                            'citrus',
                          ])
                            DropdownMenuItem(value: value, child: Text(value)),
                        ],
                        onChanged: loading
                            ? null
                            : (v) => setState(() => flavour = v!),
                      ),
                      const SizedBox(height: 20),
                      const Text('Ingredient exclusions'),
                      Wrap(
                        spacing: 8,
                        children: [
                          for (final value in [
                            'peanut',
                            'tree_nut',
                            'sesame',
                            'oats',
                            'coconut',
                          ])
                            FilterChip(
                              label: Text(value.replaceAll('_', ' ')),
                              selected: exclusions.contains(value),
                              onSelected: loading
                                  ? null
                                  : (selected) => setState(() {
                                      selected
                                          ? exclusions.add(value)
                                          : exclusions.remove(value);
                                    }),
                            ),
                        ],
                      ),
                      const SizedBox(height: 20),
                      FilledButton.icon(
                        onPressed: loading ? null : submit,
                        icon: const Icon(Icons.science_outlined),
                        label: Text(
                          loading ? 'Loading sample data…' : 'Show placeholder',
                        ),
                      ),
                      if (loading) ...[
                        const SizedBox(height: 16),
                        const LinearProgressIndicator(),
                        const Text('Reading the local sample files…'),
                      ],
                      if (error != null)
                        Padding(
                          padding: const EdgeInsets.only(top: 16),
                          child: Text(
                            error!,
                            style: TextStyle(
                              color: Theme.of(context).colorScheme.error,
                            ),
                          ),
                        ),
                    ],
                  ),
                ),
              ),
              if (result != null) ...[
                const SizedBox(height: 28),
                _PlaceholderCard(
                  title: result!['sensory_risk']['title'] as String,
                  body: result!['sensory_risk']['text'] as String,
                ),
                const SizedBox(height: 12),
                _PlaceholderCard(
                  title: result!['recommendation']['title'] as String,
                  body: result!['recommendation']['text'] as String,
                ),
              ],
              const SizedBox(height: 32),
            ],
          ),
        ),
      ),
    ),
  );
}

class _PlaceholderCard extends StatelessWidget {
  const _PlaceholderCard({required this.title, required this.body});
  final String title;
  final String body;

  @override
  Widget build(BuildContext context) => Card(
    child: Padding(
      padding: const EdgeInsets.all(20),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(title, style: Theme.of(context).textTheme.titleLarge),
          const SizedBox(height: 8),
          Text(body),
        ],
      ),
    ),
  );
}
