import 'dart:convert';

import 'package:flutter/material.dart';

import '../generated/pddcertificateissuancerequestuishape.dart' as cir;
import '../generated/pddsectionauishape.dart' as pdda;
import '../generated/pddsectionavalidationreviewuishape.dart' as pdda_review;
import '../generated/pddsectionbuishape.dart' as pddb;
import '../generated/pddsectionbvalidationreviewuishape.dart' as pddb_review;
import '../generated/pddsectioncuishape.dart' as pddc;
import '../generated/pddsectioncvalidationreviewuishape.dart' as pddc_review;
import 'workflow_contract.dart';

class PddWorkflowShellApp extends StatelessWidget {
  const PddWorkflowShellApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'NIAS PDD Workflow',
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(
          seedColor: const Color(0xff176b5f),
          brightness: Brightness.light,
        ),
        useMaterial3: true,
        visualDensity: VisualDensity.standard,
      ),
      home: const PddWorkflowShellPage(),
    );
  }
}

class PddWorkflowShellPage extends StatefulWidget {
  const PddWorkflowShellPage({super.key});

  @override
  State<PddWorkflowShellPage> createState() => _PddWorkflowShellPageState();
}

class _PddWorkflowShellPageState extends State<PddWorkflowShellPage> {
  final PddWorkflowState _workflow = PddWorkflowState();
  final Map<PddWorkflowStep, Map<String, dynamic>> _drafts = {};

  WorkflowRole _role = WorkflowRole.developer;
  PddWorkflowStep _activeStep = PddWorkflowStep.pddA;

  @override
  void initState() {
    super.initState();
    for (final step in PddWorkflowStep.values) {
      _drafts[step] = _workflow.documentSeed(step);
    }
  }

