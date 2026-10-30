import 'dart:math' as math;

import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:flutter/scheduler.dart';

import 'design.dart';
import 'input_screen.dart';

const _sage = Color(0xffbcd2c0);
const _paper = Color(0xffeceeea);
const _ink = Color(0xff0f2a1f);
const _hillDark = Color(0xff23561f);
const _display = 'Urbanist';

TextStyle _type(
  double size, {
  double weight = 500,
  Color? color = _ink,
  double tracking = 0,
  double height = 1.2,
}) => TextStyle(
  fontFamily: _display,
  fontSize: size,
  fontVariations: [FontVariation('wght', weight)],
  color: color,
  letterSpacing: size * tracking,
  height: height,
);

/// Eased 0..1 progress of [p] through the window [a]..[b].
double _seg(
  double p,
  double a,
  double b, [
  Curve curve = Curves.easeInOutCubic,
]) => curve.transform(((p - a) / (b - a)).clamp(0.0, 1.0));

class LandingScreen extends StatefulWidget {
  const LandingScreen({super.key});

  @override
  State<LandingScreen> createState() => _LandingScreenState();
}

class _LandingScreenState extends State<LandingScreen>
    with SingleTickerProviderStateMixin {
  final _scroll = ScrollController();
  final _checksKey = GlobalKey();
  final _closeKey = GlobalKey();
  // Animation progress eases toward the scroll position, so wheel steps glide.
  final _shown = ValueNotifier<double>(0);
  late final Ticker _ticker;
  double _travel = 1;

  @override
  void initState() {
    super.initState();
    _ticker = createTicker(_follow)..start();
  }

  void _follow(Duration _) {
    final target = _scroll.hasClients
        ? (_scroll.offset / _travel).clamp(0.0, 1.0)
        : 0.0;
    final gap = target - _shown.value;
    if (gap.abs() > 0.0005) {
      _shown.value += gap * 0.16;
    } else if (gap != 0) {
      _shown.value = target;
    }
  }

  @override
  void dispose() {
    _ticker.dispose();
    _shown.dispose();
    _scroll.dispose();
    super.dispose();
  }

  void _openLab() =>
      Navigator.of(context)
          .push(MaterialPageRoute<void>(builder: (_) => const InputScreen()));

  void _jump(GlobalKey key) => Scrollable.ensureVisible(
    key.currentContext!,
    duration: const Duration(milliseconds: 700),
    curve: Curves.easeOutCubic,
  );

  @override
  Widget build(BuildContext context) => Scaffold(
    backgroundColor: _sage,
    body: LayoutBuilder(
      builder: (context, box) {
        final vh = box.maxHeight;
        final narrow = box.maxWidth < 760;
        final gutter = narrow ? 10.0 : 28.0;
        // The hero stays pinned while the visitor scrolls this far.
        final travel = _travel = vh * 1.6;
        return Scrollbar(
          controller: _scroll,
          child: SingleChildScrollView(
            controller: _scroll,
            child: Column(
              children: [
                SizedBox(
                  height: vh + travel,
                  child: AnimatedBuilder(
                    animation: _scroll,
                    builder: (context, _) {
                      final offset = _scroll.hasClients
                          ? _scroll.offset.clamp(0.0, travel)
                          : 0.0;
                      return Stack(
                        children: [
                          Positioned(
                            top: offset,
                            left: 0,
                            right: 0,
                            height: vh,
                            child: RepaintBoundary(
                              child: Padding(
                                padding: EdgeInsets.all(gutter),
                                child: _Hero(
                                  progress: _shown,
                                  narrow: narrow,
                                  onOpenLab: _openLab,
                                  onChecks: () => _jump(_checksKey),
                                  onEvidence: () => _jump(_closeKey),
                                ),
                              ),
                            ),
                          ),
                        ],
                      );
                    },
                  ),
                ),
                Padding(
                  key: _checksKey,
                  padding: EdgeInsets.fromLTRB(gutter, 0, gutter, gutter),
                  child: _Checks(narrow: narrow),
                ),
                Padding(
                  key: _closeKey,
                  padding: EdgeInsets.fromLTRB(gutter, 0, gutter, gutter),
                  child: _Close(narrow: narrow, onOpenLab: _openLab),
                ),
                Padding(
                  padding: EdgeInsets.symmetric(horizontal: gutter),
                  child: const _Wordmark(),
                ),
              ],
            ),
          ),
        );
      },
    ),
  );
}

