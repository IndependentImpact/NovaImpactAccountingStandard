import 'package:flutter_test/flutter_test.dart';
import 'package:nias_pdd_workflow_shell/src/workflow_contract.dart';

void main() {
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
      workflow.submit(section.reviewStep, workflow.reviewSeed(section));
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
