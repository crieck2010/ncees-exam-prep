import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../../core/notifications/notification_service.dart';
import '../../core/theme/theme_controller.dart';
import '../domains/domain_info.dart';
import '../study/insights/insights.dart';
import '../study/srs/study_repository.dart';
import '../study/streaks/streak_logic.dart';

/// Settings: Appearance, Quiz Preferences (question count & difficulty),
/// Smart Learning Recognition, Notifications, Exam Date, and Legal Disclaimers.
class SettingsScreen extends StatefulWidget {
  const SettingsScreen({super.key});

  @override
  State<SettingsScreen> createState() => _SettingsScreenState();
}

class _SettingsScreenState extends State<SettingsScreen> {
  String? _examDateKey;
  late int _questionCount;
  late int _difficulty;

  @override
  void initState() {
    super.initState();
    final repo = context.read<StudyRepository>();
    _examDateKey = repo.examDateKey;
    _questionCount = repo.questionCount;
    _difficulty = repo.difficulty;
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final themeController = context.watch<ThemeController>();
    final notifications = context.watch<NotificationService>();
    final studyRepo = context.watch<StudyRepository>();
    final journal = studyRepo.loadJournal();
    final insights = Insights.build(journal, DateTime.now());

    return Scaffold(
      appBar: AppBar(title: const Text('Settings')),
      body: Center(
        child: ConstrainedBox(
          constraints: const BoxConstraints(maxWidth: 720),
          child: ListView(
            padding: const EdgeInsets.all(16),
            children: [
              // 1. Quiz Settings (Question count & difficulty bar)
              Text('Quiz Settings', style: theme.textTheme.titleLarge),
              const SizedBox(height: 4),
              Text(
                'Configure the standard length and difficulty of your practice sessions.',
                style: theme.textTheme.bodySmall,
              ),
              const SizedBox(height: 12),
              Card(
                elevation: 0,
                color: theme.colorScheme.surfaceContainerHighest.withOpacity(0.4),
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(16),
                  side: BorderSide(color: theme.colorScheme.outlineVariant),
                ),
                child: Padding(
                  padding: const EdgeInsets.all(16),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Row(
                        mainAxisAlignment: MainAxisAlignment.spaceBetween,
                        children: [
                          const Text('Questions Per Session:', style: TextStyle(fontWeight: FontWeight.w600)),
                          Text('$_questionCount questions', style: TextStyle(color: theme.colorScheme.primary, fontWeight: FontWeight.bold)),
                        ],
                      ),
                      Slider(
                        value: _questionCount.toDouble(),
                        min: 5,
                        max: 50,
                        divisions: 9,
                        label: '$_questionCount',
                        onChanged: (v) {
                          final count = v.round();
                          setState(() => _questionCount = count);
                          studyRepo.setQuestionCount(count);
                        },
                      ),
                      const SizedBox(height: 12),
                      const Text('Difficulty Level:', style: TextStyle(fontWeight: FontWeight.w600)),
                      const SizedBox(height: 8),
                      SegmentedButton<int>(
                        segments: const [
                          ButtonSegment(value: 0, label: Text('All Levels')),
                          ButtonSegment(value: 1, label: Text('Level 1')),
                          ButtonSegment(value: 2, label: Text('Level 2')),
                          ButtonSegment(value: 3, label: Text('Level 3')),
                        ],
                        selected: {_difficulty},
                        onSelectionChanged: (val) {
                          final diff = val.first;
                          setState(() => _difficulty = diff);
                          studyRepo.setDifficulty(diff);
                        },
                      ),
                      const SizedBox(height: 6),
                      Text(
                        _difficulty == 0
                            ? 'Mixed difficulty across all questions.'
                            : _difficulty == 1
                                ? 'Level 1: Foundational definitions & direct formulas.'
                                : _difficulty == 2
                                    ? 'Level 2: Multi-step standard exam problems.'
                                    : 'Level 3: Advanced, multi-phase boundary & geodetic problems.',
                        style: theme.textTheme.bodySmall,
                      ),
                    ],
                  ),
                ),
              ),

              const SizedBox(height: 24),

              // 2. Appearance Setting (Light / Dark / System)
              Text('Appearance', style: theme.textTheme.titleLarge),
              const SizedBox(height: 4),
              Text('Choose your preferred color theme.', style: theme.textTheme.bodySmall),
              const SizedBox(height: 12),
              SegmentedButton<ThemeMode>(
                segments: const [
                  ButtonSegment(
                    value: ThemeMode.system,
                    label: Text('System'),
                    icon: Icon(Icons.settings_suggest_outlined),
                  ),
                  ButtonSegment(
                    value: ThemeMode.light,
                    label: Text('Light'),
                    icon: Icon(Icons.light_mode_outlined),
                  ),
                  ButtonSegment(
                    value: ThemeMode.dark,
                    label: Text('Dark'),
                    icon: Icon(Icons.dark_mode_outlined),
                  ),
                ],
                selected: {themeController.mode},
                onSelectionChanged: (selection) =>
                    context.read<ThemeController>().setMode(selection.first),
              ),

              const SizedBox(height: 24),

              // 3. Smart Performance Recognition
              Text('Smart Learning Recognition', style: theme.textTheme.titleLarge),
              const SizedBox(height: 4),
              Text(
                'Automated background tracking of your strengths and weak areas.',
                style: theme.textTheme.bodySmall,
              ),
              const SizedBox(height: 12),
              Card(
                elevation: 0,
                color: theme.colorScheme.surfaceContainerHighest.withOpacity(0.3),
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(16),
                  side: BorderSide(color: theme.colorScheme.outlineVariant),
                ),
                child: Padding(
                  padding: const EdgeInsets.all(16),
                  child: Column(
                    children: [
                      Row(
                        children: [
                          Icon(Icons.auto_graph, color: theme.colorScheme.primary),
                          const SizedBox(width: 10),
                          Expanded(
                            child: Text(
                              journal.isEmpty
                                  ? 'Answer practice questions to activate smart skill recognition.'
                                  : 'Recognized ${journal.length} answered questions across all domains.',
                              style: theme.textTheme.bodyMedium,
                            ),
                          ),
                        ],
                      ),
                      if (insights.strengths.isNotEmpty) ...[
                        const Divider(height: 20),
                        Row(
                          children: [
                            const Icon(Icons.star, color: Colors.amber, size: 20),
                            const SizedBox(width: 8),
                            const Text('Top Strength: ', style: TextStyle(fontWeight: FontWeight.bold)),
                            Expanded(
                              child: Text(
                                '${domainInfo(insights.strengths.first.domain).name} (${(insights.strengths.first.accuracy * 100).round()}% correct)',
                              ),
                            ),
                          ],
                        ),
                      ],
                      if (insights.focus.isNotEmpty) ...[
                        const SizedBox(height: 6),
                        Row(
                          children: [
                            Icon(Icons.trending_down, color: theme.colorScheme.error, size: 20),
                            const SizedBox(width: 8),
                            const Text('Focus Area: ', style: TextStyle(fontWeight: FontWeight.bold)),
                            Expanded(
                              child: Text(
                                '${domainInfo(insights.focus.first.domain).name} (${(insights.focus.first.accuracy * 100).round()}% correct)',
                              ),
                            ),
                          ],
                        ),
                      ],
                    ],
                  ),
                ),
              ),

              const SizedBox(height: 24),

              // 4. Notifications
              Text('Study Notifications', style: theme.textTheme.titleLarge),
              const SizedBox(height: 8),
              SwitchListTile(
                secondary: const Icon(Icons.today_outlined),
                title: const Text('Question of the Day'),
                subtitle: const Text('Daily 8:00 AM notification with today’s question'),
                value: notifications.qotdEnabled,
                onChanged: (value) async {
                  await notifications.setQotdEnabled(value);
                  await _resync(notifications);
                  if (context.mounted) setState(() {});
                },
              ),
              SwitchListTile(
                secondary: const Icon(Icons.local_fire_department_outlined),
                title: const Text('Streak Saver'),
                subtitle: const Text('8:00 PM evening reminder if today’s question is unanswered'),
                value: notifications.streakSaverEnabled,
                onChanged: (value) async {
                  await notifications.setStreakSaverEnabled(value);
                  await _resync(notifications);
                  if (context.mounted) setState(() {});
                },
              ),
              SwitchListTile(
                secondary: const Icon(Icons.bar_chart_outlined),
                title: const Text('Weekly Progress Summary'),
                subtitle: const Text('Monday 8:00 AM overview of your study progress'),
                value: notifications.weeklyEnabled,
                onChanged: (value) async {
                  await notifications.setWeeklyEnabled(value);
                  await _resync(notifications);
                  if (context.mounted) setState(() {});
                },
              ),

              const SizedBox(height: 24),

              // 5. Exam Date
              Text('Exam Schedule', style: theme.textTheme.titleLarge),
              const SizedBox(height: 8),
              ListTile(
                leading: const Icon(Icons.event_outlined),
                title: const Text('Target Exam Date'),
                subtitle: Text(_examDateKey ?? 'Not set — click to choose your exam date'),
                trailing: _examDateKey == null
                    ? const Icon(Icons.calendar_month)
                    : IconButton(
                        icon: const Icon(Icons.clear),
                        tooltip: 'Clear exam date',
                        onPressed: () async {
                          await context.read<StudyRepository>().clearExamDate();
                          setState(() => _examDateKey = null);
                        },
                      ),
                onTap: () => _pickExamDate(context),
              ),

              const SizedBox(height: 24),

              // 6. Legal & Disclaimers (NCEES Trademark & Affiliation Notice)
              Text('Legal & Disclaimers', style: theme.textTheme.titleLarge),
              const SizedBox(height: 8),
              Card(
                elevation: 0,
                color: theme.colorScheme.surfaceContainerHighest.withOpacity(0.5),
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(16),
                  side: BorderSide(color: theme.colorScheme.outlineVariant),
                ),
                child: Padding(
                  padding: const EdgeInsets.all(16),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Row(
                        children: [
                          Icon(Icons.gavel, size: 20, color: theme.colorScheme.primary),
                          const SizedBox(width: 8),
                          const Text(
                            'NCEES® Affiliation Disclaimer',
                            style: TextStyle(fontWeight: FontWeight.bold),
                          ),
                        ],
                      ),
                      const SizedBox(height: 8),
                      Text(
                        'FS Exam Prep is an independent educational training platform developed by Charles Rieck. '
                        'This application is NOT affiliated with, approved by, sponsored by, or endorsed by the '
                        'National Council of Examiners for Engineering and Surveying (NCEES).\n\n'
                        'NCEES®, FS®, and PS® are registered trademarks owned by the National Council of '
                        'Examiners for Engineering and Surveying. All practice questions, answers, formulas, '
                        'and explanations are independently authored for educational study purposes based upon '
                        'publicly published exam topic specifications.',
                        style: theme.textTheme.bodySmall?.copyWith(height: 1.45),
                      ),
                    ],
                  ),
                ),
              ),

              const SizedBox(height: 24),

              // 7. About App
              Text('About', style: theme.textTheme.titleLarge),
              const SizedBox(height: 8),
              const ListTile(
                leading: Icon(Icons.info_outline),
                title: Text('FS Exam Prep'),
                subtitle: Text('Author: Charles Rieck · Open-Source Geomatics Education'),
              ),
              const ListTile(
                leading: Icon(Icons.verified_outlined),
                title: Text('Version'),
                subtitle: Text('v0.5.0 Production Architecture'),
              ),
              const SizedBox(height: 32),
            ],
          ),
        ),
      ),
    );
  }

  Future<void> _resync(NotificationService notifications) async {
    await notifications.refreshSchedules(
      qotdAnsweredToday: true,
      streakCount: 0,
    );
  }

  Future<void> _pickExamDate(BuildContext context) async {
    final now = DateTime.now();
    var initial = now.add(const Duration(days: 60));
    if (_examDateKey != null) {
      final parts = _examDateKey!.split('-').map(int.parse).toList();
      initial = DateTime(parts[0], parts[1], parts[2]);
    }
    final picked = await showDatePicker(
      context: context,
      initialDate: initial,
      firstDate: now.subtract(const Duration(days: 365)),
      lastDate: now.add(const Duration(days: 730)),
    );
    if (picked != null && context.mounted) {
      final key = dateKey(picked);
      await context.read<StudyRepository>().setExamDate(key);
      setState(() => _examDateKey = key);
    }
  }
}
