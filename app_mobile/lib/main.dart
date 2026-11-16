import 'package:flutter/material.dart';

import 'bank_controller.dart';
import 'models.dart';

void main() {
  final controller = BankController();
  runApp(IceiBankApp(controller: controller));
  controller.inicializar();
}

class IceiBankApp extends StatelessWidget {
  const IceiBankApp({super.key, required this.controller});

  final BankController controller;

  @override
  Widget build(BuildContext context) => MaterialApp(
    title: 'ICEIBank',
    debugShowCheckedModeBanner: false,
    theme: ThemeData(
      colorScheme: ColorScheme.fromSeed(
        seedColor: const Color(0xff1c6141),
        primary: const Color(0xff1c6141),
        secondary: const Color(0xffbd8b2d),
      ),
      useMaterial3: true,
    ),
    home: AnimatedBuilder(
      animation: controller,
      builder: (_, _) {
        if (controller.carregando) {
          return const Scaffold(
            body: Center(child: CircularProgressIndicator()),
          );
        }
        return controller.autenticado
            ? DashboardPage(controller: controller)
            : LoginPage(controller: controller);
      },
    ),
  );
}

class LoginPage extends StatefulWidget {
  const LoginPage({super.key, required this.controller});

  final BankController controller;

  @override
  State<LoginPage> createState() => _LoginPageState();
}

class _LoginPageState extends State<LoginPage> {
  final _usuario = TextEditingController(text: 'aluno');
  final _senha = TextEditingController(text: 'iceibank123');
  var _agencia = 0;
  var _enviando = false;

  @override
  void dispose() {
    _usuario.dispose();
    _senha.dispose();
    super.dispose();
  }

  Future<void> _entrar() async {
    setState(() => _enviando = true);
    final entrou = await widget.controller.login(
      _agencia,
      _usuario.text.trim(),
      _senha.text,
    );
    if (mounted) setState(() => _enviando = false);
    if (!entrou && mounted) _mostrarFeedback(widget.controller.feedback);
  }

  @override
  Widget build(BuildContext context) => Scaffold(
    body: Center(
      child: SingleChildScrollView(
        padding: const EdgeInsets.all(24),
        child: ConstrainedBox(
          constraints: const BoxConstraints(maxWidth: 440),
          child: Card(
            child: Padding(
              padding: const EdgeInsets.all(24),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  Icon(
                    Icons.account_balance,
                    size: 56,
                    color: Theme.of(context).colorScheme.primary,
                  ),
                  const SizedBox(height: 12),
                  Text(
                    'ICEIBank',
                    textAlign: TextAlign.center,
                    style: Theme.of(context).textTheme.headlineMedium,
                  ),
                  const SizedBox(height: 4),
                  const Text(
                    'Acesso seguro às suas contas',
                    textAlign: TextAlign.center,
                  ),
                  const SizedBox(height: 24),
                  TextField(
                    controller: _usuario,
                    decoration: const InputDecoration(labelText: 'Usuário'),
                  ),
                  const SizedBox(height: 12),
                  TextField(
                    controller: _senha,
                    obscureText: true,
                    decoration: const InputDecoration(labelText: 'Senha'),
                  ),
                  const SizedBox(height: 12),
                  DropdownButtonFormField<int>(
                    initialValue: _agencia,
                    decoration: const InputDecoration(
                      labelText: 'Agência para login',
                    ),
                    items: List.generate(
                      3,
                      (id) => DropdownMenuItem(
                        value: id,
                        child: Text('Agência $id'),
                      ),
                    ),
                    onChanged: (value) => setState(() => _agencia = value ?? 0),
                  ),
                  const SizedBox(height: 24),
                  if (widget.controller.feedback != null) ...[
                    Text(
                      widget.controller.feedback!,
                      textAlign: TextAlign.center,
                      style: TextStyle(
                        color: Theme.of(context).colorScheme.error,
                      ),
                    ),
                    const SizedBox(height: 12),
                  ],
                  FilledButton.icon(
                    onPressed: _enviando ? null : _entrar,
                    icon: const Icon(Icons.login),
                    label: Text(_enviando ? 'Entrando...' : 'Entrar'),
                  ),
                ],
              ),
            ),
          ),
        ),
      ),
    ),
  );
}

