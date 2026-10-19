import 'package:flutter/material.dart';

import 'api_client.dart';
import 'report_view.dart';

class InputScreen extends StatefulWidget {
  const InputScreen({super.key, this.client});
  final ApiClient? client;
  @override
  State<InputScreen> createState() => _InputScreenState();
}

class _InputScreenState extends State<InputScreen> {
  String algae = 'blend';
  String flavour = 'cocoa-spice';
  double inclusion = 5;
  double serving = 45;
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
        'algae': algae,
        'inclusion_pct': inclusion,
        'serving_g': serving,
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
          child: Chip(label: Text('LOCAL MOCK')),
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
                'Explore the next algae formulation.',
                style: Theme.of(context).textTheme.headlineLarge,
              ),
              const SizedBox(height: 12),
              const Text(
                'A protein-bar concept workspace, from sensory profile to experiment report.',
              ),
              const SizedBox(height: 20),
              const Card(
                child: Padding(
                  padding: EdgeInsets.all(16),
                  child: Text(
                    'Demo workspace • Recipes, evidence and risk levels are synthetic. Nutrition and sensory results remain unknown until data is added.',
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
                      DropdownButtonFormField<String>(
                        initialValue: algae,
                        isExpanded: true,
                        decoration: const InputDecoration(labelText: 'Algae'),
                        items: const [
                          DropdownMenuItem(
                            value: 'blend',
                            child: Text('Spirulina + chlorella'),
                          ),
                          DropdownMenuItem(
                            value: 'spirulina',
                            child: Text('Spirulina'),
                          ),
                          DropdownMenuItem(
                            value: 'chlorella',
                            child: Text('Chlorella'),
                          ),
                        ],
                        onChanged: loading
                            ? null
                            : (v) => setState(() => algae = v!),
                      ),
                      const SizedBox(height: 16),
                      Text('Algae inclusion · ${inclusion.round()}%'),
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
                      Text('Serving mass · ${serving.round()} g'),
                      Slider(
                        value: serving,
                        min: 40,
                        max: 50,
                        divisions: 10,
                        label: '${serving.round()} g',
                        onChanged: loading
                            ? null
                            : (v) => setState(() => serving = v),
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
                          loading ? 'Running workflow…' : 'Run mock experiment',
                        ),
                      ),
                      if (loading) ...[
                        const SizedBox(height: 16),
                        const LinearProgressIndicator(),
                        const Text('Waiting for the six-agent workflow…'),
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
                ReportView(result: result!),
              ],
              const SizedBox(height: 32),
            ],
          ),
        ),
      ),
    ),
  );
}
