import 'dart:collection';

enum WorkflowRole { developer, validator }

enum ReviewSection { a, b, c }

enum PddWorkflowStep { pddA, pddB, pddC, reviewA, reviewB, reviewC, pddCir }

class NiasTerm {
  static const base = 'https://nova.org.za/novaimpactaccountingstandard/';
  static const dataDocument = 'https://jellyfiiish.xyz/ns/Document';

  static const authProof = '${base}authProof';
  static const documentAuthor = '${base}documentAuthor';
  static const documentMessageId = '${base}documentMessageId';
  static const documentSchema = '${base}documentSchema';
  static const finalReviewDecision = '${base}finalReviewDecision';
  static const hasWorkflowSubmission = '${base}hasWorkflowSubmission';
  static const isEncrypted = '${base}isEncrypted';
  static const isReviewOf = '${base}isReviewOf';
  static const pddSectionAValidationReview =
      '${base}pddSectionAValidationReview';
  static const pddSectionBValidationReview =
      '${base}pddSectionBValidationReview';
  static const pddSectionCValidationReview =
      '${base}pddSectionCValidationReview';
  static const requestedIssuanceAccountId = '${base}requestedIssuanceAccountId';
  static const resourceIpfsUri = '${base}resourceIpfsUri';
  static const workflowSubject = '${base}workflowSubject';
  static const workflowSubmissionConsensusMessage =
      '${base}workflowSubmissionConsensusMessage';

  static const reviewApprove = '${base}review-approve';
  static const reviewReject = '${base}review-reject';
  static const eddsaSignature = '${base}eddsa-signature';

  static const pddASchema = '${base}document-schema/PDDxA-1.0.0';
  static const pddBSchema = '${base}document-schema/PDDxB-9.0.0';
  static const pddCSchema = '${base}document-schema/PDDxC-4.0.0';
  static const pddCirSchema = '${base}document-schema/PDDCIR-3.0.0';
  static const genericReviewSchema =
      '${base}document-schema/GenericDocumentReview-5.0.0';

  static const project = '${base}projects/pdd-alpha';
  static const developer = '${base}users/project-developer-1';
  static const validator = '${base}users/pdd-validator-1';
  static const registry = '${base}registry/nova-registry';
  static const workflow = '${base}workflows/pdd';
}

extension WorkflowRoleLabel on WorkflowRole {
  String get label {
    switch (this) {
      case WorkflowRole.developer:
        return 'Project developer';
      case WorkflowRole.validator:
        return 'PDD validator';
    }
  }
}

extension ReviewSectionDetails on ReviewSection {
  String get label {
    switch (this) {
      case ReviewSection.a:
        return 'PDD-A';
      case ReviewSection.b:
        return 'PDD-B';
      case ReviewSection.c:
        return 'PDD-C';
    }
  }

  String get expectedSchema {
    switch (this) {
      case ReviewSection.a:
        return NiasTerm.pddASchema;
      case ReviewSection.b:
        return NiasTerm.pddBSchema;
      case ReviewSection.c:
        return NiasTerm.pddCSchema;
    }
  }

  String get referencePath {
    switch (this) {
      case ReviewSection.a:
        return NiasTerm.pddSectionAValidationReview;
      case ReviewSection.b:
        return NiasTerm.pddSectionBValidationReview;
      case ReviewSection.c:
        return NiasTerm.pddSectionCValidationReview;
    }
  }

  PddWorkflowStep get sourceStep {
    switch (this) {
      case ReviewSection.a:
        return PddWorkflowStep.pddA;
      case ReviewSection.b:
        return PddWorkflowStep.pddB;
      case ReviewSection.c:
        return PddWorkflowStep.pddC;
    }
  }

  PddWorkflowStep get reviewStep {
    switch (this) {
      case ReviewSection.a:
        return PddWorkflowStep.reviewA;
      case ReviewSection.b:
        return PddWorkflowStep.reviewB;
      case ReviewSection.c:
        return PddWorkflowStep.reviewC;
    }
  }
}

