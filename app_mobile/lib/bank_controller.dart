import 'dart:async';

import 'package:connectivity_plus/connectivity_plus.dart';
import 'package:flutter/foundation.dart';

import 'api_client.dart';
import 'local_store.dart';
import 'models.dart';

class BankController extends ChangeNotifier {
  BankController({ApiClient? api, LocalStore? store})
    : _api = api ?? ApiClient(),
      _store = store ?? LocalStore();

  final ApiClient _api;
  final LocalStore _store;
  final Map<int, AccountSnapshot> accounts = {};
  List<PendingOperation> pending = [];
  SessionData? session;
  int? liderAtual;
  String? feedback;
  bool carregando = true;
  bool online = true;
  Timer? _leaderTimer;
  StreamSubscription<List<ConnectivityResult>>? _connectivitySubscription;

  bool get autenticado => session != null;
  int get pendenciasAtivas =>
      pending.where((operation) => !operation.conflito).length;
  int get conflitos => pending.where((operation) => operation.conflito).length;

  Future<void> inicializar() async {
    accounts.addAll(await _store.readAccounts());
    pending = await _store.readPending();
    session = await _store.readSession();
    _connectivitySubscription = Connectivity().onConnectivityChanged.listen((
      results,
    ) {
      online = !results.contains(ConnectivityResult.none);
      notifyListeners();
      if (online && autenticado) {
        sincronizarPendentes();
        atualizarLider();
      }
    });
    carregando = false;
    if (autenticado) {
      _iniciarAtualizacaoLider();
      await sincronizarPendentes();
      await atualizarLider();
    }
    notifyListeners();
  }

  Future<bool> login(int agenciaId, String usuario, String senha) async {
    _limparFeedback();
    try {
      final token = await _api.login(agenciaId, usuario, senha);
      session = SessionData(token: token, agenciaId: agenciaId);
      await _store.saveSession(session!);
      _iniciarAtualizacaoLider();
      await atualizarLider();
      notifyListeners();
      return true;
    } on ApiException catch (error) {
      feedback = error.message;
      notifyListeners();
      return false;
    }
  }

  Future<void> logout() async {
    session = null;
    liderAtual = null;
    _leaderTimer?.cancel();
    await _store.clearSession();
    notifyListeners();
  }

  Future<void> consultarSaldo(int contaId) async {
    _limparFeedback();
    try {
      final snapshot = await _api.consultarSaldo(
        _agenciaDaConta(contaId),
        _token,
        contaId,
      );
      await _guardarConta(snapshot);
      online = true;
    } on ApiException catch (error) {
      online = error.statusCode != null;
      final cached = accounts[contaId];
      feedback = cached == null
          ? error.message
          : 'Sem conexão: exibindo o último saldo salvo neste aparelho.';
    }
    notifyListeners();
  }

  Future<void> movimentar(int contaId, String tipo, double valor) async {
    _limparFeedback();
    if (valor <= 0) {
      feedback = 'Informe um valor maior que zero.';
      notifyListeners();
      return;
    }
    try {
      final snapshot = await _api.movimentar(
        _agenciaDaConta(contaId),
        _token,
        contaId,
        tipo,
        valor,
      );
      await _guardarConta(snapshot);
      online = true;
    } on ApiException catch (error) {
      if (error.statusCode != null) {
        feedback = error.message;
      } else {
        await _registrarPendente(contaId, tipo, valor);
      }
    }
    notifyListeners();
  }

  Future<void> transferir(int origem, int destino, double valor) async {
    _limparFeedback();
    try {
      await _api.transferir(
        _agenciaDaConta(origem),
        _token,
        origem,
        destino,
        valor,
      );
      feedback =
          'Transferência enviada. O crédito entre agências é assíncrono.';
      await consultarSaldo(origem);
    } on ApiException catch (error) {
      feedback = error.message;
      notifyListeners();
    }
  }

  Future<void> atualizarLider() async {
    for (var agenciaId = 0; agenciaId < 3; agenciaId++) {
      try {
        liderAtual = await _api.obterLider(agenciaId);
        online = true;
        notifyListeners();
        return;
      } on ApiException {
        continue;
      }
    }
    liderAtual = null;
    online = false;
    notifyListeners();
  }

  Future<void> sincronizarPendentes() async {
    if (!autenticado || pending.isEmpty) return;
    final remaining = <PendingOperation>[];
    for (final operation in pending) {
      if (operation.conflito) {
        remaining.add(operation);
        continue;
      }
      try {
        final snapshot = await _api.sincronizar(
          _agenciaDaConta(operation.contaId),
          _token,
          operation,
        );
        await _guardarConta(snapshot);
        feedback = 'Operação offline sincronizada com sucesso.';
      } on ApiException catch (error) {
        if (error.statusCode == 409 && error.payload != null) {
          final atual = error.payload!['contaAtual'] as Map<String, dynamic>;
          final vetor = error.payload!['vetorAtual'] as List<dynamic>;
          await _guardarConta(
            AccountSnapshot.fromJson({...atual, 'vetorAtual': vetor}),
          );
          remaining.add(operation.copyWith(conflito: true));
          feedback = 'Conflito: o saldo real foi atualizado; a operação pendente exige revisão.';
        } else if (error.statusCode == null) {
          remaining.add(operation);
          break;
        } else {
          remaining.add(operation.copyWith(conflito: true));
          feedback = error.message;
        }
      }
    }
    pending = remaining;
    for (final entry in accounts.entries.toList()) {
      accounts[entry.key] = entry.value.copyWith(
        pendente: pending.any(
          (operation) => operation.contaId == entry.key && !operation.conflito,
        ),
      );
    }
    await _store.saveAccounts(accounts);
    await _store.savePending(pending);
    notifyListeners();
  }

  Future<void> _registrarPendente(
    int contaId,
    String tipo,
    double valor,
  ) async {
    final atual = accounts[contaId];
    if (atual == null || atual.vetorAtual.length != 3) {
      feedback = 'Sem conexão e sem saldo salvo para esta conta. Consulte-a online antes.';
      return;
    }
    if (tipo == 'SAQUE' && atual.saldo < valor) {
      feedback = 'Saldo em cache insuficiente para registrar o saque offline.';
      return;
    }
    final operation = PendingOperation(
      id: DateTime.now().microsecondsSinceEpoch.toString(),
      contaId: contaId,
      tipo: tipo,
      valor: valor,
      vetorConhecido: atual.vetorAtual,
    );
    pending = [...pending, operation];
    final saldo = tipo == 'DEPOSITO'
        ? atual.saldo + valor
        : atual.saldo - valor;
    await _guardarConta(atual.copyWith(saldo: saldo, pendente: true));
    await _store.savePending(pending);
    online = false;
    feedback =
        'Operação registrada offline e marcada como pendente de sincronização.';
  }

  Future<void> _guardarConta(AccountSnapshot snapshot) async {
    accounts[snapshot.id] = snapshot.copyWith(
      pendente: pending.any(
        (operation) => operation.contaId == snapshot.id && !operation.conflito,
      ),
    );
    await _store.saveAccounts(accounts);
  }

  void _iniciarAtualizacaoLider() {
    _leaderTimer?.cancel();
    _leaderTimer = Timer.periodic(
      const Duration(seconds: 4),
      (_) => atualizarLider(),
    );
  }

  void _limparFeedback() => feedback = null;
  int _agenciaDaConta(int contaId) => contaId % 3;
  String get _token => session!.token;

  @override
  void dispose() {
    _leaderTimer?.cancel();
    _connectivitySubscription?.cancel();
    super.dispose();
  }
}
