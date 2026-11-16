// This is a basic Flutter widget test.
//
// To perform an interaction with a widget in your test, use the WidgetTester
// utility in the flutter_test package. For example, you can send tap and scroll
// gestures. You can also use WidgetTester to find child widgets in the widget
// tree, read text, and verify that the values of widget properties are correct.

import 'package:flutter_test/flutter_test.dart';

import 'package:iceibank_mobile/models.dart';

void main() {
  test('saldo salvo preserva o vetor e o estado pendente', () {
    final snapshot = AccountSnapshot.fromJson({
      'id': 12,
      'nomeAluno': 'Ana',
      'saldo': 50.0,
      'vetorAtual': [1, 2, 3],
      'pendente': true,
    });

    expect(snapshot.id, 12);
    expect(snapshot.vetorAtual, [1, 2, 3]);
    expect(snapshot.pendente, isTrue);
  });
}