extension PddWorkflowStepDetails on PddWorkflowStep {
  String get label {
    switch (this) {
      case PddWorkflowStep.pddA:
        return 'PDD Section A';
      case PddWorkflowStep.pddB:
        return 'PDD Section B';
      case PddWorkflowStep.pddC:
        return 'PDD Section C';
      case PddWorkflowStep.reviewA:
        return 'Validate PDD-A';
      case PddWorkflowStep.reviewB:
        return 'Validate PDD-B';
      case PddWorkflowStep.reviewC:
        return 'Validate PDD-C';
      case PddWorkflowStep.pddCir:
        return 'PDD-CIR';
    }
  }

  String get documentSchema {
    switch (this) {
      case PddWorkflowStep.pddA:
        return NiasTerm.pddASchema;
      case PddWorkflowStep.pddB:
        return NiasTerm.pddBSchema;
      case PddWorkflowStep.pddC:
        return NiasTerm.pddCSchema;
      case PddWorkflowStep.reviewA:
      case PddWorkflowStep.reviewB:
      case PddWorkflowStep.reviewC:
        return NiasTerm.genericReviewSchema;
      case PddWorkflowStep.pddCir:
        return NiasTerm.pddCirSchema;
    }
  }

  WorkflowRole get requiredRole {
    switch (this) {
      case PddWorkflowStep.reviewA:
      case PddWorkflowStep.reviewB:
      case PddWorkflowStep.reviewC:
        return WorkflowRole.validator;
      case PddWorkflowStep.pddA:
      case PddWorkflowStep.pddB:
      case PddWorkflowStep.pddC:
      case PddWorkflowStep.pddCir:
        return WorkflowRole.developer;
    }
  }

  bool get isReview {
    return this == PddWorkflowStep.reviewA ||
        this == PddWorkflowStep.reviewB ||
        this == PddWorkflowStep.reviewC;
  }

  ReviewSection? get reviewSection {
    switch (this) {
      case PddWorkflowStep.reviewA:
        return ReviewSection.a;
      case PddWorkflowStep.reviewB:
        return ReviewSection.b;
      case PddWorkflowStep.reviewC:
        return ReviewSection.c;
      case PddWorkflowStep.pddA:
      case PddWorkflowStep.pddB:
      case PddWorkflowStep.pddC:
      case PddWorkflowStep.pddCir:
        return null;
    }
  }
}

class WorkflowArtifact {
  final String documentIri;
  final String documentSchema;
  final String workflowSubject;
  final String documentMessageId;
  final String resourceIpfsUri;
  final Map<String, dynamic> payload;

  const WorkflowArtifact({
    required this.documentIri,
    required this.documentSchema,
    required this.workflowSubject,
    required this.documentMessageId,
    required this.resourceIpfsUri,
    required this.payload,
  });

  Map<String, dynamic> toDocumentReference() {
    return {
      '@type': '${NiasTerm.base}DocumentReference',
      NiasTerm.documentMessageId: documentMessageId,
      NiasTerm.resourceIpfsUri: resourceIpfsUri,
    };
  }
}

class GateResult {
  final bool allowed;
  final List<String> failures;

  const GateResult._(this.allowed, this.failures);

  factory GateResult.allowed() => const GateResult._(true, []);
  factory GateResult.blocked(List<String> failures) =>
      GateResult._(false, failures);
}

class PddWorkflowState {
  final Map<PddWorkflowStep, WorkflowArtifact> _submitted = {};

  UnmodifiableMapView<PddWorkflowStep, WorkflowArtifact> get submitted {
    return UnmodifiableMapView(_submitted);
  }

  bool isSubmitted(PddWorkflowStep step) => _submitted.containsKey(step);

  WorkflowArtifact? artifactFor(PddWorkflowStep step) => _submitted[step];