class _Hero extends StatelessWidget {
  const _Hero({
    required this.progress,
    required this.narrow,
    required this.onOpenLab,
    required this.onChecks,
    required this.onEvidence,
  });
  final ValueListenable<double> progress;
  final bool narrow;
  final VoidCallback onOpenLab;
  final VoidCallback onChecks;
  final VoidCallback onEvidence;

  static String _stage(double p) => p < 0.3
      ? 'Spirulina + chlorella powder'
      : p < 0.66
      ? 'Masked with cocoa, vanilla, citrus'
      : 'Screened protein bar';

  @override
  Widget build(BuildContext context) => ClipRRect(
    borderRadius: BorderRadius.circular(narrow ? 22 : 30),
    child: ColoredBox(
      color: _paper,
      child: LayoutBuilder(
        builder: (context, box) {
          final w = box.maxWidth;
          final h = box.maxHeight;
          final word = math.min(w * (narrow ? 0.145 : 0.155), h * 0.24);
          final pad = narrow ? 20.0 : 36.0;
          final wordStyle = _type(word, tracking: -0.04, height: 1);
          final maskWidth = (TextPainter(
            text: TextSpan(text: 'MASK', style: wordStyle),
            textDirection: TextDirection.ltr,
          )..layout()).width;
          // The ingredients fill the gap below ALGAE, left of MASK and above
          // the dataset badge.
          final room = Rect.fromLTRB(
            narrow ? 0 : pad,
            narrow ? 0 : h * 0.12 + word * 1.08 + 32,
            narrow ? w : w - pad - maskWidth - 16,
            narrow ? h : h - pad * 0.6 - h * 0.2 - 64,
          );
          return Stack(
            clipBehavior: Clip.none,
            children: [
              Positioned(
                left: 0,
                right: 0,
                bottom: 0,
                height: h * (narrow ? 0.4 : 0.3),
                child: const RepaintBoundary(
                  child: CustomPaint(painter: _HillsPainter()),
                ),
              ),
              Positioned(
                left: pad - word * 0.05,
                top: h * 0.12,
                child: Text('ALGAE', style: wordStyle),
              ),
              Positioned(
                right: pad,
                top: h * 0.12 + (narrow ? 0 : word),
                child: Text('MASK', style: wordStyle),
              ),
              Positioned.fill(
                child: RepaintBoundary(
                  child: ValueListenableBuilder<double>(
                    valueListenable: progress,
                    builder: (context, p, _) =>
                        _Transition(progress: p, narrow: narrow, room: room),
                  ),
                ),
              ),
              Positioned(
                left: pad,
                top: h * 0.12 + word * 1.08,
                child: ValueListenableBuilder<double>(
                  valueListenable: progress,
                  builder: (context, p, _) => _StageChip(label: _stage(p)),
                ),
              ),
              if (!narrow) ...[
                Positioned(
                  right: pad,
                  top: h * 0.14,
                  child: const _RoundBadge(
                    image: 'assets/ingredients/chlorella.png',
                    lines: 'Research use\nonly',
                  ),
                ),
                Positioned(
                  left: pad,
                  bottom: pad * 0.6 + h * 0.2 + 16,
                  child: const _RoundBadge(
                    icon: Icons.dataset_outlined,
                    lines: 'Dataset 0.1.0-rc.5',
                  ),
                ),
                Positioned(
                  left: pad,
                  bottom: pad * 0.6,
                  height: h * 0.2,
                  child: Row(
                    children: const [
                      _MiniCard(
                        title: '27 recipes\nper run',
                        image: 'assets/ingredients/blend.png',
                      ),
                      SizedBox(width: 12),
                      _MiniCard(
                        title: 'Masker\nmatching',
                        image: 'assets/ingredients/vanilla.png',
                      ),
                    ],
                  ),
                ),
              ],
              Positioned(
                right: pad,
                bottom: pad * (narrow ? 1 : 1.1),
                width: narrow ? w - pad * 2 : math.min(420, w * 0.34),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'Screen spirulina and chlorella bars that hide '
                      'fishy, grassy off-notes, with every claim cited.',
                      style: _type(
                        narrow ? 16 : 19,
                        color: Colors.white,
                        height: 1.35,
                      ),
                    ),
                    const SizedBox(height: 16),
                    _PillButton(
                      label: 'Start screening',
                      filled: true,
                      onPressed: onOpenLab,
                    ),
                  ],
                ),
              ),
              Positioned(
                left: pad,
                right: pad,
                top: narrow ? 14 : 20,
                child: _Nav(
                  narrow: narrow,
                  onOpenLab: onOpenLab,
                  onChecks: onChecks,
                  onEvidence: onEvidence,
                ),
              ),
            ],
          );
        },
      ),
    ),
  );
}