class DashboardPage extends StatefulWidget {
  const DashboardPage({super.key, required this.controller});

  final BankController controller;

  @override
  State<DashboardPage> createState() => _DashboardPageState();
}

class _DashboardPageState extends State<DashboardPage> {
  final _conta = TextEditingController();
  final _valor = TextEditingController();
  final _destino = TextEditingController();

  @override
  void dispose() {
    _conta.dispose();
    _valor.dispose();
    _destino.dispose();
    super.dispose();
  }

  int? get _contaId => int.tryParse(_conta.text);
  double? get _valorDigitado =>
      double.tryParse(_valor.text.replaceAll(',', '.'));

  Future<void> _consultar() async {
    final conta = _contaId;
    if (conta == null || conta < 0) {
      return _mostrarFeedback('Informe um ID de conta válido.');
    }
    await widget.controller.consultarSaldo(conta);
    if (mounted) _mostrarFeedback(widget.controller.feedback);
  }

  Future<void> _movimentar(String tipo) async {
    final conta = _contaId;
    final valor = _valorDigitado;
    if (conta == null || valor == null) {
      return _mostrarFeedback('Informe conta e valor válidos.');
    }
    await widget.controller.movimentar(conta, tipo, valor);
    if (mounted) _mostrarFeedback(widget.controller.feedback);
  }

  Future<void> _transferir() async {
    final origem = _contaId;
    final destino = int.tryParse(_destino.text);
    final valor = _valorDigitado;
    if (origem == null || destino == null || valor == null) {
      return _mostrarFeedback('Informe origem, destino e valor válidos.');
    }
    await widget.controller.transferir(origem, destino, valor);
    if (mounted) _mostrarFeedback(widget.controller.feedback);
  }

