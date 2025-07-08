import sqlite3
import os
from flask import Flask, render_template, request, jsonify
from datetime import datetime

app = Flask(__name__)

# Configuração do banco de dados
DATABASE = 'data/agenda_profissionais.db'




# Valores por convênio baseados no script original
VALORES_CONVENIO = {
    "HAPVIDA": {"vprofissional": 20.0, "vempresa": 30.0},
    "Notredame": {"vprofissional": 20.0, "vempresa": 30.0},
    "Confiança": {"vprofissional": 12.0, "vempresa": 12.0},
    "Medgold": {"vprofissional": 12.5, "vempresa": 12.5},
    "You Saúde": {"vprofissional": 15.0, "vempresa": 20.0},
    "Atende Saúde": {"vprofissional": 10.0, "vempresa": 15.0}
}

def get_tables():
    """Retorna lista de todas as tabelas (profissionais)"""
    if not os.path.exists(DATABASE):
        return []
    
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'agenda_%'")
    tables = [row[0] for row in cursor.fetchall()]
    conn.close()
    return tables

def extract_professional_name(table_name):
    return table_name.replace("agenda_", "").replace("_", " ").title()

def parse_data_brasileira(data_str):
    """Converte 'DD/MM/YY' ou 'DD/MM/YYYY' para datetime"""
    try:
        return datetime.strptime(data_str, "%d/%m/%Y")
    except ValueError:
        return datetime.strptime(data_str, "%d/%m/%y")

def get_report_data(table_name, data_inicio=None, data_fim=None):
    """Gera dados do relatório de um profissional, com filtro opcional por data"""
    if not os.path.exists(DATABASE):
        return None
    
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    query = f'''
        SELECT convenio, COUNT(*) as quantidade, data
        FROM {table_name}
        WHERE presenca = 'Ok'
        GROUP BY convenio, data
        ORDER BY convenio
    '''
    
    try:
        cursor.execute(query)
        dados = cursor.fetchall()

        # Preparar filtros de data
        if data_inicio and data_fim:
            data_inicio = datetime.strptime(data_inicio, "%Y-%m-%d").date()
            data_fim = datetime.strptime(data_fim, "%Y-%m-%d").date()

            dados = [
                (convenio, quantidade, data_str)
                for convenio, quantidade, data_str in dados
                if parse_data_brasileira(data_str).date() >= data_inicio and
                   parse_data_brasileira(data_str).date() <= data_fim
            ]

        # Buscar nome do profissional
        cursor.execute(f'SELECT DISTINCT profissional FROM {table_name} LIMIT 1')
        profissional_result = cursor.fetchone()
        profissional = profissional_result[0] if profissional_result else extract_professional_name(table_name)

        # Buscar especialidade
        cursor.execute(f'SELECT DISTINCT especialidade FROM {table_name} LIMIT 1')
        especialidade_result = cursor.fetchone()
        especialidade = especialidade_result[0] if especialidade_result else "Não informado"
        
        conn.close()

        # Montar relatório
        relatorio_convenios = {}
        total_atendimentos = 0
        total_profissional = 0
        total_empresa = 0

        for convenio, quantidade, _ in dados:
            if convenio is None:
                convenio = "Desconhecido"
            
            valores = VALORES_CONVENIO.get(convenio, {"vprofissional": 15.0, "vempresa": 20.0})
            vprofissional = valores["vprofissional"]
            vempresa = valores["vempresa"]

            total_prof_convenio = vprofissional * quantidade
            total_emp_convenio = vempresa * quantidade

            if convenio not in relatorio_convenios:
                relatorio_convenios[convenio] = {
                    'quantidade': 0,
                    'valor_unitario_prof': vprofissional,
                    'valor_unitario_emp': vempresa,
                    'total_profissional': 0,
                    'total_empresa': 0
                }

            relatorio_convenios[convenio]["quantidade"] += quantidade
            relatorio_convenios[convenio]["total_profissional"] += total_prof_convenio
            relatorio_convenios[convenio]["total_empresa"] += total_emp_convenio

            total_atendimentos += quantidade
            total_profissional += total_prof_convenio
            total_empresa += total_emp_convenio

        return {
            'tabela': table_name,
            'profissional': profissional,
            'especialidade': especialidade,
            'total_atendimentos': total_atendimentos,
            'total_profissional': total_profissional,
            'total_empresa': total_empresa,
            'convenios': relatorio_convenios
        }

    except sqlite3.Error as e:
        print(f"Erro ao acessar dados: {e}")
        conn.close()
        return None

