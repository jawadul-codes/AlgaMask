import 'package:flutter/material.dart';

class AlgaColors {
  static const forest = Color(0xff103d30);
  static const deep = Color(0xff0a2e25);
  static const green = Color(0xff176b4e);
  static const lime = Color(0xffb8df55);
  static const canvas = Color(0xfff7f6f1);
  static const ink = Color(0xff142321);
  static const muted = Color(0xff64716d);
  static const line = Color(0xffdce4dc);
  static const pale = Color(0xffeef4ed);
  static const amber = Color(0xffa76405);
  static const amberPale = Color(0xfffff5df);
}

class AlgaCard extends StatelessWidget {
  const AlgaCard({
    super.key,
    required this.child,
    this.padding = const EdgeInsets.all(24),
  });
  final Widget child;
  final EdgeInsets padding;

  @override
  Widget build(BuildContext context) => Material(
    color: Colors.white,
    elevation: 1,
    shadowColor: const Color(0x160a2e25),
    shape: RoundedRectangleBorder(
      side: const BorderSide(color: AlgaColors.line),
      borderRadius: BorderRadius.circular(12),
    ),
    clipBehavior: Clip.antiAlias,
    child: Padding(padding: padding, child: child),
  );
}

class AlgaShell extends StatelessWidget {
  const AlgaShell({
    super.key,
    required this.child,
    required this.selected,
    this.onNew,
    this.onHistory,
  });
  final Widget child;
  final String selected;
  final VoidCallback? onNew;
  final VoidCallback? onHistory;

  @override
  Widget build(BuildContext context) => LayoutBuilder(
    builder: (context, constraints) {
      final desktop = constraints.maxWidth >= 900;
      return Scaffold(
        backgroundColor: AlgaColors.canvas,
        appBar: desktop
            ? null
            : AppBar(
                backgroundColor: AlgaColors.forest,
                foregroundColor: Colors.white,
                title: const Text(
                  'AlgaMask',
                  style: TextStyle(fontWeight: FontWeight.w800),
                ),
                actions: [
                  if (onNew != null)
                    IconButton(
                      tooltip: 'New experiment',
                      onPressed: onNew,
                      icon: const Icon(Icons.science_outlined),
                    ),
                  if (onHistory != null)
                    IconButton(
                      tooltip: 'Experiment history',
                      onPressed: onHistory,
                      icon: const Icon(Icons.history),
                    ),
                ],
              ),
        body: Row(
          children: [
            if (desktop)
              Container(
                width: 244,
                decoration: const BoxDecoration(
                  gradient: LinearGradient(
                    begin: Alignment.topLeft,
                    end: Alignment.bottomRight,
                    colors: [AlgaColors.forest, AlgaColors.deep],
                  ),
                ),
                padding: const EdgeInsets.fromLTRB(16, 28, 16, 24),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.stretch,
                  children: [
                    const Padding(
                      padding: EdgeInsets.fromLTRB(12, 0, 0, 36),
                      child: Row(
                        children: [
                          Icon(
                            Icons.spa_rounded,
                            color: AlgaColors.lime,
                            size: 30,
                          ),
                          SizedBox(width: 12),
                          Text(
                            'AlgaMask',
                            style: TextStyle(
                              color: Colors.white,
                              fontSize: 24,
                              fontWeight: FontWeight.w800,
                              letterSpacing: -0.8,
                            ),
                          ),
                        ],
                      ),
                    ),
                    _nav(
                      'New experiment',
                      Icons.science_outlined,
                      selected == 'new',
                      onNew,
                    ),
                    const SizedBox(height: 8),
                    _nav(
                      'History',
                      Icons.history,
                      selected == 'history',
                      onHistory,
                    ),
                    const Spacer(),
                    const Divider(color: Color(0x40ffffff)),
                    const Padding(
                      padding: EdgeInsets.fromLTRB(12, 14, 12, 0),
                      child: Text(
                        'Experimental formulation screening\nResearch use only',
                        style: TextStyle(
                          color: Color(0xffb8ccc3),
                          fontSize: 12,
                          height: 1.6,
                        ),
                      ),
                    ),
                  ],
                ),
              ),
            Expanded(child: child),
          ],
        ),
      );
    },
  );

  Widget _nav(String label, IconData icon, bool active, VoidCallback? onTap) =>
      Material(
        color: active ? const Color(0xff1a634c) : Colors.transparent,
        borderRadius: BorderRadius.circular(8),
        child: InkWell(
          borderRadius: BorderRadius.circular(8),
          onTap: onTap,
          child: Padding(
            padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 15),
            child: Row(
              children: [
                Icon(
                  icon,
                  size: 22,
                  color: active ? Colors.white : const Color(0xffc5d7ce),
                ),
                const SizedBox(width: 15),
                Text(
                  label,
                  style: TextStyle(
                    color: active ? Colors.white : const Color(0xffc5d7ce),
                    fontWeight: active ? FontWeight.w700 : FontWeight.w500,
                  ),
                ),
              ],
            ),
          ),
        ),
      );
}

class AlgaNotice extends StatelessWidget {
  const AlgaNotice({super.key, required this.text});
  final String text;

  @override
  Widget build(BuildContext context) => Container(
    padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 12),
    decoration: BoxDecoration(
      color: AlgaColors.amberPale,
      border: Border.all(color: const Color(0xffefd69e)),
      borderRadius: BorderRadius.circular(8),
    ),
    child: Row(
      children: [
        const Icon(
          Icons.warning_amber_rounded,
          size: 20,
          color: AlgaColors.amber,
        ),
        const SizedBox(width: 10),
        Expanded(
          child: Text(
            text,
            style: const TextStyle(
              color: Color(0xff80500c),
              fontSize: 12,
              height: 1.35,
            ),
          ),
        ),
      ],
    ),
  );
}