  @override
  Widget build(BuildContext context) {
    final controller = widget.controller;
    final snapshot = _contaId == null ? null : controller.accounts[_contaId];
    return Scaffold(
      appBar: AppBar(
        title: const Text('ICEIBank Mobile'),
        actions: [
          IconButton(
            tooltip: 'Sair',
            onPressed: controller.logout,
            icon: const Icon(Icons.logout),
          ),
        ],
      ),
      body: RefreshIndicator(
        onRefresh: () async {
          await controller.atualizarLider();
          if (_contaId != null) await controller.consultarSaldo(_contaId!);
        },
        child: ListView(
          padding: const EdgeInsets.all(16),
          children: [
            _LeaderPanel(controller: controller),
            const SizedBox(height: 16),
            _StatusPanel(controller: controller),
            if (controller.feedback != null) ...[
              const SizedBox(height: 8),
              Card(
                color: Theme.of(context).colorScheme.errorContainer,
                child: Padding(
                  padding: const EdgeInsets.all(12),
                  child: Text(controller.feedback!),
                ),
              ),
            ],
            const SizedBox(height: 16),
            TextField(
              controller: _conta,
              keyboardType: TextInputType.number,
              onChanged: (_) => setState(() {}),
              decoration: const InputDecoration(
                labelText: 'ID da conta',
                prefixIcon: Icon(Icons.badge_outlined),
              ),
            ),
            const SizedBox(height: 8),
            OutlinedButton.icon(
              onPressed: _consultar,
              icon: const Icon(Icons.refresh),
              label: const Text('Consultar saldo'),
            ),
            if (snapshot != null) ...[
              const SizedBox(height: 12),
              _AccountCard(snapshot: snapshot),
            ],
            const SizedBox(height: 24),
            Text(
              'Movimentações',
              style: Theme.of(context).textTheme.titleLarge,
            ),
            const SizedBox(height: 8),
            TextField(
              controller: _valor,
              keyboardType: const TextInputType.numberWithOptions(
                decimal: true,
              ),
              decoration: const InputDecoration(
                labelText: 'Valor',
                prefixText: 'R\$ ',
              ),
            ),
            const SizedBox(height: 8),
            Row(
              children: [
                Expanded(
                  child: FilledButton(
                    onPressed: () => _movimentar('DEPOSITO'),
                    child: const Text('Depositar'),
                  ),
                ),
                const SizedBox(width: 8),
                Expanded(
                  child: OutlinedButton(
                    onPressed: () => _movimentar('SAQUE'),
                    child: const Text('Sacar'),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 24),
            Text(
              'Transferência',
              style: Theme.of(context).textTheme.titleLarge,
            ),
            const SizedBox(height: 8),
            TextField(
              controller: _destino,
              keyboardType: TextInputType.number,
              decoration: const InputDecoration(
                labelText: 'ID da conta de destino',
              ),
            ),
            const SizedBox(height: 8),
            FilledButton.tonalIcon(
              onPressed: _transferir,
              icon: const Icon(Icons.send),
              label: const Text('Transferir'),
            ),
            if (controller.pending.isNotEmpty) ...[
              const SizedBox(height: 24),
              Text(
                'Operações offline',
                style: Theme.of(context).textTheme.titleLarge,
              ),
              ...controller.pending.map(
                (operation) => ListTile(
                  leading: Icon(
                    operation.conflito
                        ? Icons.warning_amber
                        : Icons.cloud_upload_outlined,
                  ),
                  title: Text(
                    '${operation.tipo == 'DEPOSITO' ? 'Depósito' : 'Saque'} de R\$ ${operation.valor.toStringAsFixed(2)}',
                  ),
                  subtitle: Text(
                    operation.conflito
                        ? 'Conflito: revise o saldo atual.'
                        : 'Pendente de sincronização',
                  ),
                ),
              ),
            ],
          ],
        ),
      ),
    );
  }
}

class _LeaderPanel extends StatelessWidget {
  const _LeaderPanel({required this.controller});

  final BankController controller;

  @override
  Widget build(BuildContext context) => Card(
    color: Theme.of(context).colorScheme.primaryContainer,
    child: ListTile(
      leading: const Icon(Icons.workspace_premium),
      title: const Text('Consenso distribuído'),
      subtitle: Text(
        controller.liderAtual == null
            ? 'Líder indisponível - tentando outras agências.'
            : 'Agência ${controller.liderAtual} é a líder atual.',
      ),
      trailing: IconButton(
        onPressed: controller.atualizarLider,
        icon: const Icon(Icons.sync),
        tooltip: 'Atualizar líder',
      ),
    ),
  );
}

class _StatusPanel extends StatelessWidget {
  const _StatusPanel({required this.controller});

  final BankController controller;

  @override
  Widget build(BuildContext context) => Card(
    child: Padding(
      padding: const EdgeInsets.all(12),
      child: Wrap(
        spacing: 12,
        runSpacing: 8,
        children: [
          Chip(
            avatar: Icon(
              controller.online ? Icons.cloud_done : Icons.cloud_off,
            ),
            label: Text(controller.online ? 'Conectado' : 'Modo offline'),
          ),
          Chip(label: Text('${controller.pendenciasAtivas} pendente(s)')),
          if (controller.conflitos > 0)
            Chip(label: Text('${controller.conflitos} conflito(s)')),
        ],
      ),
    ),
  );
}

class _AccountCard extends StatelessWidget {
  const _AccountCard({required this.snapshot});

  final AccountSnapshot snapshot;

  @override
  Widget build(BuildContext context) => Card(
    child: Padding(
      padding: const EdgeInsets.all(18),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            snapshot.nomeAluno,
            style: Theme.of(context).textTheme.titleMedium,
          ),
          const SizedBox(height: 8),
          Text(
            'R\$ ${snapshot.saldo.toStringAsFixed(2)}',
            style: Theme.of(context).textTheme.headlineMedium,
          ),
          const SizedBox(height: 8),
          Text(
            snapshot.pendente
                ? 'Saldo provisório: há sincronização pendente.'
                : 'Saldo confirmado pela agência.',
          ),
        ],
      ),
    ),
  );
}

void _mostrarFeedback(String? mensagem) {}