  @override
  Widget build(BuildContext context) {
    final gate = _workflow.gateResult();
    final blockers = _workflow.blockers(_activeStep, _role);
    final canOpen = blockers.isEmpty;

    return Scaffold(
      appBar: AppBar(
        title: const Text('NIAS PDD workflow'),
        actions: [
          Padding(
            padding: const EdgeInsets.only(right: 16),
            child: SegmentedButton<WorkflowRole>(
              segments: WorkflowRole.values
                  .map(
                    (role) => ButtonSegment(
                      value: role,
                      label: Text(role.label),
                      icon: Icon(
                        role == WorkflowRole.developer
                            ? Icons.engineering_outlined
                            : Icons.fact_check_outlined,
                      ),
                    ),
                  )
                  .toList(),
              selected: {_role},
              onSelectionChanged: (selection) {
                setState(() {
                  _role = selection.first;
                });
              },
            ),
          ),
        ],
      ),
      body: Row(
        children: [
          SizedBox(
            width: 300,
            child: _StepRail(
              role: _role,
              workflow: _workflow,
              activeStep: _activeStep,
              onStepSelected: (step) {
                setState(() {
                  _activeStep = step;
                  _refreshDerivedDraft(step);
                });
              },
            ),
          ),
          const VerticalDivider(width: 1),
          Expanded(
            child: _WorkflowPanel(
              step: _activeStep,
              role: _role,
              gate: gate,
              blockers: blockers,
              canOpen: canOpen,
              form: canOpen ? _buildForm(_activeStep) : null,
              payload: _drafts[_activeStep] ?? const {},
              onSubmit: canOpen ? () => _submitActiveStep() : null,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildForm(PddWorkflowStep step) {
    final draft = _drafts[step]!;
    switch (step) {
      case PddWorkflowStep.pddA:
        return pdda.PddSectionAUiShapeFormWidget(initial: draft);
      case PddWorkflowStep.pddB:
        return pddb.PddSectionBUiShapeFormWidget(initial: draft);
      case PddWorkflowStep.pddC:
        return pddc.PddSectionCUiShapeFormWidget(initial: draft);
      case PddWorkflowStep.reviewA:
        return pdda_review.PddSectionAValidationReviewUiShapeFormWidget(
          initial: draft,
        );
      case PddWorkflowStep.reviewB:
        return pddb_review.PddSectionBValidationReviewUiShapeFormWidget(
          initial: draft,
        );
      case PddWorkflowStep.reviewC:
        return pddc_review.PddSectionCValidationReviewUiShapeFormWidget(
          initial: draft,
        );
      case PddWorkflowStep.pddCir:
        return cir.PddCertificateIssuanceRequestUiShapeFormWidget(
          initial: draft,
        );
    }
  }

  void _refreshDerivedDraft(PddWorkflowStep step) {
    final section = step.reviewSection;
    if (section != null) {
      _drafts[step] = _workflow.reviewSeed(section);
    }
    if (step == PddWorkflowStep.pddCir) {
      _drafts[step] = _workflow.pddCirSeed();
    }
  }

  void _submitActiveStep() {
    final draft = _drafts[_activeStep]!;
    final artifact = _workflow.submit(_activeStep, draft);
    setState(() {
      if (_activeStep == PddWorkflowStep.pddCir) {
        _drafts[PddWorkflowStep.pddCir] = _workflow.pddCirSeed();
      }
    });

    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(
          '${_activeStep.label} captured as ${artifact.documentMessageId}',
        ),
      ),
    );
  }
}

class _StepRail extends StatelessWidget {
  final WorkflowRole role;
  final PddWorkflowState workflow;
  final PddWorkflowStep activeStep;
  final ValueChanged<PddWorkflowStep> onStepSelected;

  const _StepRail({
    required this.role,
    required this.workflow,
    required this.activeStep,
    required this.onStepSelected,
  });

  @override
  Widget build(BuildContext context) {
    return ListView(
      padding: const EdgeInsets.all(12),
      children: [
        Text('Workflow', style: Theme.of(context).textTheme.titleMedium),
        const SizedBox(height: 8),
        for (final step in PddWorkflowStep.values)
          _StepTile(
            step: step,
            selected: step == activeStep,
            submitted: workflow.isSubmitted(step),
            enabled: workflow.canOpen(step, role),
            blockers: workflow.blockers(step, role),
            onTap: () => onStepSelected(step),
          ),
      ],
    );
  }
}

class _StepTile extends StatelessWidget {
  final PddWorkflowStep step;
  final bool selected;
  final bool submitted;
  final bool enabled;
  final List<String> blockers;
  final VoidCallback onTap;

  const _StepTile({
    required this.step,
    required this.selected,
    required this.submitted,
    required this.enabled,
    required this.blockers,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    final colorScheme = Theme.of(context).colorScheme;
    return Card(
      elevation: selected ? 1 : 0,
      color: selected ? colorScheme.secondaryContainer : null,
      margin: const EdgeInsets.only(bottom: 8),
      child: ListTile(
        dense: true,
        enabled: enabled || selected,
        leading: Icon(
          _iconForStep(step),
          color: submitted ? colorScheme.primary : null,
        ),
        title: Text(step.label),
        subtitle: blockers.isEmpty ? null : Text(blockers.first),
        trailing: submitted
            ? const Icon(Icons.check_circle, color: Colors.green)
            : enabled
                ? const Icon(Icons.radio_button_unchecked)
                : const Icon(Icons.lock_outline),
        onTap: onTap,
      ),
    );
  }

  IconData _iconForStep(PddWorkflowStep step) {
    switch (step) {
      case PddWorkflowStep.pddA:
      case PddWorkflowStep.pddB:
      case PddWorkflowStep.pddC:
        return Icons.article_outlined;
      case PddWorkflowStep.reviewA:
      case PddWorkflowStep.reviewB:
      case PddWorkflowStep.reviewC:
        return Icons.rate_review_outlined;
      case PddWorkflowStep.pddCir:
        return Icons.verified_outlined;
    }
  }
}

class _WorkflowPanel extends StatelessWidget {
  final PddWorkflowStep step;
  final WorkflowRole role;
  final GateResult gate;
  final List<String> blockers;
  final bool canOpen;
  final Widget? form;
  final Map<String, dynamic> payload;
  final VoidCallback? onSubmit;

  const _WorkflowPanel({
    required this.step,
    required this.role,
    required this.gate,
    required this.blockers,
    required this.canOpen,
    required this.form,
    required this.payload,
    required this.onSubmit,
  });

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        _PanelHeader(
          step: step,
          role: role,
          gate: gate,
          blockers: blockers,
          payload: payload,
        ),
        const Divider(height: 1),
        Expanded(
          child: canOpen
              ? Row(
                  crossAxisAlignment: CrossAxisAlignment.stretch,
                  children: [
                    Expanded(
                      flex: 3,
                      child: _FormSurface(child: form!),
                    ),
                  ],
                )
              : _BlockedPanel(blockers: blockers),
        ),
        const Divider(height: 1),
        Padding(
          padding: const EdgeInsets.all(12),
          child: Row(
            mainAxisAlignment: MainAxisAlignment.end,
            children: [
              FilledButton.icon(
                icon: Icon(
                  step == PddWorkflowStep.pddCir ? Icons.verified : Icons.send,
                ),
                label: Text(
                  step == PddWorkflowStep.pddCir ? 'Submit PDD-CIR' : 'Submit',
                ),
                onPressed: onSubmit,
              ),
            ],
          ),
        ),
      ],
    );
  }
}

class _FormSurface extends StatelessWidget {
  final Widget child;

  const _FormSurface({required this.child});

  @override
  Widget build(BuildContext context) {
    return LayoutBuilder(
      builder: (context, constraints) {
        final contentWidth =
            constraints.maxWidth < 1160 ? 1160.0 : constraints.maxWidth;

        return SingleChildScrollView(
          padding: const EdgeInsets.all(20),
          child: SingleChildScrollView(
            scrollDirection: Axis.horizontal,
            child: SizedBox(width: contentWidth - 40, child: child),
          ),
        );
      },
    );
  }
}

class _PanelHeader extends StatelessWidget {
  final PddWorkflowStep step;
  final WorkflowRole role;
  final GateResult gate;
  final List<String> blockers;
  final Map<String, dynamic> payload;

  const _PanelHeader({
    required this.step,
    required this.role,
    required this.gate,
    required this.blockers,
    required this.payload,
  });

  @override
  Widget build(BuildContext context) {
    final blocked = blockers.isNotEmpty;
    return Padding(
      padding: const EdgeInsets.fromLTRB(20, 16, 20, 12),
      child: Row(
        children: [
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  step.label,
                  style: Theme.of(context).textTheme.headlineSmall,
                ),
                const SizedBox(height: 4),
                Text(
                  'Role: ${role.label}',
                  style: Theme.of(context).textTheme.bodyMedium,
                ),
              ],
            ),
          ),
          _StatusChip(
            icon: blocked ? Icons.lock_outline : Icons.lock_open_outlined,
            label: blocked ? 'Blocked' : 'Open',
            color: blocked ? Colors.orange : Colors.green,
          ),
          const SizedBox(width: 8),
          _StatusChip(
            icon: gate.allowed
                ? Icons.verified_outlined
                : Icons.pending_actions_outlined,
            label: gate.allowed ? 'CIR gate ready' : 'CIR gate pending',
            color: gate.allowed ? Colors.green : Colors.blueGrey,
          ),
          const SizedBox(width: 8),
          IconButton.filledTonal(
            tooltip: 'Open payload',
            icon: const Icon(Icons.data_object_outlined),
            onPressed: () {
              showDialog<void>(
                context: context,
                builder: (context) => _PayloadDialog(payload: payload),
              );
            },
          ),
        ],
      ),
    );
  }
}

