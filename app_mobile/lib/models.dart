import 'dart:convert';

class AccountSnapshot {
  const AccountSnapshot({
    required this.id,
    required this.nomeAluno,
    required this.saldo,
    required this.vetorAtual,
    this.pendente = false,
  });

  final int id;
  final String nomeAluno;
  final double saldo;
  final List<int> vetorAtual;
  final bool pendente;

  AccountSnapshot copyWith({
    double? saldo,
    List<int>? vetorAtual,
    bool? pendente,
  }) => AccountSnapshot(
    id: id,
    nomeAluno: nomeAluno,
    saldo: saldo ?? this.saldo,
    vetorAtual: vetorAtual ?? this.vetorAtual,
    pendente: pendente ?? this.pendente,
  );

  Map<String, dynamic> toJson() => {
    'id': id,
    'nomeAluno': nomeAluno,
    'saldo': saldo,
    'vetorAtual': vetorAtual,
    'pendente': pendente,
  };

  factory AccountSnapshot.fromJson(Map<String, dynamic> json) =>
      AccountSnapshot(
        id: json['id'] as int,
        nomeAluno: json['nomeAluno'] as String,
        saldo: (json['saldo'] as num).toDouble(),
        vetorAtual: (json['vetorAtual'] as List<dynamic>? ?? const <dynamic>[])
            .map((item) => item as int)
            .toList(),
        pendente: json['pendente'] as bool? ?? false,
      );
}

class PendingOperation {
  const PendingOperation({
    required this.id,
    required this.contaId,
    required this.tipo,
    required this.valor,
    required this.vetorConhecido,
    this.conflito = false,
  });

  final String id;
  final int contaId;
  final String tipo;
  final double valor;
  final List<int> vetorConhecido;
  final bool conflito;

  PendingOperation copyWith({bool? conflito}) => PendingOperation(
    id: id,
    contaId: contaId,
    tipo: tipo,
    valor: valor,
    vetorConhecido: vetorConhecido,
    conflito: conflito ?? this.conflito,
  );

  Map<String, dynamic> toJson() => {
    'id': id,
    'contaId': contaId,
    'tipo': tipo,
    'valor': valor,
    'vetorConhecido': vetorConhecido,
    'conflito': conflito,
  };

  factory PendingOperation.fromJson(Map<String, dynamic> json) =>
      PendingOperation(
        id: json['id'] as String,
        contaId: json['contaId'] as int,
        tipo: json['tipo'] as String,
        valor: (json['valor'] as num).toDouble(),
        vetorConhecido: (json['vetorConhecido'] as List<dynamic>)
            .map((item) => item as int)
            .toList(),
        conflito: json['conflito'] as bool? ?? false,
      );
}

class SessionData {
  const SessionData({required this.token, required this.agenciaId});

  final String token;
  final int agenciaId;

  Map<String, dynamic> toJson() => {'token': token, 'agenciaId': agenciaId};

  factory SessionData.fromJson(Map<String, dynamic> json) => SessionData(
    token: json['token'] as String,
    agenciaId: json['agenciaId'] as int,
  );

  String encode() => jsonEncode(toJson());
  static SessionData decode(String source) =>
      SessionData.fromJson(jsonDecode(source));
}
