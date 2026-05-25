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
}
