import 'dart:math' as math;

import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:flutter/scheduler.dart';
import 'package:url_launcher/url_launcher.dart';

import 'design.dart';
import 'input_screen.dart';

const _sage = Color(0xffbcd2c0);
const _paper = Color(0xffeceeea);
const _ink = Color(0xff0f2a1f);
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
    _ticker = createTicker(_follow);
    _scroll.addListener(_resumeAnimation);
  }

  void _resumeAnimation() {
    if (!_ticker.isActive) _ticker.start();
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
      _ticker.stop();
    } else {
      _ticker.stop();
    }
  }

  @override
  void dispose() {
    _ticker.dispose();
    _shown.dispose();
    _scroll.removeListener(_resumeAnimation);
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
          final wordStyle = _type(word, weight: 600, tracking: -0.04, height: 1, color: const Color(0xff294536)).copyWith(fontFamily: 'SpaceGrotesk');
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
                left: narrow ? pad - word * 0.05 : w * .09,
                top: h * 0.12,
                child: Text('ALGAE', style: wordStyle),
              ),
              Positioned(
                right: narrow ? pad : w * .09,
                top: h * 0.12 + (narrow ? 0 : word * .72),
                child: Text('MASK', style: wordStyle),
              ),
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
                      style: _type(narrow ? 16 : 19, color: _ink, height: 1.35),
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
                _link('Meet the algae', onChecks),
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

/// The scroll-driven centrepiece: algae powder, maskers converging, then the bar.
class _Transition extends StatelessWidget {
  const _Transition({
    required this.progress,
    required this.narrow,
    required this.room,
  });
  final double progress;
  final bool narrow;
  final Rect room;

  @override
  Widget build(BuildContext context) => LayoutBuilder(
    builder: (context, box) {
      final w = box.maxWidth;
      final h = box.maxHeight;
      final bowlSize = math.min(w * (narrow ? .72 : .38), h * .54) * 1.12;
      final center = Offset(w * (narrow ? .5 : .51), h * (narrow ? .51 : .54));
      final spread = Curves.easeOutCubic.transform(
        (progress / .72).clamp(0.0, 1.0),
      );
      final diameter = math.min(math.max(w, h) * .88, math.min(w, h) * 1.05) * 1.12;
      return Stack(
        children: [
          Positioned(
            left: center.dx - diameter / 2,
            top: center.dy - diameter / 2,
            width: diameter,
            height: diameter,
            child: IgnorePointer(
              child: Opacity(
                opacity: (spread * 3).clamp(0.0, 1.0),
                child: Transform.scale(
                  scale: .28 + spread * .72,
                  child: Image.asset(
                    'assets/ingredients/powder-burst.png',
                    fit: BoxFit.contain,
                    filterQuality: FilterQuality.high,
                  ),
                ),
              ),
            ),
          ),
          Positioned(
            left: center.dx - bowlSize / 2,
            top: center.dy - bowlSize / 2,
            width: bowlSize,
            height: bowlSize,
            child: IgnorePointer(
              child: Image.asset(
                'assets/ingredients/bowl-cutout.png',
                fit: BoxFit.contain,
                filterQuality: FilterQuality.high,
              ),
            ),
          ),
        ],
      );
    },
  );
}

class _Checks extends StatelessWidget {
  const _Checks({required this.narrow});
  final bool narrow;