def get_all_reports(data_inicio=None, data_fim=None):
    """Gera relatório consolidado de todos os profissionais"""
    tabelas = get_tables()
    todos_relatorios = []
    
    totais_gerais = {
        'total_atendimentos': 0,
        'total_profissional': 0,
        'total_empresa': 0,
        'convenios': {}
    }
    
    for tabela in tabelas:
        relatorio = get_report_data(tabela, data_inicio, data_fim)
        if relatorio:
            todos_relatorios.append(relatorio)
            
            # Somar aos totais gerais
            totais_gerais['total_atendimentos'] += relatorio['total_atendimentos']
            totais_gerais['total_profissional'] += relatorio['total_profissional']
            totais_gerais['total_empresa'] += relatorio['total_empresa']
            
            # Consolidar por convênio
            for convenio, dados in relatorio['convenios'].items():
                if convenio not in totais_gerais['convenios']:
                    totais_gerais['convenios'][convenio] = {
                        'quantidade': 0,
                        'total_profissional': 0,
                        'total_empresa': 0
                    }
                
                totais_gerais['convenios'][convenio]['quantidade'] += dados['quantidade']
                totais_gerais['convenios'][convenio]['total_profissional'] += dados['total_profissional']
                totais_gerais['convenios'][convenio]['total_empresa'] += dados['total_empresa']
    
    return todos_relatorios, totais_gerais

@app.route('/')
def index():
    """Página inicial com lista de profissionais"""
    tabelas = get_tables()
    profissionais = []
    
    for tabela in tabelas:
        relatorio = get_report_data(tabela)
        if relatorio:
            profissionais.append({
                'tabela': tabela,
                'nome': relatorio['profissional'],
                'especialidade': relatorio['especialidade'],
                'total_atendimentos': relatorio['total_atendimentos']
            })
    
    return render_template('index.html', profissionais=profissionais)

# Filtro personalizado para formatar a data
@app.template_filter('format_date')
def format_date(value, format="%d/%m/%Y"):
    """Filtro para formatar as datas"""
    if value is None:
        return ''
    try:
        # Corrigido para o formato correto da data
        return datetime.strptime(value, "%Y-%m-%d").strftime(format)
    except ValueError:
        return value  # Caso o valor não seja uma data válida


@app.route('/relatorio/<tabela>')
def relatorio_profissional(tabela):
    """Relatório individual de um profissional"""
    if tabela not in get_tables():
        return "Profissional não encontrado", 404
    
    data_inicio = request.args.get('data_inicio')
    data_fim = request.args.get('data_fim')

    relatorio = get_report_data(tabela, data_inicio, data_fim)
    if not relatorio:
        return "Erro ao gerar relatório", 500

    return render_template('relatorio.html', relatorio=relatorio, data_inicio=data_inicio, data_fim=data_fim)


@app.route('/relatorio/todos')
def relatorio_todos():
    """Relatório consolidado de todos os profissionais"""
    data_inicio = request.args.get('data_inicio')
    data_fim = request.args.get('data_fim')

    todos_relatorios, totais_gerais = get_all_reports(data_inicio, data_fim)
    return render_template('relatorio_todos.html', 
                          relatorios=todos_relatorios, 
                          totais=totais_gerais, 
                          data_inicio=data_inicio, 
                          data_fim=data_fim)


@app.route('/api/relatorio/<tabela>')
def api_relatorio(tabela):
    """API para obter dados do relatório em JSON"""
    if tabela not in get_tables():
        return jsonify({'error': 'Profissional não encontrado'}), 404
    
    data_inicio = request.args.get('data_inicio')
    data_fim = request.args.get('data_fim')

    # Formatar as datas para o formato DD/MM/YYYY
    if data_inicio:
        data_inicio_formatada = datetime.strptime(data_inicio, "%d-%m-%y").strftime("%d/%m/%Y")
    else:
        data_inicio_formatada = None

    if data_fim:
        data_fim_formatada = datetime.strptime(data_fim, "%d-%m-%y").strftime("%d/%m/%Y")
    else:
        data_fim_formatada = None

    relatorio = get_report_data(tabela, data_inicio, data_fim)
    if not relatorio:
        return jsonify({'error': 'Erro ao gerar relatório'}), 500
    
    # Retornar as datas formatadas no JSON
    return jsonify({
        'relatorio': relatorio,
        'data_inicio': data_inicio_formatada,
        'data_fim': data_fim_formatada
    })


@app.route('/api/convenios')
def api_convenios():
    """API para obter valores dos convênios"""
    return jsonify(VALORES_CONVENIO)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
