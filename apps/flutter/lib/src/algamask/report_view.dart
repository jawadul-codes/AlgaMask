import 'dart:convert';

import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:url_launcher/url_launcher.dart';

class ReportView extends StatelessWidget {
  const ReportView({super.key, required this.result, required this.reportUri});
  final Map<String, dynamic> result;
  final Uri reportUri;
  String number(dynamic value) =>
      value is num ? value.toStringAsFixed(3) : 'unknown';
  Widget section(String title, List<Widget> children) => Card(
    child: Padding(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          Text(
            title,
            style: const TextStyle(fontSize: 20, fontWeight: FontWeight.w600),
          ),
          const SizedBox(height: 12),
          ...children,
        ],
      ),
    ),
  );
  Widget details(String title, dynamic data) => ExpansionTile(
    title: Text(title),
    children: [
      Padding(
        padding: const EdgeInsets.all(12),
        child: SelectableText(const JsonEncoder.withIndent('  ').convert(data)),
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

  @override
  Widget build(BuildContext context) {
    final status = result['status'];
    final impact = result['impact'] as Map;
    final nutrition = impact['nutrition'] as Map? ?? {};
    final generation = result['generation'] as Map?;
    final retrieval = result['retrieval'] as Map?;
    final mode = result['mode'] == 'mock'
        ? 'MOCK · synthetic fixtures'
        : result['mode'] == 'rag_development'
        ? 'LOCAL RAG · development data'
        : 'LOCAL RAG · released evidence';
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        Text(
          status == 'report_ready'
              ? 'Your experimental report'
              : status == 'generation_failed'
              ? 'Evidence explanation blocked'
              : 'Insufficient data or unmet constraints',
          style: Theme.of(context).textTheme.headlineMedium,
        ),
        Text(mode),
        const Text(
          'Not production-approved. Arithmetic checks are not scientific or allergen-safety approval.',
        ),
        if (status != 'report_ready')
          const Text(
            'No verified candidate was returned. See the screening checks and workflow trace; this does not prove that your goal is impossible.',
          ),
        details('Submitted settings', result['request']),
        Wrap(
          spacing: 8,
          children: [
            OutlinedButton(
              onPressed: () async {
                await Clipboard.setData(
                  ClipboardData(
                    text: const JsonEncoder.withIndent('  ').convert(result),
                  ),
                );
                if (context.mounted) {
                  ScaffoldMessenger.of(context).showSnackBar(
                    const SnackBar(content: Text('Run JSON copied.')),
                  );
                }
              },
              child: const Text('Copy JSON'),
            ),
            OutlinedButton(
              onPressed: () => open(context, reportUri),
              child: const Text('Print-ready report'),
            ),
          ],
        ),
        if (retrieval != null)
          section('Dataset provenance', [
            Text(
              'Dataset: ${retrieval['dataset_version']} · Index: ${retrieval['index_version']}',
            ),
            SelectableText('Dataset hash: ${retrieval['dataset_hash']}'),
          ]),
        if (generation != null)
          section('Cited evidence explanation', [
            Text('${generation['method']} · ${generation['status']}'),
            Text('${generation['limitation'] ?? ''}'),
            for (final claim in generation['claims'] ?? [])
              Padding(
                padding: const EdgeInsets.only(top: 12),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text('${claim['text']}'),
                    Text(
                      'Citation: ${claim['citation']['chunk_id']} · ${claim['citation']['source_id']}',
                    ),
                    details('Citation provenance', claim['citation']),
                  ],
                ),
              ),
          ]),
        section('Controls and screened candidates', [
          for (final formula in [
            ...result['controls'],
            ...result['formulations'],
          ])
            ExpansionTile(
              title: Text('${formula['id']} · ${formula['name']}'),
              subtitle: Text(
                '${number(formula['total_g'])} g · ${formula['status']}',
              ),
              children: [
                for (final ingredient in formula['ingredients'])
                  ListTile(
                    title: Text('${ingredient['ingredient_id']}'),
                    trailing: Text('${number(ingredient['grams'])} g'),
                  ),
                for (final warning in formula['warnings'] ?? [])
                  Text('$warning'),
              ],
            ),
        ]),
        section('Estimated nutrition', [
          Text('${impact['explanation']}'),
          Text(
            'Estimated protein-density change (%): ${number(impact['nutrition_change_pct'])}',
          ),
          const Text('Sensory change: unknown · Panel participants: 0'),
          for (final entry in nutrition.entries)
            ExpansionTile(
              title: Text('${entry.key} · composition estimate'),
              children: [
                for (final nutrient
                    in (entry.value['per_serving'] as Map).entries)
                  ListTile(
                    title: Text(
                      '${nutrient.key}: ${number(nutrient.value)} per serving',
                    ),
                    subtitle: Text(
                      'Per 100 g: ${number(entry.value['per_100g'][nutrient.key])}\nMissing forms: ${(entry.value['missing'][nutrient.key] as List).join(', ')}',
                    ),
                  ),
                Text(
                  'Protein g per 100 kcal: ${number(entry.value['protein_g_per_100_kcal'])}',
                ),
                for (final warning in entry.value['warnings']) Text('$warning'),
                details('Nutrition source records', entry.value['records']),
              ],
            ),
        ]),
        if (impact['screening'] != null)
          section('Screening checks and assumptions', [
            Text('${impact['screening']['scope']}'),
            if (impact['screening']['reason'] != null)
              Text('${impact['screening']['reason']}'),
            for (final entry
                in (impact['screening']['verdicts'] as Map).entries)
              Text(
                '${entry.key}: ${(entry.value as List).isEmpty ? 'Passed computational checks' : (entry.value as List).join(' ')}',
              ),
            details('Search and control comparison basis', impact['screening']),
          ]),
        section('Retrieved evidence', [
          for (final item in result['evidence'])
            ExpansionTile(
              title: Text(
                '${item['source_title'] ?? item['title'] ?? item['source_id']}',
              ),
              subtitle: Text(
                '${item['chunk_id']} · ${item['review_status'] ?? item['status']}',
              ),
              children: [
                Text('${item['claim_summary'] ?? item['text']}'),
                Text(
                  'Source: ${item['source_id']} · Location: ${item['source_location'] ?? 'synthetic'}',
                ),
                if (item['source_url'] is String &&
                    [
                      'http',
                      'https',
                    ].contains(Uri.tryParse(item['source_url'])?.scheme))
                  TextButton(
                    onPressed: () =>
                        open(context, Uri.parse(item['source_url'])),
                    child: const Text('Open source'),
                  ),
              ],
            ),
        ]),
        section('Six-agent trace', [
          for (final step in result['trace'])
            details(
              '${step['agent']} · ${step['state']} · ${step['status']}',
              step,
            ),
        ]),
        section('Limitations', [
          for (final item in result['limitations']) Text('• $item'),
        ]),
      ],
    );
  }
}
