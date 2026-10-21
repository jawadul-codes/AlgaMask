import 'package:flutter/material.dart';

import 'api_client.dart';

class InputScreen extends StatefulWidget {
  const InputScreen({super.key, this.client});
  final ApiClient? client;
  @override
  State<InputScreen> createState() => _InputScreenState();
}

class _InputScreenState extends State<InputScreen> {
  String flavour = 'cocoa-spice';
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
        'algae': 'spirulina',
        'inclusion_pct': inclusion,
        'serving_g': 45,
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
                'Frozen proof: explore protein density in a 45 g spirulina bar while making sensory risks and evidence visible.',
              ),
              const SizedBox(height: 20),
              const Card(
                child: Padding(
                  padding: EdgeInsets.all(16),
                  child: Text(
                    'Day 1 uses deterministic mock agents and synthetic evidence. No scientific or sensory claim is approved.',
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
                            'cocoa-spice',
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
                          loading ? 'Running sample workflow…' : 'Run Day 1 workflow',
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
                _WorkflowResult(result: result!),
              ],
              const SizedBox(height: 32),
            ],
          ),
        ),
      ),
    ),
  );
}

class _WorkflowResult extends StatelessWidget {
  const _WorkflowResult({required this.result});
  final Map<String, dynamic> result;

  @override
  Widget build(BuildContext context) {
    final trace = (result['trace'] as List<dynamic>? ?? const []);
    final sensory = (result['sensory_map'] as List<dynamic>? ?? const []);
    final formulations = (result['formulations'] as List<dynamic>? ?? const []);
    final controls = (result['controls'] as List<dynamic>? ?? const []);
    final evidence = (result['evidence'] as List<dynamic>? ?? const []);
    final impact = result['impact'] as Map<String, dynamic>? ?? const {};
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text('Mock workflow · ${result['status'] ?? 'unknown'}', style: Theme.of(context).textTheme.titleLarge),
        const SizedBox(height: 12),
        _ResultCard(title: 'Agent trace', child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [for (final item in trace)
            ListTile(
              contentPadding: EdgeInsets.zero,
              dense: true,
              leading: const Icon(Icons.check_circle_outline),
              title: Text('${item['agent']} · ${item['state']}'),
              subtitle: Text('${item['summary']} (${item['status']})'),
            ),
          ],
        )),
        const SizedBox(height: 12),
        _ResultCard(title: 'Sensory map · assumed for demo', child: Wrap(
          spacing: 8,
          runSpacing: 8,
          children: [for (final item in sensory)
            Chip(label: Text('${item['category']}: ${item['relative_risk']}')),
          ],
        )),
        const SizedBox(height: 12),
        _ResultCard(title: 'Evidence placeholders', child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [for (final item in evidence)
            Padding(
              padding: const EdgeInsets.only(bottom: 8),
              child: Text('${item['title']} · ${item['status']}'),
            ),
          ],
        )),
        const SizedBox(height: 12),
        _ResultCard(title: 'Generated concepts', child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [for (final item in formulations)
            Padding(
              padding: const EdgeInsets.only(bottom: 10),
              child: Text('${item['name']} · ${item['total_g']} g · ${_ingredients(item)}'),
            ),
          ],
        )),
        const SizedBox(height: 12),
        _ResultCard(title: 'Controls and impact', child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('Controls: ${controls.map((item) => item['id']).join(', ')}'),
            Text('Protein change: ${impact['nutrition_change_pct'] ?? 'unknown'}'),
            Text('Sensory change: ${impact['sensory_change_pct'] ?? 'unknown'}'),
          ],
        )),
        for (final limitation in (result['limitations'] as List<dynamic>? ?? const []))
          Padding(
            padding: const EdgeInsets.only(top: 8),
            child: Text('• $limitation', style: Theme.of(context).textTheme.bodySmall),
          ),
      ],
    );
  }

  String _ingredients(dynamic formula) {
    final ingredients = (formula['ingredients'] as List<dynamic>? ?? const []);
    return ingredients.map((item) => '${item['ingredient_id']} ${item['grams']}g').join(', ');
  }
}

class _ResultCard extends StatelessWidget {
  const _ResultCard({required this.title, required this.child});
  final String title;
  final Widget child;

  @override
  Widget build(BuildContext context) => Card(
    child: Padding(
      padding: const EdgeInsets.all(20),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(title, style: Theme.of(context).textTheme.titleMedium),
          const SizedBox(height: 10),
          child,
        ],
      ),
    ),
  );
}