  @override
  Widget build(BuildContext context) => Container(
    decoration: BoxDecoration(
      color: _paper,
      borderRadius: BorderRadius.circular(narrow ? 22 : 30),
    ),
    padding: EdgeInsets.symmetric(
      horizontal: narrow ? 24 : 56,
      vertical: narrow ? 36 : 64,
    ),
    child: Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text('MEET THE INGREDIENTS',
            style: _type(12, weight: 700, tracking: .14,
                color: const Color(0xff52705a))),
        const SizedBox(height: 24),
        _IngredientStory(
          narrow: narrow,
          number: '01',
          title: 'What is algae?',
          body: 'Algae are a diverse group of organisms that use sunlight to grow. '
              'Edible varieties range from seaweeds such as nori and wakame to '
              'tiny freshwater algae such as chlorella. In food, they bring '
              'distinctive colour, flavour and nutrients.',
          image: 'assets/ingredients/sea-lettuce.jpg',
          photo: true,
          caption: 'SEA LETTUCE / EDIBLE GREEN ALGAE',
          background: const Color(0xffdce4d3),
        ),
        Padding(
          padding: EdgeInsets.symmetric(vertical: narrow ? 32 : 48),
          child: const Divider(color: Color(0xffc7d0c4), height: 1),
        ),
        _IngredientStory(
          narrow: narrow,
          number: '02',
          title: 'What is spirulina?',
          body: 'Spirulina is a microscopic cyanobacterium, commonly called '
              'blue-green algae, cultivated for food. Dried into a deep-green '
              'powder, it adds protein and colour to foods such as smoothies '
              'and snack bars. Its distinctive earthy flavour is one reason '
              'ingredient pairing matters.',
          image: 'assets/ingredients/spirulina-provided.png',
          photo: true,
          photoCredit: '',
          photoSource: '',
          caption: 'SPIRULINA / DRIED GREEN POWDER',
          background: const Color(0xffd0ded5),
          reverse: true,
        ),
      ],
    ),
  );
}

class _IngredientStory extends StatelessWidget {
  const _IngredientStory({
    required this.narrow,
    required this.number,
    required this.title,
    required this.body,
    required this.image,
    required this.caption,
    required this.background,
    this.reverse = false,
    this.photo = false,
    this.photoCredit = 'Photo: Holger Krisp / CC BY 3.0',
    this.photoSource = 'https://commons.wikimedia.org/wiki/File:Meersalat-Ulva-lactuca.jpg',
  });

  final bool narrow;
  final String number, title, body, image, caption;
  final Color background;
  final bool reverse;
  final bool photo;
  final String photoCredit, photoSource;

  @override
  Widget build(BuildContext context) {
    final picture = Column(
      children: [
        Container(
          decoration: BoxDecoration(
            color: background,
            borderRadius: BorderRadius.circular(20),
          ),
          padding: const EdgeInsets.all(16),
          child: SizedBox(
            height: narrow ? 230 : 460,
            width: double.infinity,
            child: ClipRRect(
              borderRadius: BorderRadius.circular(14),
              child: Image.asset(
                image,
                fit: photo && narrow ? BoxFit.cover : BoxFit.contain,
                semanticLabel: caption,
                filterQuality: FilterQuality.high,
              ),
            ),
          ),
        ),
        const SizedBox(height: 16),
        Text(
          caption,
          textAlign: TextAlign.center,
          style: _type(11, tracking: .10, weight: 600,
              color: const Color(0xff47624f)),
        ),
        if (photo && photoCredit.isNotEmpty)
          TextButton(
            onPressed: () => launchUrl(Uri.parse(photoSource)),
            child: Text(photoCredit,
                style: _type(11, color: const Color(0xff47624f))),
          ),
      ],
    );
    final copy = Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(number, style: _type(14, weight: 600,
            color: const Color(0xff62806a))),
        const SizedBox(height: 16),
        Text(title, style: _type(narrow ? 36 : 48,
            tracking: -.035, height: 1.1)),
        const SizedBox(height: 20),
        Text(body, style: _type(narrow ? 17 : 19, weight: 400,
            height: 1.6, color: const Color(0xff42594a))),
      ],
    );
    if (narrow) {
      return Column(crossAxisAlignment: CrossAxisAlignment.start,
          children: [copy, const SizedBox(height: 24), picture]);
    }
    return Row(
      children: [
        Expanded(child: reverse ? copy : picture),
        const SizedBox(width: 64),
        Expanded(child: reverse ? picture : copy),
      ],
    );
  }
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
      mainAxisSize: MainAxisSize.min,
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
