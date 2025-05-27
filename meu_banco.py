from flask import Flask, request, jsonify
from datetime import datetime

app = Flask(__name__)

# Armazenamento de dados em memória
clientes = []
contas = []
AGENCIA = "0001"
numero_conta_sequencial = 1

def validar_cpf(cpf):
    """Valida se o CPF já existe no sistema"""
    for cliente in clientes:
        if cliente['cpf'] == cpf:
            return False
    return True

def buscar_cliente_por_cpf(cpf):
    """Busca um cliente pelo CPF"""
    for cliente in clientes:
        if cliente['cpf'] == cpf:
            return cliente
    return None

def criar_cliente(nome, data_nascimento, cpf, logradouro, numero, bairro, cidade_uf):
    """Cria um novo cliente no sistema"""
    if not validar_cpf(cpf):
        return {"sucesso": False, "mensagem": "CPF já cadastrado no sistema!"}
    
    cliente = {
        "nome": nome,
        "data_nascimento": data_nascimento,
        "cpf": cpf,
        "endereco": {
            "logradouro": logradouro,
            "numero": numero,
            "bairro": bairro,
            "cidade_uf": cidade_uf
        }
    }
    
    clientes.append(cliente)
    return {"sucesso": True, "mensagem": "Cliente cadastrado com sucesso!", "cliente": cliente}

def criar_conta_bancaria(cpf):
    """Cria uma nova conta bancária para um cliente existente"""
    global numero_conta_sequencial
    
    cliente = buscar_cliente_por_cpf(cpf)
    if not cliente:
        return {"sucesso": False, "mensagem": "Cliente não encontrado! Cadastre o cliente primeiro."}
    
    conta = {
        "agencia": AGENCIA,
        "numero_conta": numero_conta_sequencial,
        "cpf_titular": cpf,
        "saldo": 0,
        "extrato": [],
        "numero_saques_hoje": 0,
        "limite_saque": 500,
        "limite_saques_diarios": 3
    }
    
    contas.append(conta)
    numero_conta_sequencial += 1
    
    return {"sucesso": True, "mensagem": f"Conta {conta['numero_conta']} criada com sucesso!", "conta": conta}

def buscar_conta(numero_conta):
    """Busca uma conta pelo número"""
    for conta in contas:
        if conta['numero_conta'] == int(numero_conta):
            return conta
    return None

def deposito(saldo, valor, extrato, /):
    """
    Função de depósito com argumentos positional-only
    Args:
        saldo: saldo atual da conta
        valor: valor a ser depositado
        extrato: lista de transações
    Returns:
        tuple: (novo_saldo, extrato_atualizado)
    """
    if valor <= 0:
        raise ValueError("Valor inválido! Tente novamente com um valor acima de 0.")
    
    novo_saldo = saldo + valor
    transacao = {
        "tipo": "Depósito",
        "valor": valor,
        "data_hora": datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    }
    extrato.append(transacao)
    
    return novo_saldo, extrato

def saque(*, saldo, valor, extrato, limite, numero_saques, limite_saques):
    """
    Função de saque com argumentos keyword-only
    Args:
        saldo: saldo atual da conta
        valor: valor a ser sacado
        extrato: lista de transações
        limite: limite por saque
        numero_saques: número de saques já realizados hoje
        limite_saques: limite de saques diários
    Returns:
        tuple: (novo_saldo, extrato_atualizado, numero_saques_atualizado)
    """
    if numero_saques >= limite_saques:
        raise ValueError("Você atingiu o limite de saques diário (3). Tente novamente em 24 horas!")
    
    if valor > limite:
        raise ValueError(f"O valor limite por saque é de R$ {limite:.2f}. Solicite um valor menor!")
    
    if valor > saldo:
        raise ValueError(f"Saldo insuficiente! Seu saldo atual é de R$ {saldo:.2f}")
    
    if valor <= 0:
        raise ValueError("Valor inválido! Digite um valor acima de 0.")
    
    novo_saldo = saldo - valor
    transacao = {
        "tipo": "Saque",
        "valor": valor,
        "data_hora": datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    }
    extrato.append(transacao)
    
    return novo_saldo, extrato, numero_saques + 1