class _Nav extends StatelessWidget {
  const _Nav({
    required this.narrow,
    required this.onOpenLab,
    required this.onChecks,
    required this.onEvidence,
  });
  final bool narrow;
  final VoidCallback onOpenLab;
  final VoidCallback onChecks;
  final VoidCallback onEvidence;

  Widget _link(String label, VoidCallback onTap) => TextButton(
    onPressed: onTap,
    style: TextButton.styleFrom(foregroundColor: _ink),
    child: Text(label, style: _type(16)),
  );

  @override
  Widget build(BuildContext context) => SizedBox(
    height: 48,
    child: Stack(
      alignment: Alignment.center,
      children: [
        if (!narrow)
          Align(
            alignment: Alignment.centerLeft,
            child: Row(
              mainAxisSize: MainAxisSize.min,
              children: [
                _link('What it checks', onChecks),
                _link('Evidence', onEvidence),
              ],
            ),
          ),
        Align(
          alignment: narrow ? Alignment.centerLeft : Alignment.center,
          child: Text(
            'ALGAMASK',
            style: _type(20, weight: 700, tracking: 0.06),
          ),
        ),
        Align(
          alignment: Alignment.centerRight,
          child: _PillButton(
            label: 'Open the lab',
            dark: true,
            onPressed: onOpenLab,
          ),
        ),
      ],
    ),
  );
}

class _PillButton extends StatelessWidget {
  const _PillButton({
    required this.label,
    required this.onPressed,
    this.filled = false,
    this.dark = false,
  });
  final String label;
  final VoidCallback onPressed;
  final bool filled;
  final bool dark;

  @override
  Widget build(BuildContext context) {
    final shape = WidgetStateProperty.all(
      StadiumBorder(
        side: BorderSide(color: filled ? Colors.white : _ink, width: 1.2),
      ),
    );
    return TextButton(
      onPressed: onPressed,
      style: ButtonStyle(
        shape: shape,
        padding: WidgetStateProperty.all(
          const EdgeInsets.symmetric(horizontal: 26, vertical: 16),
        ),
        backgroundColor: WidgetStateProperty.resolveWith(
          (s) => dark
              ? (s.contains(WidgetState.hovered) ? AlgaColors.green : _ink)
              : filled
              ? (s.contains(WidgetState.hovered)
                    ? AlgaColors.lime
                    : Colors.white)
              : (s.contains(WidgetState.hovered) ? _ink : Colors.transparent),
        ),
        foregroundColor: WidgetStateProperty.resolveWith(
          (s) => dark || (!filled && s.contains(WidgetState.hovered))
              ? Colors.white
              : _ink,
        ),
        overlayColor: WidgetStateProperty.all(const Color(0x14000000)),
      ),
      child: Text(label, style: _type(15, weight: 600, color: null)),
    );
  }
}

class _StageChip extends StatelessWidget {
  const _StageChip({required this.label});
  final String label;

  @override
  Widget build(BuildContext context) => Row(
    mainAxisSize: MainAxisSize.min,
    children: [
      AnimatedSwitcher(
        duration: const Duration(milliseconds: 260),
        child: Text(label, key: ValueKey(label), style: _type(17, weight: 600)),
      ),
    ],
  );
}

class _RoundBadge extends StatelessWidget {
  const _RoundBadge({required this.lines, this.image, this.icon});
  final String lines;
  final String? image;
  final IconData? icon;

