import 'dart:convert';

import 'package:flutter/foundation.dart';
import 'package:http/http.dart' as http;

import 'models.dart';

class ApiException implements Exception {
  const ApiException(this.message, {this.statusCode, this.payload});

  final String message;
  final int? statusCode;
  final Map<String, dynamic>? payload;

  @override
  String toString() => message;
}

class ApiClient {
  ApiClient({http.Client? client}) : _client = client ?? http.Client();

  static const _mobileHost = String.fromEnvironment(
    'API_HOST',
    defaultValue: '10.0.2.2',
  );
  final http.Client _client;

  String _baseUrl(int agenciaId) {
    if (kIsWeb) return 'http://localhost:5173/api/agencia-$agenciaId';
    return 'http://$_mobileHost:${4045 + agenciaId}';
  }

  Future<Map<String, dynamic>> _request(
    int agenciaId,
    String method,
    String path, {
    String? token,
    Map<String, dynamic>? body,
  }) async {
    final headers = <String, String>{'Content-Type': 'application/json'};
    if (token != null) headers['Authorization'] = 'Bearer $token';
    final request =
        http.Request(method, Uri.parse('${_baseUrl(agenciaId)}$path'))
          ..headers.addAll(headers)
          ..body = body == null ? '' : jsonEncode(body);
    try {
      final response = await http.Response.fromStream(
        await _client.send(request).timeout(const Duration(seconds: 4)),
      );
      final decoded = response.body.isEmpty
          ? <String, dynamic>{}
          : jsonDecode(response.body) as Map<String, dynamic>;
      if (response.statusCode < 200 || response.statusCode >= 300) {
        final detalhes = decoded['detalhes'] as Map<String, dynamic>?;
        throw ApiException(
          decoded['erro'] as String? ?? 'A agência respondeu com erro.',
          statusCode: response.statusCode,
          payload: detalhes ?? decoded,
        );
      }
      return decoded;
    } on ApiException {
      rethrow;
    } catch (_) {
      throw const ApiException('Não foi possível conectar à agência.');
    }
  }

  Future<String> login(int agenciaId, String usuario, String senha) async {
    final data = await _request(
      agenciaId,
      'POST',
      '/auth/login',
      body: {'usuario': usuario, 'senha': senha},
    );
    return data['accessToken'] as String;
  }

  Future<AccountSnapshot> consultarSaldo(
    int agenciaId,
    String token,
    int contaId,
  ) async {
    final data = await _request(
      agenciaId,
      'GET',
      '/contas/$contaId',
      token: token,
    );
    return AccountSnapshot.fromJson(data);
  }

  Future<AccountSnapshot> movimentar(
    int agenciaId,
    String token,
    int contaId,
    String tipo,
    double valor,
  ) async {
    final path = tipo == 'DEPOSITO' ? 'depositar' : 'sacar';
    final data = await _request(
      agenciaId,
      'POST',
      '/contas/$contaId/$path',
      token: token,
      body: {'valor': valor},
    );
    final atual = await consultarSaldo(agenciaId, token, contaId);
    return atual.copyWith(saldo: double.parse(data['saldo'].toString()));
  }

  Future<AccountSnapshot> sincronizar(
    int agenciaId,
    String token,
    PendingOperation operation,
  ) async {
    final data = await _request(
      agenciaId,
      'POST',
      '/contas/${operation.contaId}/sincronizar',
      token: token,
      body: {
        'tipo': operation.tipo,
        'valor': operation.valor,
        'vetorConhecido': operation.vetorConhecido,
      },
    );
    return AccountSnapshot.fromJson(data);
  }

  Future<void> transferir(
    int agenciaId,
    String token,
    int origem,
    int destino,
    double valor,
  ) async {
    await _request(
      agenciaId,
      'POST',
      '/transferencias',
      token: token,
      body: {'idOrigem': origem, 'idDestino': destino, 'valor': valor},
    );
  }

  Future<int?> obterLider(int agenciaId) async {
    final data = await _request(agenciaId, 'GET', '/bully/lider');
    return data['liderAtual'] as int?;
  }
}
