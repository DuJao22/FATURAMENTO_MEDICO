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
    """Extrai o nome do profissional da tabela"""
    # Remove 'agenda_' do início
    name = table_name.replace('agenda_', '')
    # Substitui underscores por espaços e capitaliza
    name = name.replace('_', ' ').title()
    return name

def get_report_data(table_name, data_inicio=None, data_fim=None):
    """Gera dados do relatório para um profissional específico"""
    if not os.path.exists(DATABASE):
        return None
    
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    # Query base para buscar apenas atendimentos com presença "Ok"
    query = f'''
        SELECT convenio, COUNT(*) as quantidade, data
        FROM {table_name}
        WHERE presenca = 'Ok'
    '''
    
    params = []
    if data_inicio and data_fim:
        query += ' AND data BETWEEN ? AND ?'
        params.extend([data_inicio, data_fim])
    
    query += ' GROUP BY convenio ORDER BY convenio'
    
    try:
        cursor.execute(query, params)
        dados = cursor.fetchall()
        
        # Buscar informações do profissional
        cursor.execute(f'SELECT DISTINCT profissional FROM {table_name} LIMIT 1')
        profissional_result = cursor.fetchone()
        profissional = profissional_result[0] if profissional_result else extract_professional_name(table_name)
        
        # Buscar especialidade
        cursor.execute(f'SELECT DISTINCT especialidade FROM {table_name} LIMIT 1')
        especialidade_result = cursor.fetchone()
        especialidade = especialidade_result[0] if especialidade_result else "Não informado"
        
        conn.close()
        
        # Organizar dados por convênio
        relatorio_convenios = {}
        total_atendimentos = 0
        total_profissional = 0
        total_empresa = 0
        
        for convenio, quantidade, _ in dados:
            if convenio is None:
                convenio = "Desconhecido"  # Substituir None por "Desconhecido"
            
            if convenio in VALORES_CONVENIO:
                vprofissional = VALORES_CONVENIO[convenio]["vprofissional"]
                vempresa = VALORES_CONVENIO[convenio]["vempresa"]
            else:
                # Valores padrão para convênios não mapeados
                vprofissional = 15.0
                vempresa = 20.0
            
            total_prof_convenio = vprofissional * quantidade
            total_emp_convenio = vempresa * quantidade
            
            relatorio_convenios[convenio] = {
                'quantidade': quantidade,
                'valor_unitario_prof': vprofissional,
                'valor_unitario_emp': vempresa,
                'total_profissional': total_prof_convenio,
                'total_empresa': total_emp_convenio
            }
            
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

    
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    # Query base para buscar apenas atendimentos com presença "Ok"
    query = f'''
        SELECT convenio, COUNT(*) as quantidade, data
        FROM {table_name}
        WHERE presenca = 'Ok'
    '''
    
    params = []
    if data_inicio and data_fim:
        query += ' AND data BETWEEN ? AND ?'
        params.extend([data_inicio, data_fim])
    
    query += ' GROUP BY convenio ORDER BY convenio'
    
    try:
        cursor.execute(query, params)
        dados = cursor.fetchall()
        
        # Buscar informações do profissional
        cursor.execute(f'SELECT DISTINCT profissional FROM {table_name} LIMIT 1')
        profissional_result = cursor.fetchone()
        profissional = profissional_result[0] if profissional_result else extract_professional_name(table_name)
        
        # Buscar especialidade
        cursor.execute(f'SELECT DISTINCT especialidade FROM {table_name} LIMIT 1')
        especialidade_result = cursor.fetchone()
        especialidade = especialidade_result[0] if especialidade_result else "Não informado"
        
        conn.close()
        
        # Organizar dados por convênio
        relatorio_convenios = {}
        total_atendimentos = 0
        total_profissional = 0
        total_empresa = 0
        
        for convenio, quantidade, _ in dados:
            if convenio in VALORES_CONVENIO:
                vprofissional = VALORES_CONVENIO[convenio]["vprofissional"]
                vempresa = VALORES_CONVENIO[convenio]["vempresa"]
            else:
                # Valores padrão para convênios não mapeados
                vprofissional = 15.0
                vempresa = 20.0
            
            total_prof_convenio = vprofissional * quantidade
            total_emp_convenio = vempresa * quantidade
            
            relatorio_convenios[convenio] = {
                'quantidade': quantidade,
                'valor_unitario_prof': vprofissional,
                'valor_unitario_emp': vempresa,
                'total_profissional': total_prof_convenio,
                'total_empresa': total_emp_convenio
            }
            
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
    
    return render_template('relatorio.html', relatorio=relatorio)

@app.route('/relatorio/todos')
def relatorio_todos():
    """Relatório consolidado de todos os profissionais"""
    data_inicio = request.args.get('data_inicio')
    data_fim = request.args.get('data_fim')
    
    todos_relatorios, totais_gerais = get_all_reports(data_inicio, data_fim)
    return render_template('relatorio_todos.html', 
                         relatorios=todos_relatorios, 
                         totais=totais_gerais)

@app.route('/api/relatorio/<tabela>')
def api_relatorio(tabela):
    """API para obter dados do relatório em JSON"""
    if tabela not in get_tables():
        return jsonify({'error': 'Profissional não encontrado'}), 404
    
    data_inicio = request.args.get('data_inicio')
    data_fim = request.args.get('data_fim')
    
    relatorio = get_report_data(tabela, data_inicio, data_fim)
    if not relatorio:
        return jsonify({'error': 'Erro ao gerar relatório'}), 500
    
    return jsonify(relatorio)

@app.route('/api/convenios')
def api_convenios():
    """API para obter valores dos convênios"""
    return jsonify(VALORES_CONVENIO)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
