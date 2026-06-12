import 'package:flutter_test/flutter_test.dart';
import 'package:nias_pdd_workflow_shell/src/workflow_contract.dart';

void main() {
  test('PDD section seeds open required content subforms', () {
    final workflow = PddWorkflowState();

    final pddA = workflow.documentSeed(PddWorkflowStep.pddA);
    final pddAContent = _singleMap(pddA[NiasTerm.reportContent]);
    final projectDesign = _singleMap(pddAContent[NiasTerm.hasSubject]);
    expect(projectDesign[NiasTerm.hasObjective], isA<List>());
    expect(projectDesign[NiasTerm.hasSpatialLocation], isA<List>());
    expect(projectDesign[NiasTerm.technologyOrMeasure], isA<List>());
    expect(projectDesign[NiasTerm.projectParty], isA<List>());

    final pddB = workflow.documentSeed(PddWorkflowStep.pddB);
    final pddBContent = _singleMap(pddB[NiasTerm.reportContent]);
    expect(pddBContent[NiasTerm.hasDeclaredImpact], isA<List>());
    expect(pddBContent[NiasTerm.impactClaim], isA<List>());

    final pddC = workflow.documentSeed(PddWorkflowStep.pddC);
    expect(pddC[NiasTerm.stakeholderEngagementModalities], isNotNull);
    expect(pddC[NiasTerm.hasSubject], NiasTerm.project);
  });

  test('PDD-CIR gate opens only after approved A, B, and C reviews', () {
    final workflow = PddWorkflowState();

    for (final step in [
      PddWorkflowStep.pddA,
      PddWorkflowStep.pddB,
      PddWorkflowStep.pddC,
    ]) {
      workflow.submit(step, workflow.documentSeed(step));
    }

    expect(workflow.gateResult().allowed, isFalse);

    for (final section in ReviewSection.values) {
      final seed = workflow.reviewSeed(section);
      // Explicitly approve: the conservative default is reject.
      seed[NiasTerm.finalReviewDecision] = NiasTerm.reviewApprove;
      workflow.submit(section.reviewStep, seed);
    }

    expect(workflow.gateResult().allowed, isTrue);
    expect(
      workflow.canOpen(PddWorkflowStep.pddCir, WorkflowRole.developer),
      isTrue,
    );
  });

  test('rejected review blocks PDD-CIR', () {
    final workflow = PddWorkflowState();
    workflow.submit(
      PddWorkflowStep.pddA,
      workflow.documentSeed(PddWorkflowStep.pddA),
    );
    workflow.submit(
      PddWorkflowStep.pddB,
      workflow.documentSeed(PddWorkflowStep.pddB),
    );
    workflow.submit(
      PddWorkflowStep.pddC,
      workflow.documentSeed(PddWorkflowStep.pddC),
    );

    workflow.submit(
      ReviewSection.a.reviewStep,
      workflow.reviewSeed(ReviewSection.a),
    );

    final rejected = workflow.reviewSeed(ReviewSection.b);
    rejected[NiasTerm.finalReviewDecision] = NiasTerm.reviewReject;
    workflow.submit(ReviewSection.b.reviewStep, rejected);

    workflow.submit(
      ReviewSection.c.reviewStep,
      workflow.reviewSeed(ReviewSection.c),
    );

    final gate = workflow.gateResult();
    expect(gate.allowed, isFalse);
    expect(gate.failures, contains('PDD-B validation review is not approved.'));
  });

  test('reviewSeed emits reviewTarget and no fieldKey', () {
    final workflow = PddWorkflowState();

    for (final step in [
      PddWorkflowStep.pddA,
      PddWorkflowStep.pddB,
      PddWorkflowStep.pddC,
    ]) {
      workflow.submit(step, workflow.documentSeed(step));
    }

    for (final section in ReviewSection.values) {
      final seed = workflow.reviewSeed(section);
      final fieldReviews = seed['${NiasTerm.base}fieldReview'] as List<dynamic>;
      expect(fieldReviews, isNotEmpty);

      for (final entry in fieldReviews) {
        final review = entry as Map<String, dynamic>;
        expect(review.containsKey('${NiasTerm.base}fieldKey'), isFalse,
            reason: 'fieldKey must not appear in reviewSeed output');
        final targetList = review['${NiasTerm.base}reviewTarget'];
        expect(targetList, isA<List>(),
            reason:
                'reviewTarget must be a list-wrapped node (sh:node subform)');
        final targetMap =
            (targetList as List<dynamic>).first as Map<String, dynamic>;
        expect(targetMap['${NiasTerm.base}reviewedArtifact'], isNotNull);
        expect(targetMap['${NiasTerm.base}reviewedAnchor'], isNotNull);
      }
    }
  });

  test('wrong reviewed document link blocks PDD-CIR', () {
    final workflow = PddWorkflowState();
    workflow.submit(
      PddWorkflowStep.pddA,
      workflow.documentSeed(PddWorkflowStep.pddA),
    );
    workflow.submit(
      PddWorkflowStep.pddB,
      workflow.documentSeed(PddWorkflowStep.pddB),
    );
    workflow.submit(
      PddWorkflowStep.pddC,
      workflow.documentSeed(PddWorkflowStep.pddC),
    );

    workflow.submit(
      ReviewSection.a.reviewStep,
      workflow.reviewSeed(ReviewSection.a),
    );

    final wrongReview = workflow.reviewSeed(ReviewSection.b);
    wrongReview[NiasTerm.isReviewOf] =
        '${NiasTerm.base}documents/some-other-document';
    workflow.submit(ReviewSection.b.reviewStep, wrongReview);

    workflow.submit(
      ReviewSection.c.reviewStep,
      workflow.reviewSeed(ReviewSection.c),
    );

    final gate = workflow.gateResult();
    expect(gate.allowed, isFalse);
    expect(
      gate.failures,
      contains('PDD-B review does not point to the submitted document.'),
    );
  });
}

Map<String, dynamic> _singleMap(dynamic value) {
  final list = value as List<dynamic>;
  expect(list, hasLength(1));
  return list.single as Map<String, dynamic>;
}
