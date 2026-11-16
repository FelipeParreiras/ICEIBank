import 'dart:convert';

import 'package:shared_preferences/shared_preferences.dart';

import 'models.dart';

class LocalStore {
  static const _sessionKey = 'session';
  static const _accountsKey = 'accounts';
  static const _pendingKey = 'pending_operations';

  Future<SharedPreferences> get _preferences => SharedPreferences.getInstance();

  Future<SessionData?> readSession() async {
    final source = (await _preferences).getString(_sessionKey);
    return source == null ? null : SessionData.decode(source);
  }

  Future<void> saveSession(SessionData session) async {
    await (await _preferences).setString(_sessionKey, session.encode());
  }

  Future<void> clearSession() async => (await _preferences).remove(_sessionKey);

  Future<Map<int, AccountSnapshot>> readAccounts() async {
    final source = (await _preferences).getString(_accountsKey);
    if (source == null) return {};
    final items = jsonDecode(source) as List<dynamic>;
    return {
      for (final item in items)
        (item as Map<String, dynamic>)['id'] as int: AccountSnapshot.fromJson(
          item,
        ),
    };
  }

  Future<void> saveAccounts(Map<int, AccountSnapshot> accounts) async {
    final values = accounts.values.map((account) => account.toJson()).toList();
    await (await _preferences).setString(_accountsKey, jsonEncode(values));
  }

  Future<List<PendingOperation>> readPending() async {
    final source = (await _preferences).getString(_pendingKey);
    if (source == null) return [];
    return (jsonDecode(source) as List<dynamic>)
        .map((item) => PendingOperation.fromJson(item as Map<String, dynamic>))
        .toList();
  }

  Future<void> savePending(List<PendingOperation> pending) async {
    await (await _preferences).setString(
      _pendingKey,
      jsonEncode(pending.map((operation) => operation.toJson()).toList()),
    );
  }
}