def exibir_extrato(saldo, /, *, extrato):
    """
    Função de extrato com argumentos mistos
    Args:
        saldo: saldo atual (posicional)
        extrato: lista de transações (nomeado)
    Returns:
        dict: informações do extrato formatadas
    """
    total_depositos = sum(t['valor'] for t in extrato if t['tipo'] == 'Depósito')
    total_saques = sum(t['valor'] for t in extrato if t['tipo'] == 'Saque')
    numero_depositos = len([t for t in extrato if t['tipo'] == 'Depósito'])
    numero_saques = len([t for t in extrato if t['tipo'] == 'Saque'])
    
    return {
        "saldo": saldo,
        "transacoes": extrato,
        "total_depositos": total_depositos,
        "total_saques": total_saques,
        "numero_depositos": numero_depositos,
        "numero_saques": numero_saques
    }

# Interface HTML integrada no código Python
HTML_INTERFACE = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Sistema Bancário - Arquivo Único</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background-color: #f5f5f5; }
        .container { max-width: 800px; margin: 0 auto; background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        h1 { color: #2c3e50; text-align: center; }
        .menu { display: flex; justify-content: center; gap: 10px; margin-bottom: 30px; }
        .menu button { padding: 10px 20px; background-color: #3498db; color: white; border: none; border-radius: 5px; cursor: pointer; }
        .menu button:hover { background-color: #2980b9; }
        .menu button.active { background-color: #27ae60; }
        .section { display: none; padding: 20px; background-color: #f8f9fa; border-radius: 8px; margin-bottom: 20px; }
        .section.active { display: block; }
        .form-group { margin-bottom: 15px; }
        label { display: block; margin-bottom: 5px; font-weight: bold; color: #34495e; }
        input { width: 100%; padding: 8px; border: 1px solid #ddd; border-radius: 4px; box-sizing: border-box; }
        button { background-color: #27ae60; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; }
        button:hover { background-color: #229954; }
        .alert { padding: 10px; margin: 10px 0; border-radius: 5px; }
        .alert-success { background-color: #d4edda; color: #155724; border: 1px solid #c3e6cb; }
        .alert-error { background-color: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; }
        .two-columns { display: grid; grid-template-columns: 1fr 1fr; gap: 15px; }
        .result { background: white; padding: 15px; margin: 10px 0; border-radius: 5px; border-left: 4px solid #3498db; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🏦 Sistema Bancário - Arquivo Único</h1>
        
        <div class="menu">
            <button onclick="showSection('cliente')" class="active">Cliente</button>
            <button onclick="showSection('conta')">Conta</button>
            <button onclick="showSection('deposito')">Depósito</button>
            <button onclick="showSection('saque')">Saque</button>
            <button onclick="showSection('extrato')">Extrato</button>
        </div>

        <div id="alerts"></div>

        <!-- Seção Cliente -->
        <div id="cliente" class="section active">
            <h2>📋 Cadastrar Cliente</h2>
            <form onsubmit="criarCliente(event)">
                <div class="two-columns">
                    <div class="form-group">
                        <label>Nome:</label>
                        <input type="text" id="nome" required>
                    </div>
                    <div class="form-group">
                        <label>Data Nascimento:</label>
                        <input type="date" id="data_nascimento" required>
                    </div>
                </div>
                <div class="form-group">
                    <label>CPF:</label>
                    <input type="text" id="cpf" placeholder="12345678901" required>
                </div>
                <div class="two-columns">
                    <div class="form-group">
                        <label>Logradouro:</label>
                        <input type="text" id="logradouro" required>
                    </div>
                    <div class="form-group">
                        <label>Número:</label>
                        <input type="text" id="numero" required>
                    </div>
                </div>
                <div class="two-columns">
                    <div class="form-group">
                        <label>Bairro:</label>
                        <input type="text" id="bairro" required>
                    </div>
                    <div class="form-group">
                        <label>Cidade/UF:</label>
                        <input type="text" id="cidade_uf" placeholder="São Paulo/SP" required>
                    </div>
                </div>
                <button type="submit">💾 Cadastrar</button>
            </form>
        </div>

        <!-- Seção Conta -->
        <div id="conta" class="section">
            <h2>💳 Criar Conta</h2>
            <form onsubmit="criarConta(event)">
                <div class="form-group">
                    <label>CPF do Cliente:</label>
                    <input type="text" id="cpf_conta" placeholder="12345678901" required>
                </div>
                <button type="submit">🆕 Criar Conta</button>
            </form>
            <button onclick="listarContas()" style="margin-top: 10px; background-color: #3498db;">📋 Listar Contas</button>
            <div id="listaContas"></div>
        </div>

        <!-- Seção Depósito -->
        <div id="deposito" class="section">
            <h2>📈 Depósito</h2>
            <form onsubmit="realizarDeposito(event)">
                <div class="form-group">
                    <label>Número da Conta:</label>
                    <input type="number" id="conta_deposito" required>
                </div>
                <div class="form-group">
                    <label>Valor (R$):</label>
                    <input type="number" id="valor_deposito" step="0.01" min="0.01" required>
                </div>
                <button type="submit">💸 Depositar</button>
            </form>
        </div>

        <!-- Seção Saque -->
        <div id="saque" class="section">
            <h2>📉 Saque</h2>
            <form onsubmit="realizarSaque(event)">
                <div class="form-group">
                    <label>Número da Conta:</label>
                    <input type="number" id="conta_saque" required>
                </div>
                <div class="form-group">
                    <label>Valor (R$):</label>
                    <input type="number" id="valor_saque" step="0.01" min="0.01" max="500" required>
                    <small>Limite: R$ 500 por saque (máx. 3 saques/dia)</small>
                </div>
                <button type="submit" style="background-color: #e74c3c;">💵 Sacar</button>
            </form>
        </div>

        <!-- Seção Extrato -->
        <div id="extrato" class="section">
            <h2>📊 Extrato</h2>
            <div class="form-group">
                <label>Número da Conta:</label>
                <input type="number" id="conta_extrato" required>
            </div>
            <button onclick="consultarExtrato()" style="background-color: #3498db;">📋 Ver Extrato</button>
            <div id="extratoResults"></div>
        </div>
    </div>

    <script>
        function showAlert(message, type = 'success') {
            const alertsDiv = document.getElementById('alerts');
            const alertClass = type === 'success' ? 'alert-success' : 'alert-error';
            alertsDiv.innerHTML = `<div class="alert ${alertClass}">${message}</div>`;
            setTimeout(() => alertsDiv.innerHTML = '', 5000);
        }

        function showSection(sectionName) {
            document.querySelectorAll('.section').forEach(section => section.classList.remove('active'));
            document.getElementById(sectionName).classList.add('active');
            document.querySelectorAll('.menu button').forEach(btn => btn.classList.remove('active'));
            event.target.classList.add('active');
        }

        async function criarCliente(event) {
            event.preventDefault();
            const formData = {
                nome: document.getElementById('nome').value,
                data_nascimento: document.getElementById('data_nascimento').value,
                cpf: document.getElementById('cpf').value,
                logradouro: document.getElementById('logradouro').value,
                numero: document.getElementById('numero').value,
                bairro: document.getElementById('bairro').value,
                cidade_uf: document.getElementById('cidade_uf').value
            };
            
            try {
                const response = await fetch('/criar_cliente', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify(formData)
                });
                const result = await response.json();
                showAlert(result.sucesso ? '✅ ' + result.mensagem : '❌ ' + result.mensagem, result.sucesso ? 'success' : 'error');
                if (result.sucesso) event.target.reset();
            } catch (error) {
                showAlert('❌ Erro: ' + error.message, 'error');
            }
        }

        async function criarConta(event) {
            event.preventDefault();
            const cpf = document.getElementById('cpf_conta').value;
            
            try {
                const response = await fetch('/criar_conta', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ cpf: cpf })
                });
                const result = await response.json();
                showAlert(result.sucesso ? '✅ ' + result.mensagem : '❌ ' + result.mensagem, result.sucesso ? 'success' : 'error');
                if (result.sucesso) event.target.reset();
            } catch (error) {
                showAlert('❌ Erro: ' + error.message, 'error');
            }
        }

        async function listarContas() {
            try {
                const response = await fetch('/listar_contas');
                const contas = await response.json();
                const lista = document.getElementById('listaContas');
                
                if (contas.length > 0) {
                    let html = '<h3>Contas Cadastradas:</h3>';
                    contas.forEach(conta => {
                        html += `<div class="result">
                            <strong>Conta: ${conta.agencia}-${conta.numero_conta}</strong><br>
                            Titular: ${conta.titular}<br>
                            CPF: ${conta.cpf}<br>
                            Saldo: R$ ${conta.saldo.toFixed(2)}
                        </div>`;
                    });
                    lista.innerHTML = html;
                } else {
                    lista.innerHTML = '<p>Nenhuma conta cadastrada.</p>';
                }
            } catch (error) {
                showAlert('❌ Erro: ' + error.message, 'error');
            }
        }

        async function realizarDeposito(event) {
            event.preventDefault();
            const formData = {
                numero_conta: document.getElementById('conta_deposito').value,
                valor: document.getElementById('valor_deposito').value
            };
            
            try {
                const response = await fetch('/depositar', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify(formData)
                });
                const result = await response.json();
                showAlert(result.sucesso ? `✅ ${result.mensagem} Saldo: R$ ${result.saldo.toFixed(2)}` : '❌ ' + result.mensagem, result.sucesso ? 'success' : 'error');
                if (result.sucesso) event.target.reset();
            } catch (error) {
                showAlert('❌ Erro: ' + error.message, 'error');
            }
        }

        async function realizarSaque(event) {
            event.preventDefault();
            const formData = {
                numero_conta: document.getElementById('conta_saque').value,
                valor: document.getElementById('valor_saque').value
            };
            
            try {
                const response = await fetch('/sacar', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify(formData)
                });
                const result = await response.json();
                showAlert(result.sucesso ? `✅ ${result.mensagem} Saldo: R$ ${result.saldo.toFixed(2)}` : '❌ ' + result.mensagem, result.sucesso ? 'success' : 'error');
                if (result.sucesso) event.target.reset();
            } catch (error) {
                showAlert('❌ Erro: ' + error.message, 'error');
            }
        }

        async function consultarExtrato() {
            const numeroConta = document.getElementById('conta_extrato').value;
            if (!numeroConta) {
                showAlert('❌ Digite o número da conta', 'error');
                return;
            }
            
            try {
                const response = await fetch(`/extrato/${numeroConta}`);
                const result = await response.json();
                
                if (result.sucesso) {
                    let html = `<h3>📋 Extrato da Conta ${result.agencia}-${result.numero_conta}</h3>
                        <div class="result">
                            <strong>Saldo Atual: R$ ${result.saldo.toFixed(2)}</strong><br>
                            Total Depósitos: R$ ${result.total_depositos.toFixed(2)} (${result.numero_depositos})<br>
                            Total Saques: R$ ${result.total_saques.toFixed(2)} (${result.numero_saques})
                        </div>
                        <h4>Transações:</h4>`;
                    
                    if (result.transacoes && result.transacoes.length > 0) {
                        result.transacoes.forEach(transacao => {
                            const emoji = transacao.tipo === 'Depósito' ? '📈' : '📉';
                            html += `<div class="result">
                                <strong>${emoji} ${transacao.tipo}</strong> - R$ ${transacao.valor.toFixed(2)}<br>
                                <small>${transacao.data_hora}</small>
                            </div>`;
                        });
                    } else {
                        html += '<p>Nenhuma transação encontrada.</p>';
                    }
                    
                    document.getElementById('extratoResults').innerHTML = html;
                } else {
                    showAlert('❌ ' + result.mensagem, 'error');
                }
            } catch (error) {
                showAlert('❌ Erro: ' + error.message, 'error');
            }
        }
    </script>
</body>
</html>
"""

# Rotas Flask
@app.route('/')
def index():
    return HTML_INTERFACE

@app.route('/criar_cliente', methods=['POST'])
def api_criar_cliente():
    try:
        data = request.get_json()
        resultado = criar_cliente(
            data['nome'], data['data_nascimento'], data['cpf'],
            data['logradouro'], data['numero'], data['bairro'], data['cidade_uf']
        )
        return jsonify(resultado)
    except Exception as e:
        return jsonify({"sucesso": False, "mensagem": str(e)})

@app.route('/criar_conta', methods=['POST'])
def api_criar_conta():
    try:
        data = request.get_json()
        resultado = criar_conta_bancaria(data['cpf'])
        return jsonify(resultado)
    except Exception as e:
        return jsonify({"sucesso": False, "mensagem": str(e)})

@app.route('/listar_contas')
def api_listar_contas():
    try:
        contas_info = []
        for conta in contas:
            cliente = buscar_cliente_por_cpf(conta['cpf_titular'])
            contas_info.append({
                "agencia": conta['agencia'],
                "numero_conta": conta['numero_conta'],
                "titular": cliente['nome'] if cliente else "Cliente não encontrado",
                "cpf": conta['cpf_titular'],
                "saldo": conta['saldo']
            })
        return jsonify(contas_info)
    except Exception as e:
        return jsonify({"sucesso": False, "mensagem": str(e)})

@app.route('/depositar', methods=['POST'])
def api_depositar():
    try:
        data = request.get_json()
        conta = buscar_conta(data['numero_conta'])
        
        if not conta:
            return jsonify({"sucesso": False, "mensagem": "Conta não encontrada!"})
        
        valor = float(data['valor'])
        novo_saldo, extrato_atualizado = deposito(conta['saldo'], valor, conta['extrato'])
        
        conta['saldo'] = novo_saldo
        conta['extrato'] = extrato_atualizado
        
        return jsonify({
            "sucesso": True,
            "mensagem": f"Depósito de R$ {valor:.2f} realizado com sucesso!",
            "saldo": novo_saldo
        })
    except Exception as e:
        return jsonify({"sucesso": False, "mensagem": str(e)})

@app.route('/sacar', methods=['POST'])
def api_sacar():
    try:
        data = request.get_json()
        conta = buscar_conta(data['numero_conta'])
        
        if not conta:
            return jsonify({"sucesso": False, "mensagem": "Conta não encontrada!"})
        
        valor = float(data['valor'])
        novo_saldo, extrato_atualizado, numero_saques_atualizado = saque(
            saldo=conta['saldo'], valor=valor, extrato=conta['extrato'],
            limite=conta['limite_saque'], numero_saques=conta['numero_saques_hoje'],
            limite_saques=conta['limite_saques_diarios']
        )
        
        conta['saldo'] = novo_saldo
        conta['extrato'] = extrato_atualizado
        conta['numero_saques_hoje'] = numero_saques_atualizado
        
        return jsonify({
            "sucesso": True,
            "mensagem": f"Saque de R$ {valor:.2f} realizado com sucesso!",
            "saldo": novo_saldo
        })
    except Exception as e:
        return jsonify({"sucesso": False, "mensagem": str(e)})

@app.route('/extrato/<int:numero_conta>')
def api_extrato(numero_conta):
    try:
        conta = buscar_conta(numero_conta)
        
        if not conta:
            return jsonify({"sucesso": False, "mensagem": "Conta não encontrada!"})
        
        resultado = exibir_extrato(conta['saldo'], extrato=conta['extrato'])
        resultado['sucesso'] = True
        resultado['numero_conta'] = numero_conta
        resultado['agencia'] = conta['agencia']
        
        return jsonify(resultado)
    except Exception as e:
        return jsonify({"sucesso": False, "mensagem": str(e)})

if __name__ == '__main__':
    print("🏦 Sistema Bancário iniciado!")
    print("📍 Acesse: http://localhost:5000")
    print("=" * 50)
    app.run(host='0.0.0.0', port=5000, debug=True)
    