  bool canOpen(PddWorkflowStep step, WorkflowRole role) {
    if (step.requiredRole != role) {
      return false;
    }

    final section = step.reviewSection;
    if (section != null) {
      return _submitted.containsKey(section.sourceStep);
    }

    if (step == PddWorkflowStep.pddCir) {
      return gateResult().allowed;
    }

    return true;
  }

  List<String> blockers(PddWorkflowStep step, WorkflowRole role) {
    final blockers = <String>[];
    if (step.requiredRole != role) {
      blockers.add('Requires ${step.requiredRole.label}.');
    }

    final section = step.reviewSection;
    if (section != null && !_submitted.containsKey(section.sourceStep)) {
      blockers.add('${section.label} must be submitted first.');
    }

    if (step == PddWorkflowStep.pddCir) {
      blockers.addAll(gateResult().failures);
    }

    return blockers;
  }

  WorkflowArtifact submit(PddWorkflowStep step, Map<String, dynamic> payload) {
    final artifact = WorkflowArtifact(
      documentIri: _documentIri(step),
      documentSchema: step.documentSchema,
      workflowSubject: _workflowSubject(payload) ?? NiasTerm.project,
      documentMessageId: _messageId(payload, step),
      resourceIpfsUri: _stringValue(payload[NiasTerm.resourceIpfsUri]) ??
          'ipfs://draft-${step.name.toLowerCase()}',
      payload: Map<String, dynamic>.from(payload),
    );
    _submitted[step] = artifact;
    return artifact;
  }

  GateResult gateResult() {
    final failures = <String>[];
    final resolvedReviews = <String>{};

    for (final section in ReviewSection.values) {
      final source = _submitted[section.sourceStep];
      final review = _submitted[section.reviewStep];

      if (source == null) {
        failures.add('${section.label} has not been submitted.');
        continue;
      }
      if (review == null) {
        failures.add(
          '${section.label} validation review has not been submitted.',
        );
        continue;
      }
      if (review.payload[NiasTerm.finalReviewDecision] !=
          NiasTerm.reviewApprove) {
        failures.add('${section.label} validation review is not approved.');
      }
      if (review.payload[NiasTerm.isReviewOf] != source.documentIri) {
        failures.add(
          '${section.label} review does not point to the submitted document.',
        );
      }
      if (source.documentSchema != section.expectedSchema) {
        failures.add('${section.label} source document has the wrong schema.');
      }
      if (review.workflowSubject != source.workflowSubject) {
        failures.add(
          '${section.label} review workflow subject does not match the source.',
        );
      }
      if (!resolvedReviews.add(review.documentIri)) {
        failures.add(
          '${section.label} review duplicates another review artifact.',
        );
      }
    }

    if (failures.isEmpty) {
      return GateResult.allowed();
    }
    return GateResult.blocked(failures);
  }

  Map<String, dynamic> pddCirSeed() {
    final seed = documentSeed(PddWorkflowStep.pddCir);
    for (final section in ReviewSection.values) {
      final review = _submitted[section.reviewStep];
      if (review != null) {
        seed[section.referencePath] = [review.toDocumentReference()];
      }
    }
    seed[NiasTerm.requestedIssuanceAccountId] = '0.0.2002';
    return seed;
  }