  @override
  Widget build(BuildContext context) => Row(
    mainAxisSize: MainAxisSize.min,
    children: [
      Container(
        width: image != null ? 52 : 34,
        height: image != null ? 52 : 34,
        decoration: const BoxDecoration(
          color: AlgaColors.forest,
          shape: BoxShape.circle,
        ),
        padding: const EdgeInsets.all(5),
        child: image != null
            ? Image.asset(image!)
            : Icon(icon, color: Colors.white, size: 18),
      ),
      const SizedBox(width: 12),
      Text(lines, style: _type(16, weight: 600, height: 1.25)),
    ],
  );
}

class _MiniCard extends StatelessWidget {
  const _MiniCard({required this.title, required this.image});
  final String title;
  final String image;

  @override
  Widget build(BuildContext context) => AspectRatio(
    aspectRatio: 0.92,
    child: Container(
      decoration: BoxDecoration(
        color: const Color(0xfff7f8f4),
        borderRadius: BorderRadius.circular(14),
      ),
      padding: const EdgeInsets.fromLTRB(12, 12, 12, 0),
      child: Column(
        children: [
          Text(
            title,
            textAlign: TextAlign.center,
            style: _type(16, weight: 600, height: 1.2),
          ),
          Expanded(child: Image.asset(image, fit: BoxFit.contain)),
        ],
      ),
    ),
  );
}

/// The scroll-driven centrepiece: algae powder, maskers converging, then the bar.
class _Transition extends StatelessWidget {
  const _Transition({
    required this.progress,
    required this.narrow,
    required this.room,
  });
  final double progress;
  final bool narrow;

  /// Where the powder mounds may sit without covering the headline words.
  final Rect room;

  static const _maskers = [
    ('cocoa-spice', Offset(-1, -0.08), 0.5, -0.3),
    ('vanilla', Offset(0.62, -0.62), 0.46, 0.4),
    ('citrus', Offset(0.3, 0.7), 0.42, -0.2),
    ('cocoa-spice', Offset(-0.85, 0.5), 0.36, 0.6),
  ];

  @override
  Widget build(BuildContext context) => LayoutBuilder(
    builder: (context, box) {
      final w = box.maxWidth;
      final h = box.maxHeight;
      // The mounds reach about 0.78s left, 0.74s right, 0.3s above and
      // 0.42s below their centre.
      final s = math.max(
        0.0,
        [
          w * (narrow ? 0.56 : 0.3),
          h * 0.4,
          room.width / 1.52,
          if (!narrow) room.height / 0.72,
        ].reduce(math.min),
      );
      final c = narrow
          ? Offset(w * 0.5, h * 0.55)
          : Offset(
              room.left + 0.78 * s + (room.width - 1.52 * s) / 2,
              room.top + 0.3 * s + (room.height - 0.72 * s) / 2,
            );
      final p = progress;
      final gather = _seg(p, 0.18, 0.62);
      final fade = 1 - _seg(p, 0.5, 0.72);
      final bar = _seg(p, 0.55, 0.95, Curves.easeOutCubic);
      // Maskers wait just past the card edge and fly in to merge with the algae.
      final fly = _seg(p, 0.02, 0.6);

      Widget at(Offset o, double size, Widget child, {double turn = 0}) =>
          Positioned(
            left: o.dx - size / 2,
            top: o.dy - size / 2,
            width: size,
            height: size,
            child: turn == 0
                ? child
                : Transform.rotate(angle: turn, child: child),
          );

      Offset toward(Offset from, double t) => Offset.lerp(from, c, t)!;
      Offset offstage(Offset dir, double size) {
        final u = dir / dir.distance;
        final reach = math.min(
          u.dx == 0 ? double.infinity : (w / 2 + size) / u.dx.abs(),
          u.dy == 0 ? double.infinity : (h / 2 + size) / u.dy.abs(),
        );
        return c + u * reach;
      }

      return Stack(
        clipBehavior: Clip.none,
        children: [
          if (fade > 0) ...[
            for (final (name, dir, scale, turn) in _maskers)
              at(
                Offset.lerp(offstage(dir, s * scale), c, fly)!,
                s * scale * (1 - fly * 0.6),
                _Cutout(name, fade),
                turn: turn * (1 - fly) * 2,
              ),
            at(
              toward(c + Offset(-s * 0.3, s * 0.06), gather),
              s * 1.05 * (1 - gather * 0.55),
              _Cutout('spirulina', fade),
            ),
            at(
              toward(c + Offset(s * 0.34, s * 0.14), gather),
              s * 0.85 * (1 - gather * 0.55),
              _Cutout('chlorella', fade),
            ),
          ],
          Positioned.fill(
            child: IgnorePointer(
              child: CustomPaint(
                painter: _DustPainter(center: c, radius: s, t: gather * fade),
              ),
            ),
          ),
          if (bar > 0)
            at(
              c + Offset(0, s * 0.05),
              s * 1.5 * (0.6 + bar * 0.4),
              Opacity(
                opacity: _seg(p, 0.55, 0.75),
                child: Transform.rotate(
                  angle: -0.42 + bar * 0.28,
                  child: const RepaintBoundary(
                    child: CustomPaint(painter: _BarPainter()),
                  ),
                ),
              ),
            ),
        ],
      );
    },
  );
}

