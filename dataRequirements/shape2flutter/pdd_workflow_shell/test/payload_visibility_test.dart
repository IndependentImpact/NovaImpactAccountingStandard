import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:nias_pdd_workflow_shell/src/pdd_workflow_shell_app.dart';

void main() {
  testWidgets('payload preview is hidden until explicitly opened',
      (tester) async {
    tester.view.physicalSize = const Size(1400, 1000);
    tester.view.devicePixelRatio = 1;
    addTearDown(tester.view.resetPhysicalSize);
    addTearDown(tester.view.resetDevicePixelRatio);

    await tester.pumpWidget(const PddWorkflowShellApp());
    await tester.pumpAndSettle();

    expect(find.text('Payload'), findsNothing);

    await tester.tap(find.byTooltip('Open payload'));
    await tester.pumpAndSettle();

    expect(find.text('Payload'), findsOneWidget);
    expect(find.byTooltip('Close payload'), findsOneWidget);

    await tester.tap(find.byTooltip('Close payload'));
    await tester.pumpAndSettle();

    expect(find.text('Payload'), findsNothing);
    expect(find.byTooltip('Open payload'), findsOneWidget);
  });

  testWidgets('artifact identity panel starts collapsed and can be expanded',
      (tester) async {
    tester.view.physicalSize = const Size(1400, 1000);
    tester.view.devicePixelRatio = 1;
    addTearDown(tester.view.resetPhysicalSize);
    addTearDown(tester.view.resetDevicePixelRatio);

    await tester.pumpWidget(const PddWorkflowShellApp());
    await tester.pumpAndSettle();

    // The panel title is visible but the content rows are hidden by default.
    expect(find.text('Artifact identity'), findsOneWidget);
    expect(
      find.text('Auto-populated by the system — expand to review'),
      findsWidgets,
    );
    expect(find.text('IPFS URI'), findsNothing);

    // Expanding the tile reveals the identity field rows.
    await tester.tap(find.text('Artifact identity'));
    await tester.pumpAndSettle();

    expect(find.text('IPFS URI'), findsOneWidget);
    expect(find.text('Encrypted'), findsOneWidget);

    // Collapsing again hides the rows.
    await tester.tap(find.text('Artifact identity'));
    await tester.pumpAndSettle();

    expect(find.text('IPFS URI'), findsNothing);
  });

  testWidgets('document details panel starts collapsed and can be expanded',
      (tester) async {
    tester.view.physicalSize = const Size(1400, 1000);
    tester.view.devicePixelRatio = 1;
    addTearDown(tester.view.resetPhysicalSize);
    addTearDown(tester.view.resetDevicePixelRatio);

    await tester.pumpWidget(const PddWorkflowShellApp());
    await tester.pumpAndSettle();

    expect(find.text('Document details'), findsOneWidget);
    expect(find.text('Document schema IRI'), findsNothing);

    await tester.tap(find.text('Document details'));
    await tester.pumpAndSettle();

    expect(find.text('Document schema IRI'), findsOneWidget);
    expect(find.text('Document author'), findsOneWidget);
    expect(find.text('Authenticity proof'), findsOneWidget);

    await tester.tap(find.text('Document details'));
    await tester.pumpAndSettle();

    expect(find.text('Document schema IRI'), findsNothing);
  });

  testWidgets(
      'workflow submission panel starts collapsed and can be expanded',
      (tester) async {
    tester.view.physicalSize = const Size(1400, 1000);
    tester.view.devicePixelRatio = 1;
    addTearDown(tester.view.resetPhysicalSize);
    addTearDown(tester.view.resetDevicePixelRatio);

    await tester.pumpWidget(const PddWorkflowShellApp());
    await tester.pumpAndSettle();

    expect(find.text('Workflow submission'), findsOneWidget);
    expect(find.text('Workflow subject'), findsNothing);

    await tester.tap(find.text('Workflow submission'));
    await tester.pumpAndSettle();

    expect(find.text('Workflow subject'), findsOneWidget);
    expect(find.text('Submission topic'), findsOneWidget);

    await tester.tap(find.text('Workflow submission'));
    await tester.pumpAndSettle();

    expect(find.text('Workflow subject'), findsNothing);
  });
}
