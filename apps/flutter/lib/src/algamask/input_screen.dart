import 'package:flutter/material.dart';

import 'api_client.dart';
import 'report_view.dart';
import 'history_screen.dart';

class InputScreen extends StatefulWidget {
  const InputScreen({super.key, this.client});
  final ApiClient? client;
  @override
  State<InputScreen> createState() => _InputScreenState();
}

class _InputScreenState extends State<InputScreen> {
  late final ApiClient client = widget.client ?? ApiClient();
  final form = GlobalKey<FormState>();
  final protein = TextEditingController();
  final energy = TextEditingController();
  final sugar = TextEditingController();
  String algae = 'spirulina', flavour = 'cocoa-spice';
  double inclusion = 5, serving = 45;
  final exclusions = <String>{};
  bool loading = false;
  String? error;
  Map<String, dynamic>? result;

  @override
  void dispose() {
    protein.dispose();
    energy.dispose();
    sugar.dispose();
    if (widget.client == null) client.close();
    super.dispose();
  }

  Future<void> submit() async {
    if (loading || !form.currentState!.validate()) return;
    setState(() {
      loading = true;
      error = null;
      result = null;
    });
    try {
      final response = await client.run({
        'algae': algae,
        'inclusion_pct': inclusion,
        'serving_g': serving,
        'flavour': flavour,
        'exclusions': exclusions.toList(),
        if (protein.text.trim().isNotEmpty)
          'min_protein_g': double.parse(protein.text.trim()),
        if (energy.text.trim().isNotEmpty)
          'max_energy_kcal': double.parse(energy.text.trim()),
        if (sugar.text.trim().isNotEmpty)
          'max_sugar_g': double.parse(sugar.text.trim()),
      });
      if (mounted) setState(() => result = response);
    } on ApiFailure catch (failure) {
      if (mounted) setState(() => error = failure.message);
    } catch (_) {
      if (mounted) {
        setState(
          () => error =
              'Could not complete the run. Check the backend at ${client.baseUrl} and retry with the same inputs to recover the original submission, or open experiment history.',
        );
      }
    } finally {
      if (mounted) setState(() => loading = false);
    }
  }

  Widget target(
    String label,
    TextEditingController controller,
    double maximum, {
    bool positive = false,
  }) => Padding(
    padding: const EdgeInsets.only(bottom: 12),
    child: TextFormField(
      controller: controller,
      enabled: !loading,
      keyboardType: const TextInputType.numberWithOptions(decimal: true),
      decoration: InputDecoration(
        labelText: label,
        helperText: 'Optional · per serving',
      ),
      validator: (text) {
        if (text == null || text.trim().isEmpty) return null;
        final value = double.tryParse(text.trim());
        if (value == null ||
            !value.isFinite ||
            value < 0 ||
            value > maximum ||
            (positive && value == 0)) {
          return 'Enter ${positive ? 'more than 0' : '0'} to $maximum, or leave blank.';
        }
        return null;
      },
    ),
  );

  @override
  Widget build(BuildContext context) => Scaffold(
    appBar: AppBar(
      title: const Text('AlgaMask'),
      actions: [
        IconButton(
          tooltip: 'Experiment history',
          onPressed: loading
              ? null
              : () => Navigator.of(context).push(
                  MaterialPageRoute<void>(
                    builder: (_) => HistoryScreen(client: client),
                  ),
                ),
          icon: const Icon(Icons.history),
        ),
      ],
    ),
    body: SingleChildScrollView(
      padding: const EdgeInsets.all(24),
      child: Center(
        child: ConstrainedBox(
          constraints: const BoxConstraints(maxWidth: 1000),
          child: Form(
            key: form,
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                Text(
                  'Design an algae-bar experiment',
                  style: Theme.of(context).textTheme.headlineMedium,
                ),
                const SizedBox(height: 12),
                const Text(
                  'Experimental screening, not a safety-approved recipe. Results identify the backend mode and data limitations. Missing values remain unknown.',
                ),
                const SizedBox(height: 24),
                DropdownButtonFormField<String>(
                  initialValue: algae,
                  decoration: const InputDecoration(labelText: 'Algae'),
                  items: [
                    for (final value in ['spirulina', 'chlorella', 'blend'])
                      DropdownMenuItem(value: value, child: Text(value)),
                  ],
                  onChanged: loading
                      ? null
                      : (value) => setState(() => algae = value!),
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
                      : (value) => setState(() => inclusion = value),
                ),
                Text('Serving · ${serving.round()} g'),
                Slider(
                  value: serving,
                  min: 40,
                  max: 50,
                  divisions: 10,
                  label: '${serving.round()} g',
                  onChanged: loading
                      ? null
                      : (value) => setState(() => serving = value),
                ),
                DropdownButtonFormField<String>(
                  initialValue: flavour,
                  decoration: const InputDecoration(
                    labelText: 'Flavour direction',
                  ),
                  items: [
                    for (final value in ['cocoa-spice', 'vanilla', 'citrus'])
                      DropdownMenuItem(value: value, child: Text(value)),
                  ],
                  onChanged: loading
                      ? null
                      : (value) => setState(() => flavour = value!),
                ),
                const SizedBox(height: 20),
                target('Minimum protein (g)', protein, 50),
                target('Maximum energy (kcal)', energy, 1000, positive: true),
                target('Maximum sugar (g)', sugar, 50),
                const Text(
                  'Sugar data is missing. Chlorella/blend energy is incomplete. Targets requiring those values cannot currently pass.',
                ),
                const SizedBox(height: 20),
                const Text('Exclusions'),
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
                const Text(
                  'Allergy exclusions may block screening because free-from coverage is incomplete. No result certifies allergen safety.',
                ),
                const SizedBox(height: 20),
                FilledButton(
                  onPressed: loading ? null : submit,
                  child: Text(loading ? 'Running…' : 'Run experiment'),
                ),
                if (loading) ...[
                  const SizedBox(height: 12),
                  const LinearProgressIndicator(),
                  const Text(
                    'Retrieving evidence and checking candidates. The first local run can take longer.',
                  ),
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
                if (result != null) ...[
                  const SizedBox(height: 24),
                  const Text(
                    'Saved result for the submitted settings. Editing inputs does not change this result; run again to apply changes.',
                  ),
                  ReportView(
                    result: result!,
                    reportUri: client.reportUrl(result!['run_id'] as String),
                  ),
                ],
              ],
            ),
          ),
        ),
      ),
    ),
  );
}
