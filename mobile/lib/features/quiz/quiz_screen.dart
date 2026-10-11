import 'package:flutter/material.dart';

import '../../data/models/question.dart';
import '../domains/domain_info.dart';
import '../results/results_screen.dart';
import '../study/study_event.dart';
import 'quiz_controller.dart';

/// Gemini-style quiz interaction:
/// 1. Clean question stem and domain badges.
/// 2. Interactive choice cards (A, B, C, D) with instant color feedback
///    (green checkmark for correct, red 'X' for incorrect, correct answer highlighted).
/// 3. Immediate worked explanation card revealed smoothly below choices.
/// 4. Zero manual self-rating prompts (automated smart recognition).
/// 5. Prominent Next Question / See Results progression button.
class QuizScreen extends StatefulWidget {
  final List<Question> questions;
  final String title;
  final String sessionKind;

  /// Wired by the study layer (SRS recording, QOTD, streaks, journal).
  final Future<void> Function(AnswerEvent event)? onAnswerLocked;

  const QuizScreen({
    super.key,
    required this.questions,
    required this.title,
    this.sessionKind = 'quiz',
    this.onAnswerLocked,
  });

  @override
  State<QuizScreen> createState() => _QuizScreenState();
}

class _QuizScreenState extends State<QuizScreen> {
  late final QuizController _controller;

  @override
  void initState() {
    super.initState();
    _controller = QuizController(
      widget.questions,
      sessionKind: widget.sessionKind,
      onAnswerLocked: widget.onAnswerLocked,
    );
    _controller.addListener(_refresh);
  }

  void _refresh() => setState(() {});