/// An ingredient cutout, decoded small and faded without a compositing layer.
class _Cutout extends StatelessWidget {
  const _Cutout(this.name, this.opacity);
  final String name;
  final double opacity;

  @override
  Widget build(BuildContext context) => Image.asset(
    'assets/ingredients/$name.png',
    cacheWidth: 512,
    filterQuality: FilterQuality.medium,
    opacity: AlwaysStoppedAnimation(opacity.clamp(0.0, 1.0)),
    gaplessPlayback: true,
  );
}

/// Green and cocoa specks pulled inward as the ingredients combine.
class _DustPainter extends CustomPainter {
  const _DustPainter({
    required this.center,
    required this.radius,
    required this.t,
  });
  final Offset center;
  final double radius;
  final double t;

  @override
  void paint(Canvas canvas, Size size) {
    if (t <= 0.01) return;
    final rnd = math.Random(7);
    final paint = Paint();
    const colors = [Color(0xff1f5d3a), Color(0xff5b7a2a), Color(0xff6b3b22)];
    for (var i = 0; i < 90; i++) {
      final a = rnd.nextDouble() * math.pi * 2;
      final r = radius * (0.5 + rnd.nextDouble() * 1.1) * (1.15 - t);
      final spin = a + t * 1.6;
      paint.color = colors[i % 3].withValues(alpha: math.sin(t * math.pi));
      canvas.drawCircle(
        center + Offset(math.cos(spin), math.sin(spin)) * r,
        1.5 + rnd.nextDouble() * 3,
        paint,
      );
    }
  }

  @override
  bool shouldRepaint(_DustPainter old) => old.t != t || old.center != center;
}

/// A chocolate-coated algae bar in three-quarter view, cut end showing the
/// green spirulina interior.
class _BarPainter extends CustomPainter {
  const _BarPainter();