  Map<String, dynamic> documentSeed(PddWorkflowStep step) {
    final submitter = step.requiredRole == WorkflowRole.validator
        ? NiasTerm.validator
        : NiasTerm.developer;
    return {
      NiasTerm.resourceIpfsUri: 'ipfs://draft-${step.name.toLowerCase()}',
      NiasTerm.documentSchema: step.documentSchema,
      NiasTerm.isEncrypted: false,
      NiasTerm.documentAuthor: submitter,
      NiasTerm.authProof: NiasTerm.eddsaSignature,
      NiasTerm.hasWorkflowSubmission: [
        {
          '${NiasTerm.base}submittedDocument': _documentIri(step),
          '${NiasTerm.base}workflow': NiasTerm.workflow,
          '${NiasTerm.base}workflowStep':
              '${NiasTerm.base}workflow-steps/${step.name}',
          NiasTerm.workflowSubject: NiasTerm.project,
          '${NiasTerm.base}workflowDocumentSubmittedBy': submitter,
          '${NiasTerm.base}workflowDocumentRecipient': NiasTerm.registry,
          NiasTerm.workflowSubmissionConsensusMessage: [
            {
              'https://hashgraphontology.xyz/core/inTopic': [
                {'https://hashgraphontology.xyz/core/hasTopicId': '0.0.1001'},
              ],
              'https://hashgraphontology.xyz/core/hasConsensusTimestamp':
                  '2026-01-${_dayForStep(step).toString().padLeft(2, '0')}T00:00:00Z',
            },
          ],
        },
      ],
    };
  }

  Map<String, dynamic> reviewSeed(ReviewSection section) {
    final source = _submitted[section.sourceStep];
    final seed = documentSeed(section.reviewStep);
    seed[NiasTerm.isReviewOf] = source?.documentIri ?? '';
    seed[NiasTerm.finalReviewDecision] = NiasTerm.reviewApprove;
    seed['${NiasTerm.base}fieldReview'] = [
      {
        '@type': '${NiasTerm.base}DocumentFieldReview',
        '${NiasTerm.base}fieldKey': 'section_${section.name}_summary',
        '${NiasTerm.base}fieldTitle': '${section.label} summary',
        '${NiasTerm.base}fieldPrompt':
            'Review the submitted ${section.label} section.',
        '${NiasTerm.base}originalResponse':
            'Submitted ${section.label} payload.',
        '${NiasTerm.base}reviewerDecision': NiasTerm.reviewApprove,
        '${NiasTerm.base}reviewerFeedback':
            'The submitted section is acceptable.',
      },
    ];
    return seed;
  }

  String _documentIri(PddWorkflowStep step) {
    return '${NiasTerm.base}documents/pdd-alpha/${step.name}';
  }

  int _dayForStep(PddWorkflowStep step) {
    return PddWorkflowStep.values.indexOf(step) + 1;
  }

  String _messageId(Map<String, dynamic> payload, PddWorkflowStep step) {
    final submission = _firstMap(payload[NiasTerm.hasWorkflowSubmission]);
    final message = _firstMap(
      submission?[NiasTerm.workflowSubmissionConsensusMessage],
    );
    final topic = _firstMap(
      message?['https://hashgraphontology.xyz/core/inTopic'],
    );
    final topicId = _stringValue(
      topic?['https://hashgraphontology.xyz/core/hasTopicId'],
    );
    final timestamp = _stringValue(
      message?['https://hashgraphontology.xyz/core/hasConsensusTimestamp'],
    );
    if (topicId != null && timestamp != null) {
      return '$topicId-$timestamp';
    }
    return '0.0.1001-2026-01-${_dayForStep(step).toString().padLeft(2, '0')}T00:00:00Z';
  }

  String? _workflowSubject(Map<String, dynamic> payload) {
    final submission = _firstMap(payload[NiasTerm.hasWorkflowSubmission]);
    return _stringValue(submission?[NiasTerm.workflowSubject]);
  }
}

Map<String, dynamic>? _firstMap(Object? value) {
  if (value is Map<String, dynamic>) {
    return value;
  }
  if (value is List &&
      value.isNotEmpty &&
      value.first is Map<String, dynamic>) {
    return value.first as Map<String, dynamic>;
  }
  return null;
}

String? _stringValue(Object? value) {
  if (value == null) {
    return null;
  }
  if (value is String && value.trim().isNotEmpty) {
    return value.trim();
  }
  if (value is Map && value['@id'] is String) {
    return value['@id'] as String;
  }
  if (value is Map && value['@value'] is String) {
    return value['@value'] as String;
  }
  return null;
}
