import 'dart:convert';

import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:url_launcher/url_launcher.dart';

import 'design.dart';

class ReportView extends StatelessWidget {
  const ReportView({super.key, required this.result, required this.reportUri});
  final Map<String, dynamic> result;
  final Uri reportUri;

  String number(dynamic value, {int decimals = 1}) =>
      value is num ? value.toStringAsFixed(decimals) : 'unknown';
  String label(dynamic value) => '$value'.replaceAll('_', ' ');
  Map<String, dynamic> get impact =>
      (result['impact'] as Map?)?.cast<String, dynamic>() ?? {};
  Map<String, dynamic> get nutrition =>
      (impact['nutrition'] as Map?)?.cast<String, dynamic>() ?? {};
  Map<String, dynamic> get screening =>
      (impact['screening'] as Map?)?.cast<String, dynamic>() ?? {};
  List<dynamic> get formulas => [
    ...?result['controls'] as List?,
    ...?result['formulations'] as List?,
  ];

  Widget heading(String title, String subtitle) => Column(
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
      const SizedBox(height: 3),
      Text(
        subtitle,
        style: const TextStyle(fontSize: 12, color: AlgaColors.muted),
      ),
    ],
  );

  Widget details(String title, dynamic data) => ExpansionTile(
    tilePadding: EdgeInsets.zero,
    title: Text(
      title,
      style: const TextStyle(fontSize: 13, fontWeight: FontWeight.w700),
    ),
    children: [
      Padding(
        padding: const EdgeInsets.only(bottom: 14),
        child: SelectableText(
          const JsonEncoder.withIndent('  ').convert(data),
          style: const TextStyle(fontSize: 11),
        ),
      ),
    ],
  );

  Future<void> open(BuildContext context, Uri uri) async {
    try {
      if (!['http', 'https'].contains(uri.scheme) ||
          !await launchUrl(uri, webOnlyWindowName: '_blank')) {
        throw StateError('Cannot open link');
      }
    } catch (_) {
      if (context.mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text(
              'Could not open link. Check the backend or source URL.',
            ),
          ),
        );
      }
    }
  }

  Future<void> copy(BuildContext context) async {
    await Clipboard.setData(
      ClipboardData(text: const JsonEncoder.withIndent('  ').convert(result)),
    );
    if (context.mounted) {
      ScaffoldMessenger.of(context)
          .showSnackBar(const SnackBar(content: Text('Run JSON copied.')));
    }
  }

  @override
  Widget build(BuildContext context) {
    final ready = result['status'] == 'report_ready';
    final selected = _selectedFormula();
    final selectedId = selected?['id']?.toString();
    final estimate = nutrition[selectedId] as Map?;
    final serving = estimate?['per_serving'] as Map?;
    final protein = serving?['protein_g'];
    final energy = serving?['energy_kcal'];
    final mode = result['mode'] == 'mock'
        ? 'MOCK · synthetic fixtures'
        : result['mode'] == 'rag_development'
        ? 'LOCAL RAG · development data'
        : 'LOCAL RAG · released evidence';
    final top = Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text(
          'EXPERIMENTS  /  SCREENING REPORT',
          style: TextStyle(
            fontSize: 11,
            fontWeight: FontWeight.w800,
            color: AlgaColors.green,
            letterSpacing: 1.4,
          ),
        ),
        const SizedBox(height: 10),
        Wrap(
          crossAxisAlignment: WrapCrossAlignment.center,
          spacing: 14,
          runSpacing: 8,
          children: [
            const Text(
              'Screening report',
              style: TextStyle(
                fontSize: 35,
                fontWeight: FontWeight.w800,
                letterSpacing: -1.3,
              ),
            ),
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 11, vertical: 6),
              decoration: BoxDecoration(
                color: ready ? AlgaColors.pale : AlgaColors.amberPale,
                borderRadius: BorderRadius.circular(6),
              ),
              child: Text(
                label(result['status']),
                style: TextStyle(
                  fontWeight: FontWeight.w700,
                  fontSize: 12,
                  color: ready ? AlgaColors.green : AlgaColors.amber,
                ),
              ),
            ),
          ],
        ),
        const SizedBox(height: 5),
        SelectableText(
          'Run ${result['run_id']}   ·   $mode',
          style: const TextStyle(fontSize: 12, color: AlgaColors.muted),
        ),
        const SizedBox(height: 15),
        const AlgaNotice(
          text: 'Experimental screening only. Arithmetic checks do not establish scientific or allergen safety approval.',
        ),
        if (!ready)
          const Padding(
            padding: EdgeInsets.only(top: 12),
            child: Text(
              'No verified candidate was returned. Inspect the screening checks and workflow trace for the reason.',
              style: TextStyle(color: AlgaColors.muted),
            ),
          ),
        const SizedBox(height: 22),
      ],
    );

    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        top,
        AlgaCard(
          child: LayoutBuilder(
            builder: (context, c) {
              final metrics = <Widget>[
                _metric(
                  'Selected formulation',
                  selectedId ?? '—',
                  selected?['name']?.toString() ?? 'No formulation',
                  Icons.science_outlined,
                ),
                _metric(
                  'Protein estimate',
                  protein == null ? 'Unknown' : '${number(protein)} g',
                  'Per serving',
                  Icons.analytics_outlined,
                ),
                _metric(
                  'Energy estimate',
                  energy == null
                      ? 'Unknown'
                      : '${number(energy, decimals: 0)} kcal',
                  'Per serving',
                  Icons.bolt_outlined,
                ),
                _metric(
                  'Screened formulas',
                  '${formulas.length}',
                  'Controls and candidates',
                  Icons.check_circle_outline,
                ),
              ];
              if (c.maxWidth < 700) {
                return Wrap(
                  spacing: 20,
                  runSpacing: 20,
                  children: [
                    for (final item in metrics)
                      SizedBox(
                        width: c.maxWidth < 380
                            ? c.maxWidth
                            : (c.maxWidth - 20) / 2,
                        child: item,
                      ),
                  ],
                );
              }
              return Row(
                children: [
                  for (var i = 0; i < metrics.length; i++) ...[
                    if (i > 0) const SizedBox(width: 14),
                    Expanded(child: metrics[i]),
                  ],
                ],
              );
            },
          ),
        ),
        const SizedBox(height: 16),
        LayoutBuilder(
          builder: (context, c) {
            final left = Column(
              children: [
                _candidates(),
                const SizedBox(height: 16),
                _nutrition(),
              ],
            );
            final right = Column(
              children: [
                _evidence(context),
                const SizedBox(height: 16),
                _checks(),
              ],
            );
            if (c.maxWidth < 880) {
              return Column(
                children: [left, const SizedBox(height: 16), right],
              );
            }
            return Row(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Expanded(flex: 7, child: left),
                const SizedBox(width: 16),
                Expanded(flex: 5, child: right),
              ],
            );
          },
        ),
        const SizedBox(height: 16),
        AlgaCard(
          child: Column(
            children: [
              details('Submitted settings', result['request']),
              details(
                'Dataset provenance',
                result['retrieval'] ?? {'mode': mode},
              ),
              details('Retrieved evidence', result['evidence'] ?? []),
              details('Six-agent trace', result['trace'] ?? []),
              details('Limitations', result['limitations'] ?? []),
            ],
          ),
        ),
        const SizedBox(height: 17),
        Wrap(
          spacing: 10,
          runSpacing: 10,
          children: [
            FilledButton.icon(
              onPressed: () => open(context, reportUri),
              icon: const Icon(Icons.description_outlined, size: 18),
              label: const Text('Open print report'),
            ),
            OutlinedButton.icon(
              onPressed: () => copy(context),
              icon: const Icon(Icons.copy_outlined, size: 18),
              label: const Text('Copy run JSON'),
            ),
          ],
        ),
      ],
    );
  }

  Map? _selectedFormula() {
    final candidates = result['formulations'] as List? ?? [];
    for (final item in candidates) {
      if (item is Map && item['id'] == 'A1') return item;
    }
    if (candidates.isNotEmpty && candidates.first is Map) {
      return candidates.first as Map;
    }
    return null;
  }

  Widget _metric(String title, String value, String note, IconData icon) => Row(
    crossAxisAlignment: CrossAxisAlignment.start,
    children: [
      Container(
        width: 38,
        height: 38,
        decoration: const BoxDecoration(
          color: AlgaColors.pale,
          shape: BoxShape.circle,
        ),
        child: Icon(icon, size: 20, color: AlgaColors.green),
      ),
      const SizedBox(width: 10),
      Expanded(
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              title,
              style: const TextStyle(fontSize: 11, color: AlgaColors.muted),
            ),
            Text(
              value,
              style: const TextStyle(
                fontSize: 24,
                fontWeight: FontWeight.w800,
                letterSpacing: -0.5,
              ),
              maxLines: 1,
              overflow: TextOverflow.ellipsis,
            ),
            Text(
              note,
              style: const TextStyle(fontSize: 11, color: AlgaColors.muted),
              maxLines: 2,
            ),
          ],
        ),
      ),
    ],
  );

  Widget _candidates() => AlgaCard(
    child: Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        heading(
          'Candidate comparison',
          'Formula mass and estimated key outputs per serving',
        ),
        const SizedBox(height: 17),
        if (formulas.isEmpty)
          const Text(
            'No formulations were returned for this run.',
            style: TextStyle(color: AlgaColors.muted),
          ),
        for (final raw in formulas)
          if (raw is Map) _formulaRow(raw),
      ],
    ),
  );

  Widget _formulaRow(Map formula) {
    final id = '${formula['id']}';
    final isSelected = id == _selectedFormula()?['id'];
    final ingredients = formula['ingredients'] as List? ?? [];
    final estimate = nutrition[id] as Map?;
    final perServing = estimate?['per_serving'] as Map?;
    final total = formula['total_g'] is num
        ? (formula['total_g'] as num).toDouble()
        : 0.0;
    return Container(
      margin: const EdgeInsets.only(bottom: 8),
      padding: const EdgeInsets.all(13),
      decoration: BoxDecoration(
        color: isSelected ? const Color(0xfff3f8f1) : Colors.white,
        border: Border.all(
          color: isSelected ? AlgaColors.green : AlgaColors.line,
        ),
        borderRadius: BorderRadius.circular(8),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          Row(
            children: [
              Container(
                width: 42,
                height: 34,
                alignment: Alignment.center,
                decoration: BoxDecoration(
                  color: isSelected ? AlgaColors.forest : AlgaColors.pale,
                  borderRadius: BorderRadius.circular(5),
                ),
                child: Text(
                  id,
                  style: TextStyle(
                    color: isSelected ? Colors.white : AlgaColors.forest,
                    fontWeight: FontWeight.w800,
                  ),
                ),
              ),
              const SizedBox(width: 10),
              Expanded(
                child: Text(
                  '${formula['name']}',
                  style: const TextStyle(
                    fontSize: 13,
                    fontWeight: FontWeight.w700,
                  ),
                  maxLines: 2,
                ),
              ),
              Text(
                '${number(total)} g',
                style: const TextStyle(fontSize: 12, color: AlgaColors.muted),
              ),
            ],
          ),
          const SizedBox(height: 11),
          ClipRRect(
            borderRadius: BorderRadius.circular(4),
            child: SizedBox(
              height: 10,
              child: Row(
                children: [
                  for (var i = 0; i < ingredients.length; i++)
                    if (ingredients[i] is Map &&
                        ingredients[i]['grams'] is num &&
                        total > 0)
                      Expanded(
                        flex:
                            (((ingredients[i]['grams'] as num).toDouble() /
                                        total) *
                                    1000)
                                .round()
                                .clamp(1, 1000),
                        child: Container(
                          color: [
                            AlgaColors.forest,
                            const Color(0xff8ba88e),
                            const Color(0xffb8c9b3),
                            const Color(0xffc7b09e),
                            const Color(0xffded7c6),
                          ][i % 5],
                        ),
                      ),
                ],
              ),
            ),
          ),
          const SizedBox(height: 8),
          Wrap(
            spacing: 13,
            runSpacing: 4,
            children: [
              for (final ingredient in ingredients)
                if (ingredient is Map)
                  Text(
                    '${label(ingredient['ingredient_id'])} ${number(ingredient['grams'])} g',
                    style: const TextStyle(
                      fontSize: 10,
                      color: AlgaColors.muted,
                    ),
                  ),
            ],
          ),
          const SizedBox(height: 9),
          Text(
            'Protein: ${number(perServing?['protein_g'])} g   ·   Energy: ${number(perServing?['energy_kcal'], decimals: 0)} kcal',
            style: const TextStyle(fontSize: 11, fontWeight: FontWeight.w700),
          ),
          if ((formula['warnings'] as List? ?? []).isNotEmpty)
            details('Formula warnings', formula['warnings']),
        ],
      ),
    );
  }

  Widget _nutrition() => AlgaCard(
    child: Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        heading(
          'Nutrition estimate',
          'Calculated composition; missing values remain unknown',
        ),
        const SizedBox(height: 14),
        Text(
          '${impact['explanation'] ?? 'No nutrition comparison available.'}',
          style: const TextStyle(fontSize: 12, color: AlgaColors.muted),
        ),
        const SizedBox(height: 12),
        if (nutrition.isEmpty)
          const Text(
            'No composition estimates were returned.',
            style: TextStyle(color: AlgaColors.muted),
          ),
        for (final entry in nutrition.entries)
          if (entry.value is Map) _nutritionRow(entry.key, entry.value as Map),
        const SizedBox(height: 5),
        Text(
          'Estimated protein-density change: ${number(impact['nutrition_change_pct'])}%  ·  Sensory change: unknown  ·  Panel participants: 0',
          style: const TextStyle(fontSize: 11, color: AlgaColors.muted),
        ),
      ],
    ),
  );

  Widget _nutritionRow(String id, Map estimate) {
    final perServing = estimate['per_serving'] as Map? ?? {};
    return ExpansionTile(
      tilePadding: EdgeInsets.zero,
      title: Text(
        '$id · composition estimate',
        style: const TextStyle(fontSize: 13, fontWeight: FontWeight.w700),
      ),
      subtitle: Text(
        'Protein ${number(perServing['protein_g'])} g  ·  Energy ${number(perServing['energy_kcal'], decimals: 0)} kcal',
        style: const TextStyle(fontSize: 11),
      ),
      children: [
        for (final nutrient in perServing.entries)
          ListTile(
            dense: true,
            contentPadding: EdgeInsets.zero,
            title: Text(
              '${nutrient.key}: ${number(nutrient.value, decimals: 3)} per serving',
              style: const TextStyle(fontSize: 12),
            ),
            subtitle: Text(
              'Per 100 g: ${number((estimate['per_100g'] as Map?)?[nutrient.key], decimals: 3)} · Missing forms: ${((estimate['missing'] as Map?)?[nutrient.key] as List? ?? []).join(', ')}',
              style: const TextStyle(fontSize: 11),
            ),
          ),
        Text(
          'Protein g per 100 kcal: ${number(estimate['protein_g_per_100_kcal'], decimals: 3)}',
          style: const TextStyle(fontSize: 11),
        ),
        for (final warning in estimate['warnings'] as List? ?? [])
          Text(
            '$warning',
            style: const TextStyle(fontSize: 11, color: AlgaColors.amber),
          ),
        details('Nutrition source records', estimate['records'] ?? []),
      ],
    );
  }

  Widget _evidence(BuildContext context) {
    final generation = result['generation'] as Map?;
    final claims = generation?['claims'] as List? ?? [];
    final evidence = result['evidence'] as List? ?? [];
    return AlgaCard(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          heading(
            'Why this candidate',
            'Cited context and evidence used in screening',
          ),
          const SizedBox(height: 12),
          Text(
            '${generation?['method'] ?? 'No generated explanation'} · ${generation?['status'] ?? 'unavailable'}  ·  ${evidence.length} retrieved records',
            style: const TextStyle(fontSize: 11, color: AlgaColors.muted),
          ),
          if (generation?['limitation'] != null)
            Padding(
              padding: const EdgeInsets.only(top: 7),
              child: Text(
                '${generation!['limitation']}',
                style: const TextStyle(fontSize: 11, color: AlgaColors.muted),
              ),
            ),
          const SizedBox(height: 10),
          if (claims.isEmpty)
            const Text(
              'No cited explanation was returned.',
              style: TextStyle(fontSize: 12, color: AlgaColors.muted),
            ),
          for (final item in claims)
            if (item is Map)
              Container(
                margin: const EdgeInsets.only(bottom: 8),
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  border: Border.all(color: AlgaColors.line),
                  borderRadius: BorderRadius.circular(7),
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      '${item['text']}',
                      style: const TextStyle(fontSize: 12, height: 1.45),
                    ),
                    const SizedBox(height: 8),
                    Text(
                      '${(item['citation'] as Map?)?['chunk_id'] ?? 'Citation'} · ${(item['citation'] as Map?)?['source_id'] ?? 'source unknown'}',
                      style: const TextStyle(
                        fontSize: 10,
                        fontWeight: FontWeight.w800,
                        color: AlgaColors.green,
                      ),
                    ),
                    details('Citation provenance', item['citation']),
                  ],
                ),
              ),
          if (claims.isEmpty && evidence.isNotEmpty) ...[
            const SizedBox(height: 8),
            for (final item in evidence.take(3))
              if (item is Map)
                Text(
                  '${item['source_title'] ?? item['title'] ?? item['source_id']}: ${item['claim_summary'] ?? item['text'] ?? ''}',
                  style: const TextStyle(fontSize: 12, height: 1.5),
                ),
          ],
        ],
      ),
    );
  }

  Widget _checks() {
    final verdicts = screening['verdicts'] as Map? ?? {};
    return AlgaCard(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          heading(
            'Screening checks',
            'Automated checks against experiment constraints',
          ),
          const SizedBox(height: 12),
          if (screening['scope'] != null)
            Text(
              '${screening['scope']}',
              style: const TextStyle(fontSize: 11, color: AlgaColors.muted),
            ),
          if (screening['reason'] != null)
            Padding(
              padding: const EdgeInsets.only(top: 7),
              child: Text(
                '${screening['reason']}',
                style: const TextStyle(fontSize: 12, color: AlgaColors.amber),
              ),
            ),
          if (verdicts.isEmpty)
            const Padding(
              padding: EdgeInsets.only(top: 12),
              child: Text(
                'No screening verdicts were returned.',
                style: TextStyle(color: AlgaColors.muted),
              ),
            ),
          for (final entry in verdicts.entries)
            _checkRow('${entry.key}', entry.value as List? ?? []),
          if (screening.isNotEmpty)
            details('Search and comparison basis', screening),
        ],
      ),
    );
  }

  Widget _checkRow(String id, List reasons) => Container(
    margin: const EdgeInsets.only(top: 9),
    padding: const EdgeInsets.all(10),
    decoration: BoxDecoration(
      border: Border.all(color: AlgaColors.line),
      borderRadius: BorderRadius.circular(7),
    ),
    child: Row(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Icon(
          reasons.isEmpty ? Icons.check_circle : Icons.warning_amber_rounded,
          size: 18,
          color: reasons.isEmpty ? AlgaColors.green : AlgaColors.amber,
        ),
        const SizedBox(width: 9),
        Expanded(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                id,
                style: const TextStyle(
                  fontSize: 12,
                  fontWeight: FontWeight.w800,
                ),
              ),
              Text(
                reasons.isEmpty
                    ? 'Passed computational checks'
                    : reasons.join(' '),
                style: const TextStyle(
                  fontSize: 11,
                  color: AlgaColors.muted,
                  height: 1.4,
                ),
              ),
            ],
          ),
        ),
      ],
    ),
  );
}