  @override
  void dispose() {
    _controller.removeListener(_refresh);
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final colorScheme = theme.colorScheme;
    final question = _controller.current;
    final info = domainInfo(question.domain);
    final answered = _controller.answered;
    final userSelection = _controller.selectedIndex;
    final isCorrect = answered && question.isCorrect(userSelection!);

    return Scaffold(
      appBar: AppBar(
        title: Text(widget.title),
        actions: [
          Center(
            child: Padding(
              padding: const EdgeInsets.only(right: 16),
              child: Text(
                '${_controller.index + 1} / ${_controller.total}',
                style: theme.textTheme.titleMedium?.copyWith(
                  fontWeight: FontWeight.bold,
                ),
              ),
            ),
          ),
        ],
      ),
      body: Center(
        child: ConstrainedBox(
          constraints: const BoxConstraints(maxWidth: 720),
          child: Column(
            children: [
              LinearProgressIndicator(
                value: (_controller.index + 1) / _controller.total,
                minHeight: 4,
              ),
              Expanded(
                child: ListView(
                  padding: const EdgeInsets.fromLTRB(16, 16, 16, 24),
                  children: [
                    // Domain and difficulty pills
                    Row(
                      children: [
                        Container(
                          padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                          decoration: BoxDecoration(
                            color: colorScheme.secondaryContainer,
                            borderRadius: BorderRadius.circular(16),
                          ),
                          child: Row(
                            mainAxisSize: MainAxisSize.min,
                            children: [
                              Icon(info.icon, size: 16, color: colorScheme.onSecondaryContainer),
                              const SizedBox(width: 6),
                              Text(
                                info.name,
                                style: theme.textTheme.labelMedium?.copyWith(
                                  color: colorScheme.onSecondaryContainer,
                                  fontWeight: FontWeight.w600,
                                ),
                              ),
                            ],
                          ),
                        ),
                        const SizedBox(width: 8),
                        Container(
                          padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                          decoration: BoxDecoration(
                            color: colorScheme.surfaceContainerHighest,
                            borderRadius: BorderRadius.circular(16),
                          ),
                          child: Text(
                            'Level ${question.difficulty}',
                            style: theme.textTheme.labelMedium?.copyWith(
                              color: colorScheme.onSurfaceVariant,
                            ),
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 16),

                    // Question Stem Card
                    Card(
                      elevation: 1,
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(16),
                        side: BorderSide(color: colorScheme.outlineVariant.withOpacity(0.5)),
                      ),
                      child: Padding(
                        padding: const EdgeInsets.all(20),
                        child: Text(
                          question.stem,
                          style: theme.textTheme.titleMedium?.copyWith(
                            height: 1.45,
                            fontWeight: FontWeight.w500,
                          ),
                        ),
                      ),
                    ),
                    const SizedBox(height: 16),

                    // Gemini-Style Options (A, B, C, D)
                    for (int i = 0; i < question.choices.length; i++)
                      _buildChoiceCard(context, question, i),

                    // Gemini-Style Instant Worked Explanation Banner
                    if (answered) ...[
                      const SizedBox(height: 16),
                      _buildExplanationBanner(context, question, isCorrect),
                    ],

                    const SizedBox(height: 24),
                  ],
                ),
              ),

              // Fixed Bottom Navigation Bar
              SafeArea(
                child: Container(
                  padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
                  decoration: BoxDecoration(
                    color: colorScheme.surface,
                    border: Border(top: BorderSide(color: colorScheme.outlineVariant.withOpacity(0.4))),
                  ),
                  child: Row(
                    children: [
                      if (_controller.index > 0)
                        OutlinedButton.icon(
                          onPressed: _controller.previous,
                          icon: const Icon(Icons.arrow_back, size: 18),
                          label: const Text('Back'),
                        ),
                      if (_controller.index > 0) const SizedBox(width: 12),
                      Expanded(
                        child: FilledButton.icon(
                          onPressed: answered
                              ? () {
                                  if (_controller.isLast) {
                                    _finish();
                                  } else {
                                    _controller.next();
                                  }
                                }
                              : null,
                          icon: Icon(
                            _controller.isLast ? Icons.check_circle_outline : Icons.arrow_forward,
                            size: 18,
                          ),
                          label: Text(
                            _controller.isLast ? 'See Results' : 'Next Question',
                            style: const TextStyle(fontWeight: FontWeight.bold),
                          ),
                        ),
                      ),
                    ],
                  ),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  /// Gemini-style interactive choice card.
  Widget _buildChoiceCard(BuildContext context, Question question, int i) {
    final theme = Theme.of(context);
    final colorScheme = theme.colorScheme;
    final answered = _controller.answered;
    final isSelected = _controller.selectedIndex == i;
    final isRightAnswer = i == question.answerIndex;

    Color backgroundColor = colorScheme.surface;
    Color borderColor = colorScheme.outlineVariant;
    Color badgeBg = colorScheme.surfaceContainerHighest;
    Color badgeFg = colorScheme.onSurfaceVariant;
    Widget? trailingIcon;
    double opacity = 1.0;

    if (answered) {
      if (isRightAnswer) {
        backgroundColor = Colors.green.withOpacity(0.12);
        borderColor = Colors.green.shade600;
        badgeBg = Colors.green.shade600;
        badgeFg = Colors.white;
        trailingIcon = const Icon(Icons.check_circle, color: Colors.green, size: 22);
      } else if (isSelected) {
        backgroundColor = colorScheme.errorContainer.withOpacity(0.5);
        borderColor = colorScheme.error;
        badgeBg = colorScheme.error;
        badgeFg = colorScheme.onError;
        trailingIcon = Icon(Icons.cancel, color: colorScheme.error, size: 22);
      } else {
        opacity = 0.55;
      }
    }

    final letter = 'ABCD'[i];

    return AnimatedOpacity(
      duration: const Duration(milliseconds: 250),
      opacity: opacity,
      child: Padding(
        padding: const EdgeInsets.symmetric(vertical: 5),
        child: Material(
          color: backgroundColor,
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(12),
            side: BorderSide(
              color: borderColor,
              width: (answered && (isRightAnswer || isSelected)) ? 2.0 : 1.0,
            ),
          ),
          child: InkWell(
            borderRadius: BorderRadius.circular(12),
            onTap: answered ? null : () => _controller.select(i),
            child: Padding(
              padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 14),
              child: Row(
                children: [
                  Container(
                    width: 32,
                    height: 32,
                    decoration: BoxDecoration(
                      color: badgeBg,
                      shape: BoxShape.circle,
                    ),
                    alignment: Alignment.center,
                    child: Text(
                      letter,
                      style: TextStyle(
                        color: badgeFg,
                        fontWeight: FontWeight.bold,
                        fontSize: 14,
                      ),
                    ),
                  ),
                  const SizedBox(width: 14),
                  Expanded(
                    child: Text(
                      question.choices[i],
                      style: theme.textTheme.bodyLarge?.copyWith(
                        fontWeight: isSelected || (answered && isRightAnswer)
                            ? FontWeight.w600
                            : FontWeight.normal,
                      ),
                    ),
                  ),
                  if (trailingIcon != null) ...[
                    const SizedBox(width: 8),
                    trailingIcon,
                  ],
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }

  /// Instant worked explanation card delivered below the choices.
  Widget _buildExplanationBanner(
      BuildContext context, Question question, bool isCorrect) {
    final theme = Theme.of(context);
    final colorScheme = theme.colorScheme;

    final bannerBg = isCorrect
        ? Colors.green.withOpacity(0.10)
        : colorScheme.errorContainer.withOpacity(0.35);
    final borderColor = isCorrect ? Colors.green.shade600 : colorScheme.error;

    return Card(
      elevation: 0,
      color: bannerBg,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(16),
        side: BorderSide(color: borderColor, width: 1.5),
      ),
      child: Padding(
        padding: const EdgeInsets.all(18),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(
                  isCorrect ? Icons.check_circle : Icons.cancel,
                  color: isCorrect ? Colors.green.shade700 : colorScheme.error,
                  size: 24,
                ),
                const SizedBox(width: 10),
                Expanded(
                  child: Text(
                    isCorrect
                        ? 'Correct! Well done.'
                        : 'Incorrect · Correct answer is ${question.correctChoice}',
                    style: theme.textTheme.titleMedium?.copyWith(
                      fontWeight: FontWeight.bold,
                      color: isCorrect ? Colors.green.shade900 : colorScheme.error,
                    ),
                  ),
                ),
              ],
            ),
            const Divider(height: 20),
            Text(
              'Explanation & Worked Solution',
              style: theme.textTheme.labelLarge?.copyWith(
                fontWeight: FontWeight.bold,
                color: theme.textTheme.bodyMedium?.color?.withOpacity(0.75),
              ),
            ),
            const SizedBox(height: 6),
            Text(
              question.explanation,
              style: theme.textTheme.bodyMedium?.copyWith(
                height: 1.5,
              ),
            ),
          ],
        ),
      ),
    );
  }

  void _finish() {
    Navigator.of(context).pushReplacement(
      MaterialPageRoute(
        builder: (_) => ResultsScreen(
          records: _controller.records,
          total: _controller.total,
          title: widget.title,
          allQuestions: _controller.questions,
          onAnswerLocked: widget.onAnswerLocked,
        ),
      ),
    );
  }
}