class _StatusChip extends StatelessWidget {
  final IconData icon;
  final String label;
  final Color color;

  const _StatusChip({
    required this.icon,
    required this.label,
    required this.color,
  });

  @override
  Widget build(BuildContext context) {
    return Chip(
      avatar: Icon(icon, size: 18, color: color),
      label: Text(label),
      side: BorderSide(color: color.withValues(alpha: 0.4)),
    );
  }
}

class _BlockedPanel extends StatelessWidget {
  final List<String> blockers;

  const _BlockedPanel({required this.blockers});

  @override
  Widget build(BuildContext context) {
    return Center(
      child: ConstrainedBox(
        constraints: const BoxConstraints(maxWidth: 620),
        child: Card(
          child: Padding(
            padding: const EdgeInsets.all(20),
            child: Column(
              mainAxisSize: MainAxisSize.min,
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  children: [
                    Icon(
                      Icons.lock_outline,
                      color: Theme.of(context).colorScheme.primary,
                    ),
                    const SizedBox(width: 8),
                    Text(
                      'Prerequisites',
                      style: Theme.of(context).textTheme.titleMedium,
                    ),
                  ],
                ),
                const SizedBox(height: 12),
                for (final blocker in blockers)
                  Padding(
                    padding: const EdgeInsets.only(bottom: 8),
                    child: Row(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        const Text('- '),
                        Expanded(child: Text(blocker)),
                      ],
                    ),
                  ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}

class _PayloadDialog extends StatelessWidget {
  final Map<String, dynamic> payload;

  const _PayloadDialog({required this.payload});

  @override
  Widget build(BuildContext context) {
    const encoder = JsonEncoder.withIndent('  ');
    return Dialog(
      child: ConstrainedBox(
        constraints: const BoxConstraints(maxWidth: 900, maxHeight: 720),
        child: Column(
          children: [
            Padding(
              padding: const EdgeInsets.fromLTRB(20, 16, 12, 8),
              child: Row(
                children: [
                  Expanded(
                    child: Text(
                      'Payload',
                      style: Theme.of(context).textTheme.titleLarge,
                    ),
                  ),
                  IconButton(
                    tooltip: 'Close payload',
                    icon: const Icon(Icons.close),
                    onPressed: () => Navigator.of(context).pop(),
                  ),
                ],
              ),
            ),
            const Divider(height: 1),
            Expanded(
              child: ColoredBox(
                color: Theme.of(
                  context,
                ).colorScheme.surfaceContainerHighest.withValues(alpha: 0.35),
                child: SingleChildScrollView(
                  padding: const EdgeInsets.all(20),
                  child: SelectableText(
                    encoder.convert(payload),
                    style: Theme.of(
                      context,
                    ).textTheme.bodySmall?.copyWith(fontFamily: 'monospace'),
                  ),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