  @override
  void paint(Canvas canvas, Size size) {
    final u = size.width;
    final len = u * 0.78;
    final hgt = u * 0.17;
    final dep = u * 0.16;
    final x0 = (u - len - dep * 0.7) / 2;
    final y0 = u * 0.44;
    final skew = Offset(dep * 0.7, -dep * 0.55);

    canvas.drawOval(
      Rect.fromCenter(
        center: Offset(u * 0.52, y0 + hgt + u * 0.05),
        width: len * 1.05,
        height: u * 0.09,
      ),
      Paint()
        ..color = const Color(0x55102a14)
        ..maskFilter = const MaskFilter.blur(BlurStyle.normal, 14),
    );

    final front = RRect.fromRectAndRadius(
      Rect.fromLTWH(x0, y0, len, hgt),
      Radius.circular(hgt * 0.22),
    );
    final top = Path()
      ..moveTo(x0 + hgt * 0.1, y0)
      ..lineTo(x0 + len - hgt * 0.1, y0)
      ..lineTo(x0 + len - hgt * 0.1 + skew.dx, y0 + skew.dy)
      ..lineTo(x0 + hgt * 0.1 + skew.dx, y0 + skew.dy)
      ..close();
    final end = Path()
      ..moveTo(x0 + len, y0 + hgt * 0.12)
      ..lineTo(x0 + len + skew.dx * 0.97, y0 + skew.dy + hgt * 0.08)
      ..lineTo(x0 + len + skew.dx * 0.97, y0 + skew.dy + hgt * 0.9)
      ..lineTo(x0 + len, y0 + hgt * 0.97)
      ..close();

    canvas.drawPath(top, Paint()..color = const Color(0xff5a3826));
    canvas.drawRRect(front, Paint()..color = const Color(0xff3a2216));

    // Cut end: spirulina-green crumb with crisp and seed flecks.
    canvas.drawPath(end, Paint()..color = const Color(0xff2d5a35));
    canvas.save();
    canvas.clipPath(end);
    final rnd = math.Random(3);
    final bounds = end.getBounds();
    const flecks = [
      Color(0xff3f7a46),
      Color(0xffd9c79a),
      Color(0xff1b3a22),
      Color(0xff6f9a4a),
    ];
    for (var i = 0; i < 70; i++) {
      canvas.drawCircle(
        Offset(
          bounds.left + rnd.nextDouble() * bounds.width,
          bounds.top + rnd.nextDouble() * bounds.height,
        ),
        0.8 + rnd.nextDouble() * hgt * 0.05,
        Paint()..color = flecks[i % 4],
      );
    }
    canvas.restore();
    canvas.drawPath(
      end,
      Paint()
        ..color = const Color(0xff2a170e)
        ..style = PaintingStyle.stroke
        ..strokeWidth = hgt * 0.06,
    );

    // Drizzle across the coated top and front.
    final drizzle = Paint()
      ..color = const Color(0xff8a5a3c)
      ..style = PaintingStyle.stroke
      ..strokeCap = StrokeCap.round
      ..strokeWidth = hgt * 0.06;
    for (var k = 0; k < 3; k++) {
      final path = Path();
      for (var i = 0; i <= 40; i++) {
        final t = i / 40;
        final x = x0 + len * (0.04 + t * 0.9) + skew.dx * (0.25 + k * 0.25);
        final y =
            y0 +
            skew.dy * (0.25 + k * 0.25) +
            math.sin(t * math.pi * 7 + k) * hgt * 0.18 +
            hgt * 0.12;
        i == 0 ? path.moveTo(x, y) : path.lineTo(x, y);
      }
      canvas.drawPath(path, drizzle);
    }

    // Soft highlight along the front edge.
    canvas.drawLine(
      Offset(x0 + hgt * 0.3, y0 + hgt * 0.1),
      Offset(x0 + len - hgt * 0.3, y0 + hgt * 0.1),
      Paint()
        ..color = const Color(0x40ffffff)
        ..strokeWidth = hgt * 0.05
        ..strokeCap = StrokeCap.round,
    );
  }

  @override
  bool shouldRepaint(_BarPainter old) => false;
}

/// Layered rolling hills with a seeded grass texture.
class _HillsPainter extends CustomPainter {
  const _HillsPainter();

  @override
  void paint(Canvas canvas, Size size) {
    final w = size.width;
    final h = size.height;
    final layers = [
      (0.28, const Color(0xff7fb24f), const Color(0xff4f8a32), 0.9),
      (0.42, const Color(0xff5f9a3c), const Color(0xff346d25), 1.7),
      (0.6, const Color(0xff3f7f2c), _hillDark, 2.6),
    ];
    final rnd = math.Random(11);
    for (final (rise, light, dark, phase) in layers) {
      final path = Path()..moveTo(0, h);
      for (var i = 0; i <= 60; i++) {
        final x = w * i / 60;
        final y =
            h * rise +
            math.sin(i / 60 * math.pi * 2.2 + phase) * h * 0.13 +
            math.sin(i / 60 * math.pi * 5.1 + phase * 2) * h * 0.04;
        path.lineTo(x, y);
      }
      path
        ..lineTo(w, h)
        ..close();
      canvas.drawPath(path, Paint()..color = Color.lerp(light, dark, 0.45)!);
      canvas.save();
      canvas.clipPath(path);
      final blade = Paint()
        ..strokeWidth = 1.1
        ..strokeCap = StrokeCap.round;
      for (var i = 0; i < (w * 1.4).round(); i++) {
        final x = rnd.nextDouble() * w;
        final y = h * (rise - 0.18) + rnd.nextDouble() * h;
        blade.color = (rnd.nextBool() ? light : dark).withValues(alpha: 0.55);
        canvas.drawLine(
          Offset(x, y),
          Offset(x + rnd.nextDouble() * 2 - 1, y - 3 - rnd.nextDouble() * 5),
          blade,
        );
      }
      canvas.restore();
    }
  }

