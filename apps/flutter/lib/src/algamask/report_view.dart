import 'dart:convert';

import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:url_launcher/url_launcher.dart';

import 'api_client.dart';

class ReportView extends StatelessWidget {
  const ReportView({super.key, required this.result});
  final Map<String, dynamic> result;

  Widget section(String title, List<Widget> children) => Padding(
    padding: const EdgeInsets.only(top: 20),
    child: Card(
      child: Padding(
        padding: const EdgeInsets.all(20),
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
    ),
  );

  @override
  Widget build(BuildContext context) => Column(
    crossAxisAlignment: CrossAxisAlignment.start,
    children: [
      Text(
        result['status'] == 'report_ready'
            ? 'Your concept report'
            : 'No feasible mock formulation',
        style: Theme.of(context).textTheme.headlineMedium,
      ),
      if (result['status'] != 'report_ready')
        const Text(
          'An exclusion conflicts with the available mock recipe. Change the exclusions or extend the ingredient library. No rejected recipe is returned.',
        ),
      const SizedBox(height: 12),
      Wrap(
        spacing: 12,
        runSpacing: 8,
        children: [
          OutlinedButton.icon(
            icon: const Icon(Icons.copy),
            label: const Text('Copy JSON'),
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
          ),
          OutlinedButton.icon(
            icon: const Icon(Icons.print_outlined),
            label: const Text('Print-ready report'),
            onPressed: () async {
              try {
                final opened = await launchUrl(
                  Uri.parse('$apiBase/runs/${result['run_id']}/report'),
                  webOnlyWindowName: '_blank',
                );
                if (!opened) {
                  throw StateError('Could not open report');
                }
              } catch (_) {
                if (context.mounted) {
                  ScaffoldMessenger.of(context).showSnackBar(
                    const SnackBar(
                      content: Text(
                        'Could not open report. Check the backend and retry.',
                      ),
                    ),
                  );
                }
              }
            },
          ),
        ],
      ),
      section('Six-agent trace', [
        for (final step in result['trace'])
          ExpansionTile(
            title: Text('${step['agent']} · ${step['state']}'),
            subtitle: Text(step['summary'] as String),
            children: [
              Padding(
                padding: const EdgeInsets.all(12),
                child: SelectableText(
                  const JsonEncoder.withIndent('  ').convert(step['output']),
                ),
              ),
            ],
          ),
      ]),
      section('Sensory profile · illustrative risks', [
        const Text('Molecular structures and evidence links are pending.'),
        for (final item in result['sensory_map'])
          Padding(
            padding: const EdgeInsets.symmetric(vertical: 8),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(item['category'] as String),
                const SizedBox(height: 6),
                LinearProgressIndicator(
                  value: (item['relative_risk'] as num).toDouble(),
                  minHeight: 8,
                ),
              ],
            ),
          ),
      ]),
      section('Controls & generated concepts', [
        for (final formula in [
          ...result['controls'],
          ...result['formulations'],
        ])
          ExpansionTile(
            initiallyExpanded: formula['id'] == 'A1',
            title: Text('${formula['id']} · ${formula['name']}'),
            subtitle: Text('${formula['total_g']} g · assumed for demo'),
            children: [
              for (final ingredient in formula['ingredients'])
                ListTile(
                  title: Text('${ingredient['ingredient_id']}'),
                  subtitle: Text('${ingredient['role']}'),
                  trailing: Text('${ingredient['grams']} g'),
                ),
              const Padding(
                padding: EdgeInsets.all(12),
                child: Text(
                  'Score / confidence: unavailable. Screening validation pending.',
                ),
              ),
            ],
          ),
      ]),
      section('Evidence placeholders', [
        for (final item in result['evidence'])
          ExpansionTile(
            title: Text(item['title'] as String),
            subtitle: Text('${item['chunk_id']} · ${item['status']}'),
            children: [
              Padding(
                padding: const EdgeInsets.all(12),
                child: Text(
                  '${item['text']} Source: ${item['source_id']} (synthetic; no external citation).',
                ),
              ),
            ],
          ),
      ]),
      section('B0 → A0 → A1 impact comparison', [
        const Text(
          'Nutrition change: unknown\nSensory change: unknown\nPanel participants: 0',
        ),
        const SizedBox(height: 12),
        Text(result['impact']['explanation'] as String),
      ]),
      section('Limitations & next experiment', [
        for (final item in result['limitations'])
          Padding(
            padding: const EdgeInsets.only(bottom: 6),
            child: Text('• $item'),
          ),
      ]),
    ],
  );
}
