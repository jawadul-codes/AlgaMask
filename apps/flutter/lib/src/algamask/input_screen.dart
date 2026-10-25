import 'dart:async';

import 'package:flutter/material.dart';

import 'api_client.dart';
import 'design.dart';
import 'history_screen.dart';
import 'report_view.dart';

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
  String exclusionMode = 'ingredient_preference';
  bool loading = false, fixedProof = false;
  String? error;
  Map<String, dynamic>? result;
  Map<String, dynamic>? feasibility;
  String? checkError;
  bool checking = true;
  Timer? debounce;
  int revision = 0;

  Map<String, dynamic> inputs() => {
    if (fixedProof) 'experiment': 'spirulina-proof-v1',
    'algae': fixedProof ? 'spirulina' : algae,
    'inclusion_pct': fixedProof ? 2.0 : inclusion,
    'serving_g': fixedProof ? 45.0 : serving,
    'flavour': fixedProof ? 'cocoa-spice' : flavour,
    'exclusions': exclusions.toList(),
    if (exclusions.isNotEmpty) 'exclusion_mode': exclusionMode,
    if (protein.text.trim().isNotEmpty)
      'min_protein_g': double.parse(protein.text.trim()),
    if (energy.text.trim().isNotEmpty)
      'max_energy_kcal': double.parse(energy.text.trim()),
    if (sugar.text.trim().isNotEmpty)
      'max_sugar_g': double.parse(sugar.text.trim()),
  };

  @override
  void initState() {
    super.initState();
    for (final field in [protein, energy, sugar]) {
      field.addListener(scheduleCheck);
    }
    scheduleCheck();
  }

  void change(VoidCallback update) {
    setState(update);
    scheduleCheck();
  }

  void scheduleCheck() {
    debounce?.cancel();
    final current = ++revision;
    setState(() {
      checking = true;
      feasibility = null;
      checkError = null;
    });
    debounce = Timer(const Duration(milliseconds: 350), () async {
      if (!mounted) return;
      if (!(form.currentState?.validate() ?? false)) {
        setState(() {
          checking = false;
          checkError = 'Correct the highlighted input values to check this configuration.';
        });
        return;
      }
      try {
        final check = await client.preflight(inputs());
        if (mounted && current == revision) {
          setState(() {
            feasibility = check;
            checking = false;
          });
        }
      } catch (e) {
        if (mounted && current == revision) {
          setState(() {
            checking = false;
            checkError = e is ApiFailure ? e.message : 'Could not check the configuration. Check your backend connection and try again.';
          });
        }
      }
    });
  }

  @override
  void dispose() {
    debounce?.cancel();
    revision++;
    protein.dispose();
    energy.dispose();
    sugar.dispose();
    if (widget.client == null) client.close();
    super.dispose();
  }

  Future<void> submit() async {
    if (loading ||
        checking ||
        feasibility?['can_run'] != true ||
        !form.currentState!.validate()) {
      return;
    }
    setState(() {
      loading = true;
      error = null;
      result = null;
    });
    try {
      final response = await client.run(inputs());
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

  void newExperiment() {
    setState(() => result = null);
    scheduleCheck();
  }

  Future<void> openHistory() async {
    final requestedNewExperiment = await Navigator.of(context).push<bool>(
      MaterialPageRoute<bool>(builder: (_) => HistoryScreen(client: client)),
    );
    if (mounted && requestedNewExperiment == true) {
      newExperiment();
    }
  }

  @override
  Widget build(BuildContext context) => AlgaShell(
    selected: 'new',
    onNew: result == null ? null : newExperiment,
    onHistory: loading ? null : openHistory,
    child: SingleChildScrollView(
      key: ValueKey(
        result == null ? 'experiment-builder' : 'experiment-report',
      ),
      padding: const EdgeInsets.fromLTRB(28, 32, 28, 64),
      child: Center(
        child: ConstrainedBox(
          constraints: const BoxConstraints(maxWidth: 1240),
          child: result == null
              ? _builder()
              : Column(
                  crossAxisAlignment: CrossAxisAlignment.stretch,
                  children: [
                    Align(
                      alignment: Alignment.centerLeft,
                      child: TextButton.icon(
                        onPressed: newExperiment,
                        icon: const Icon(Icons.arrow_back, size: 18),
                        label: const Text('New experiment'),
                      ),
                    ),
                    ReportView(
                      result: result!,
                      reportUri: client.reportUrl(result!['run_id'] as String),
                    ),
                  ],
                ),
        ),
      ),
    ),
  );

  Widget _builder() => Form(
    key: form,
    child: Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        const Text(
          'NEW EXPERIMENT',
          style: TextStyle(
            fontSize: 11,
            fontWeight: FontWeight.w800,
            letterSpacing: 2,
            color: AlgaColors.green,
          ),
        ),
        const SizedBox(height: 12),
        const Text(
          'Design a better algae bar',
          style: TextStyle(
            fontSize: 39,
            fontWeight: FontWeight.w800,
            letterSpacing: -1.7,
            height: 1.08,
          ),
        ),
        const SizedBox(height: 12),
        const Text(
          'Explore algae sources, formulation options, and nutrition targets before laboratory trials.',
          style: TextStyle(fontSize: 15, color: AlgaColors.muted),
        ),
        const SizedBox(height: 28),
        LayoutBuilder(
          builder: (context, constraints) {
            final left = _setupCard(), right = _briefCard();
            if (constraints.maxWidth < 880) {
              return Column(
                children: [left, const SizedBox(height: 18), right],
              );
            }
            return Row(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Expanded(flex: 7, child: left),
                const SizedBox(width: 18),
                Expanded(flex: 4, child: right),
              ],
            );
          },
        ),
        if (error != null)
          Padding(
            padding: const EdgeInsets.only(top: 18),
            child: AlgaNotice(text: error!),
          ),
        if (loading)
          const Padding(
            padding: EdgeInsets.only(top: 18),
            child: Column(
              children: [
                LinearProgressIndicator(),
                SizedBox(height: 10),
                Text(
                  'Retrieving evidence and screening candidates. The first local run may take longer.',
                ),
              ],
            ),
          ),
      ],
    ),
  );

  Widget _setupCard() => AlgaCard(
    child: Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        _step(
          '01',
          'Algae source',
          'Select the primary algae source for this experiment.',
        ),
        const SizedBox(height: 18),
        if (fixedProof)
          const AlgaNotice(
            text: 'Fixed proof uses spirulina at 2% inclusion and a 45 g ingredient input.',
          )
        else
          LayoutBuilder(
            builder: (context, c) => Wrap(
              spacing: 12,
              runSpacing: 12,
              children: [
                _choice(
                  'spirulina',
                  'Spirulina',
                  'Primary source',
                  Icons.spa_outlined,
                  algae == 'spirulina',
                  c.maxWidth,
                ),
                _choice(
                  'chlorella',
                  'Chlorella',
                  'Alternative source',
                  Icons.grass,
                  algae == 'chlorella',
                  c.maxWidth,
                ),
                _choice(
                  'blend',
                  'Blend',
                  'Combined sources',
                  Icons.blur_on,
                  algae == 'blend',
                  c.maxWidth,
                ),
              ],
            ),
          ),
        const SizedBox(height: 27),
        const Divider(color: AlgaColors.line),
        const SizedBox(height: 18),
        _step('02', 'Formula', 'Set the core formulation parameters.'),
        const SizedBox(height: 20),
        if (!fixedProof)
          LayoutBuilder(
            builder: (context, c) {
              final a = _rangeControl(
                'Algae inclusion',
                '${inclusion.round()}%',
                inclusion,
                1,
                15,
                14,
                (v) => change(() => inclusion = v),
              );
              final b = _rangeControl(
                'Serving size',
                '${serving.round()} g',
                serving,
                40,
                50,
                10,
                (v) => change(() => serving = v),
              );
              return c.maxWidth < 510
                  ? Column(children: [a, const SizedBox(height: 12), b])
                  : Row(
                      children: [
                        Expanded(child: a),
                        const SizedBox(width: 25),
                        Expanded(child: b),
                      ],
                    );
            },
          )
        else
          const Text(
            'Spirulina 2% · 45 g ingredient input',
            style: TextStyle(color: AlgaColors.muted),
          ),
        const SizedBox(height: 24),
        const Divider(color: AlgaColors.line),
        const SizedBox(height: 18),
        _step(
          '03',
          'Flavour direction',
          'Select the intended flavour direction.',
        ),
        const SizedBox(height: 18),
        if (!fixedProof)
          LayoutBuilder(
            builder: (context, c) => Wrap(
              spacing: 12,
              runSpacing: 12,
              children: [
                _choice(
                  'cocoa-spice',
                  'Cocoa + spice',
                  'Warm and familiar',
                  Icons.coffee_outlined,
                  flavour == 'cocoa-spice',
                  c.maxWidth,
                  isFlavour: true,
                ),
                _choice(
                  'vanilla',
                  'Vanilla',
                  'Mild profile',
                  Icons.local_florist_outlined,
                  flavour == 'vanilla',
                  c.maxWidth,
                  isFlavour: true,
                ),
                _choice(
                  'citrus',
                  'Citrus',
                  'Bright notes',
                  Icons.wb_sunny_outlined,
                  flavour == 'citrus',
                  c.maxWidth,
                  isFlavour: true,
                ),
              ],
            ),
          )
        else
          const Text(
            'Cocoa + spice',
            style: TextStyle(color: AlgaColors.muted),
          ),
        const SizedBox(height: 26),
        const Divider(color: AlgaColors.line),
        SwitchListTile.adaptive(
          contentPadding: EdgeInsets.zero,
          title: const Text(
            'Fixed B0 / A0 / A1 experiment',
            style: TextStyle(fontSize: 14, fontWeight: FontWeight.w700),
          ),
          subtitle: const Text(
            'spirulina-proof-v1 · engineering assumptions',
            style: TextStyle(fontSize: 12),
          ),
          value: fixedProof,
          onChanged: loading ? null : (v) => change(() => fixedProof = v),
        ),
        if (fixedProof)
          const Padding(
            padding: EdgeInsets.only(top: 8),
            child: Text(
              '45 g ingredient input, not finished serving. Spirulina 2% in A0/A1; dates 13.50 g and cocoa 0.90 g in every arm. A1 adds 0.45 g cinnamon by replacing oats. Nutrition targets apply to A1; exclusions apply to every arm.',
              style: TextStyle(
                fontSize: 12,
                color: AlgaColors.muted,
                height: 1.5,
              ),
            ),
          ),
      ],
    ),
  );

  Widget _briefCard() => AlgaCard(
    child: Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        const Text(
          'Live experiment brief',
          style: TextStyle(
            fontSize: 20,
            fontWeight: FontWeight.w800,
            letterSpacing: -0.5,
          ),
        ),
        const SizedBox(height: 4),
        const Text(
          'This summary updates as you adjust your selections.',
          style: TextStyle(fontSize: 12, color: AlgaColors.muted),
        ),
        const SizedBox(height: 17),
        Container(
          padding: const EdgeInsets.all(16),
          decoration: BoxDecoration(
            color: AlgaColors.pale,
            borderRadius: BorderRadius.circular(8),
          ),
          child: Column(
            children: [
              _summary(
                'Algae source',
                fixedProof ? 'Spirulina' : _title(algae),
                Icons.spa_outlined,
              ),
              _summary(
                'Algae inclusion',
                fixedProof ? '2%' : '${inclusion.round()}%',
                Icons.percent,
              ),
              _summary(
                'Serving size',
                fixedProof ? '45 g' : '${serving.round()} g',
                Icons.inventory_2_outlined,
              ),
              _summary(
                'Flavour direction',
                fixedProof ? 'Cocoa + spice' : _title(flavour),
                Icons.local_florist_outlined,
              ),
            ],
          ),
        ),
        const SizedBox(height: 23),
        const Divider(color: AlgaColors.line),
        const SizedBox(height: 15),
        const Text(
          'Nutrition targets',
          style: TextStyle(fontSize: 15, fontWeight: FontWeight.w800),
        ),
        const SizedBox(height: 3),
        const Text(
          'Optional limits per serving',
          style: TextStyle(fontSize: 12, color: AlgaColors.muted),
        ),
        const SizedBox(height: 16),
        _target('Minimum protein', 'g', protein, 50),
        _target('Maximum energy', 'kcal', energy, 1000, positive: true),
        _target('Maximum sugar', 'g', sugar, 50),
        const Text(
          'Targets use reference ingredient composition, not lab measurements. The check below shows available ranges and any missing data. Total sugar includes sugar naturally present in ingredients.',
          style: TextStyle(fontSize: 11, color: AlgaColors.muted, height: 1.45),
        ),
        const SizedBox(height: 21),
        const Divider(color: AlgaColors.line),
        const SizedBox(height: 15),
        const Text(
          'Exclusions',
          style: TextStyle(fontSize: 15, fontWeight: FontWeight.w800),
        ),
        const SizedBox(height: 3),
        const Text(
          'Choose how to apply your exclusions',
          style: TextStyle(fontSize: 12, color: AlgaColors.muted),
        ),
        const SizedBox(height: 12),
        DropdownButton<String>(
          key: const Key('exclusion-mode'),
          value: exclusionMode,
          isExpanded: true,
          items: const [
            DropdownMenuItem(
              value: 'ingredient_preference',
              child: Text('Omit ingredients (preference)'),
            ),
            DropdownMenuItem(
              value: 'verified_free_from',
              child: Text('Require verified free-from'),
            ),
          ],
          onChanged: loading
              ? null
              : (value) => change(() => exclusionMode = value!),
        ),
        Wrap(
          spacing: 6,
          runSpacing: 4,
          children: [
            for (final value in [
              'peanut',
              'tree_nut',
              'sesame',
              'oats',
              'coconut',
              'milk',
              'soy',
            ])
              FilterChip(
                label: Text(
                  value.replaceAll('_', ' '),
                  style: const TextStyle(fontSize: 11),
                ),
                selected: exclusions.contains(value),
                onSelected: loading
                    ? null
                    : (v) => change(
                        () => v
                            ? exclusions.add(value)
                            : exclusions.remove(value),
                      ),
                visualDensity: VisualDensity.compact,
                selectedColor: AlgaColors.pale,
                checkmarkColor: AlgaColors.green,
              ),
          ],
        ),
        const SizedBox(height: 6),
        Text(
          exclusionMode == 'ingredient_preference'
              ? 'Omits the selected foods from the recipe. For an allergy, choose verified free-from; preferences do not check supplier cross-contact.'
              : 'Requires verified absence, including supplier cross-contact. Current supplier data cannot confirm this for selected exclusions.',
          style: const TextStyle(
            fontSize: 11,
            color: AlgaColors.muted,
            height: 1.4,
          ),
        ),
        const SizedBox(height: 18),
        _feasibilityNotice(),
        const SizedBox(height: 12),
        SizedBox(
          width: double.infinity,
          child: FilledButton.icon(
            onPressed: loading || checking || feasibility?['can_run'] != true
                ? null
                : submit,
            icon: Icon(
              loading ? Icons.hourglass_top : Icons.play_arrow_rounded,
            ),
            label: Text(loading ? 'Running…' : 'Run screening'),
          ),
        ),
        const SizedBox(height: 12),
        const AlgaNotice(
          text: 'Computational experiment · not production approved',
        ),
      ],
    ),
  );

  Widget _feasibilityNotice() {
    final messages = <String>[
      if (checking) 'Checking available data and targets…',
      ?checkError,
      if (feasibility != null)
        feasibility!['can_run'] == true
            ? 'Configuration can be screened with current data.'
            : 'Adjust your configuration before running.',
      ...?((feasibility?['messages'] as List?)?.map((e) => '$e')),
    ];
    final ranges = feasibility?['margins'] as Map? ?? {};
    for (final entry in ranges.entries) {
      final value = entry.value as Map;
      final label = switch (entry.key) {
        'min_protein_g' => 'Protein (g)',
        'max_energy_kcal' => 'Energy (kcal)',
        _ => 'Sugar (g)',
      };
      messages.add(
        value['min'] == null
            ? '$label: unknown for this configuration.'
            : '$label: ${(value['min'] as num).toStringAsFixed(4)}–${(value['max'] as num).toStringAsFixed(4)} per serving in current recipes.',
      );
    }
    messages.addAll((feasibility?['notes'] as List? ?? []).map((e) => '$e'));
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        AlgaNotice(text: messages.join('\n\n')),
        if (checkError != null)
          TextButton(
            onPressed: scheduleCheck,
            child: const Text('Check again'),
          ),
      ],
    );
  }

  Widget _step(String number, String title, String subtitle) => Row(
    crossAxisAlignment: CrossAxisAlignment.start,
    children: [
      Container(
        width: 42,
        height: 42,
        alignment: Alignment.center,
        decoration: const BoxDecoration(
          color: AlgaColors.pale,
          shape: BoxShape.circle,
        ),
        child: Text(
          number,
          style: const TextStyle(
            fontWeight: FontWeight.w800,
            color: AlgaColors.forest,
          ),
        ),
      ),
      const SizedBox(width: 13),
      Expanded(
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              title,
              style: const TextStyle(
                fontSize: 18,
                fontWeight: FontWeight.w800,
                letterSpacing: -0.4,
              ),
            ),
            Text(
              subtitle,
              style: const TextStyle(fontSize: 12, color: AlgaColors.muted),
            ),
          ],
        ),
      ),
    ],
  );

  Widget _choice(
    String value,
    String title,
    String subtitle,
    IconData icon,
    bool selected,
    double available, {
    bool isFlavour = false,
  }) {
    final width = available < 510 ? available : (available - 24) / 3;
    return InkWell(
      borderRadius: BorderRadius.circular(9),
      onTap: loading
          ? null
          : () => change(() => isFlavour ? flavour = value : algae = value),
      child: Container(
        width: width,
        height: 184,
        padding: const EdgeInsets.all(14),
        decoration: BoxDecoration(
          color: selected ? const Color(0xfff3f8f1) : Colors.white,
          border: Border.all(
            color: selected ? AlgaColors.green : AlgaColors.line,
            width: selected ? 1.5 : 1,
          ),
          borderRadius: BorderRadius.circular(9),
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(
                  selected
                      ? Icons.radio_button_checked
                      : Icons.radio_button_unchecked,
                  color: selected ? AlgaColors.forest : AlgaColors.muted,
                  size: 19,
                ),
              ],
            ),
            Expanded(
              child: Center(
                child: Image.asset(
                  'assets/ingredients/$value.png',
                  width: 124,
                  height: 94,
                  fit: BoxFit.contain,
                  errorBuilder: (_, _, _) =>
                      Icon(icon, color: AlgaColors.green, size: 42),
                ),
              ),
            ),
            Text(
              title,
              style: const TextStyle(fontSize: 14, fontWeight: FontWeight.w800),
            ),
            Text(
              subtitle,
              style: const TextStyle(fontSize: 11, color: AlgaColors.muted),
            ),
          ],
        ),
      ),
    );
  }

  Widget _rangeControl(
    String title,
    String valueText,
    double value,
    double min,
    double max,
    int divisions,
    ValueChanged<double> onChanged,
  ) => Column(
    crossAxisAlignment: CrossAxisAlignment.stretch,
    children: [
      Row(
        children: [
          Expanded(
            child: Text(
              title,
              style: const TextStyle(fontSize: 13, fontWeight: FontWeight.w700),
            ),
          ),
          Text(
            valueText,
            style: const TextStyle(
              fontWeight: FontWeight.w800,
              color: AlgaColors.forest,
            ),
          ),
        ],
      ),
      Slider(
        value: value,
        min: min,
        max: max,
        divisions: divisions,
        onChanged: loading ? null : onChanged,
      ),
      Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(
            '$min${title == 'Algae inclusion' ? '%' : ' g'}',
            style: const TextStyle(fontSize: 11, color: AlgaColors.muted),
          ),
          Text(
            '$max${title == 'Algae inclusion' ? '%' : ' g'}',
            style: const TextStyle(fontSize: 11, color: AlgaColors.muted),
          ),
        ],
      ),
    ],
  );

  Widget _summary(String label, String value, IconData icon) => Padding(
    padding: const EdgeInsets.symmetric(vertical: 7),
    child: Row(
      children: [
        Icon(icon, size: 18, color: AlgaColors.forest),
        const SizedBox(width: 11),
        Expanded(
          child: Text(
            label,
            style: const TextStyle(fontSize: 12, color: AlgaColors.muted),
          ),
        ),
        Text(
          value,
          style: const TextStyle(fontSize: 12, fontWeight: FontWeight.w800),
        ),
      ],
    ),
  );

  Widget _target(
    String label,
    String unit,
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
        suffixText: unit,
        hintText: 'Optional',
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

  String _title(String value) => value == 'cocoa-spice'
      ? 'Cocoa + spice'
      : value[0].toUpperCase() + value.substring(1);
}