  @override
  bool shouldRepaint(_HillsPainter old) => false;
}

class _Checks extends StatelessWidget {
  const _Checks({required this.narrow});
  final bool narrow;

  static const _rows = [
    (
      'Off-note masking',
      'Sensory compounds behind spirulina and chlorella off-notes are linked to '
          'masking ingredients through reviewed sensory evidence.',
    ),
    (
      'Exact-form nutrition',
      'Protein, energy and allergens are computed for the exact ingredient form '
          'you choose, powder or extract, not generic values.',
    ),
    (
      'Cited evidence',
      'Every explanation is drawn from a reviewed dataset and evidence index, '
          'and its citations are checked before the report shows them.',
    ),
  ];

  @override
  Widget build(BuildContext context) => Container(
    decoration: BoxDecoration(
      color: AlgaColors.deep,
      borderRadius: BorderRadius.circular(narrow ? 22 : 30),
    ),
    padding: EdgeInsets.symmetric(
      horizontal: narrow ? 22 : 56,
      vertical: narrow ? 40 : 80,
    ),
    child: Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        ConstrainedBox(
          constraints: const BoxConstraints(maxWidth: 760),
          child: Text(
            'What every screening run checks',
            style: _type(
              narrow ? 34 : 56,
              color: Colors.white,
              tracking: -0.03,
              height: 1.05,
            ),
          ),
        ),
        SizedBox(height: narrow ? 28 : 48),
        for (final (title, body) in _rows)
          Container(
            padding: const EdgeInsets.symmetric(vertical: 22),
            child: Flex(
              direction: narrow ? Axis.vertical : Axis.horizontal,
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                SizedBox(
                  width: narrow ? null : 340,
                  child: Text(
                    title,
                    style: _type(28, color: AlgaColors.lime, weight: 600),
                  ),
                ),
                SizedBox(height: narrow ? 8 : 0),
                Flexible(
                  child: ConstrainedBox(
                    constraints: const BoxConstraints(maxWidth: 620),
                    child: Text(
                      body,
                      style: _type(
                        18,
                        color: Colors.white,
                        weight: 400,
                        height: 1.55,
                      ),
                    ),
                  ),
                ),
              ],
            ),
          ),
      ],
    ),
  );
}

class _Close extends StatelessWidget {
  const _Close({required this.narrow, required this.onOpenLab});
  final bool narrow;
  final VoidCallback onOpenLab;

  @override
  Widget build(BuildContext context) => Container(
    decoration: BoxDecoration(
      color: _paper,
      borderRadius: BorderRadius.circular(narrow ? 22 : 30),
    ),
    padding: EdgeInsets.symmetric(
      horizontal: narrow ? 22 : 56,
      vertical: narrow ? 44 : 88,
    ),
    child: Flex(
      direction: narrow ? Axis.vertical : Axis.horizontal,
      crossAxisAlignment: narrow
          ? CrossAxisAlignment.start
          : CrossAxisAlignment.center,
      children: [
        Flexible(
          fit: FlexFit.loose,
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                'Shortlist your next bench trial',
                style: _type(narrow ? 34 : 52, tracking: -0.03, height: 1.05),
              ),
              const SizedBox(height: 16),
              ConstrainedBox(
                constraints: const BoxConstraints(maxWidth: 560),
                child: Text(
                  'Results are computational screening. Sensory and '
                  'manufacturing validation still happen at the bench.',
                  style: _type(18, weight: 400, height: 1.55),
                ),
              ),
            ],
          ),
        ),
        SizedBox(width: 40, height: narrow ? 28 : 0),
        _PillButton(label: 'Start screening', dark: true, onPressed: onOpenLab),
      ],
    ),
  );
}

class _Wordmark extends StatelessWidget {
  const _Wordmark();

  @override
  Widget build(BuildContext context) => LayoutBuilder(
    builder: (context, box) => Padding(
      padding: const EdgeInsets.only(top: 24, bottom: 8),
      child: Text(
        'ALGAMASK',
        maxLines: 1,
        style: _type(
          box.maxWidth * 0.158,
          weight: 600,
          tracking: -0.04,
          height: 0.9,
        ),
      ),
    ),
  );
}
