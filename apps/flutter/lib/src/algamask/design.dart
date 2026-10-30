import 'package:flutter/material.dart';

/// Palette shared with the landing page (docs/design/LANDING_MASTER_PROMPT.md).
class AlgaColors {
  static const sage = Color(0xffbcd2c0);
  static const paper = Color(0xffeceeea);
  static const forest = Color(0xff103d30);
  static const deep = Color(0xff0a2e25);
  static const green = Color(0xff176b4e);
  static const lime = Color(0xffb8df55);
  static const canvas = sage;
  static const ink = Color(0xff0f2a1f);
  static const muted = Color(0xff4f5d58);
  static const line = Color(0xffdfe3dc);
  static const pale = Color(0xfff7f8f4);
  static const amber = Color(0xffa76405);
  static const amberPale = Color(0xfffff5df);
}

/// Urbanist at an explicit weight (the bundled face is a variable font).
TextStyle algaType(
  double size, {
  double weight = 500,
  Color? color = AlgaColors.ink,
  double tracking = 0,
  double height = 1.3,
}) => TextStyle(
  fontFamily: 'Urbanist',
  fontSize: size,
  fontWeight: FontWeight.values[((weight / 100).round() - 1).clamp(0, 8)],
  fontVariations: [FontVariation('wght', weight)],
  color: color,
  letterSpacing: size * tracking,
  height: height,
);

class AlgaCard extends StatelessWidget {
  const AlgaCard({
    super.key,
    required this.child,
    this.padding,
  });
  final Widget child;

  /// Defaults to 32, or 20 on phone widths.
  final EdgeInsets? padding;

  @override
  // Material (not a decorated box) so list tiles inside keep their ink.
  Widget build(BuildContext context) => Material(
    color: AlgaColors.paper,
    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(30)),
    clipBehavior: Clip.antiAlias,
    child: Padding(
      padding:
          padding ??
          EdgeInsets.all(MediaQuery.sizeOf(context).width < 600 ? 20 : 32),
      child: child,
    ),
  );
}

/// App frame: a plain bar (wordmark, two destinations) over the sage field.
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
      final narrow = constraints.maxWidth < 700;
      final gutter = narrow ? 10.0 : 28.0;
      return Scaffold(
        backgroundColor: AlgaColors.sage,
        body: SafeArea(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              Padding(
                padding: EdgeInsets.fromLTRB(gutter + 8, 14, gutter, 4),
                child: Row(
                  children: [
                    Semantics(
                      button: true,
                      label: 'AlgaMask home',
                      child: InkWell(
                        borderRadius: BorderRadius.circular(8),
                        onTap: () =>
                            Navigator.of(context)
                                .popUntil((route) => route.isFirst),
                        child: Padding(
                          padding: const EdgeInsets.symmetric(vertical: 8),
                          child: Text(
                            'ALGAMASK',
                            style: algaType(20, weight: 700, tracking: 0.06),
                          ),
                        ),
                      ),
                    ),
                    const Spacer(),
                    _nav(
                      'New experiment',
                      'New experiment',
                      Icons.science_outlined,
                      selected == 'new',
                      onNew,
                      narrow,
                    ),
                    const SizedBox(width: 8),
                    _nav(
                      'History',
                      'Experiment history',
                      Icons.history,
                      selected == 'history',
                      onHistory,
                      narrow,
                    ),
                  ],
                ),
              ),
              Expanded(child: child),
            ],
          ),
        ),
      );
    },
  );

  Widget _nav(
    String label,
    String tooltip,
    IconData icon,
    bool active,
    VoidCallback? onTap,
    bool narrow,
  ) {
    final fg = active ? Colors.white : AlgaColors.ink;
    final content = narrow
        ? Icon(icon, size: 20, color: fg)
        : Text(label, style: algaType(15, weight: 600, color: fg));
    return Tooltip(
      message: tooltip,
      child: Material(
        color: active ? AlgaColors.ink : Colors.transparent,
        shape: const StadiumBorder(),
        child: InkWell(
          customBorder: const StadiumBorder(),
          onTap: active ? null : onTap,
          child: Padding(
            padding: EdgeInsets.symmetric(
              horizontal: narrow ? 14 : 22,
              vertical: 13,
            ),
            child: content,
          ),
        ),
      ),
    );
  }
}

class AlgaNotice extends StatelessWidget {
  const AlgaNotice({super.key, required this.text});
  final String text;

  @override
  Widget build(BuildContext context) => Container(
    padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 14),
    decoration: BoxDecoration(
      color: AlgaColors.amberPale,
      borderRadius: BorderRadius.circular(14),
    ),
    child: Row(
      crossAxisAlignment: CrossAxisAlignment.start,
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
            style: algaType(
              14,
              weight: 500,
              color: const Color(0xff6b430a),
              height: 1.45,
            ),
          ),
        ),
      ],
    ),
  );
}
