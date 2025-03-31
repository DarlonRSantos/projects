from flask import Flask, request, render_template_string
import requests
import os

app = Flask(__name__)

# Configurações
ARQUIVO_MUNICIPIOS = 'municipios.txt'
UF_PADRAO = 'SC'  # Mude para o estado desejado

# Template HTML integrado
HTML = """<!DOCTYPE html>
<html>
<head>
    <title>Consulta IBGE</title>
    <style>
        body{font-family:Arial,sans-serif;margin:40px;max-width:800px;}
        input{padding:8px;width:300px;margin-right:10px;}
        button{padding:8px 15px;cursor:pointer;}
        .result{margin-top:20px;padding:15px;background:#f0f8ff;border-radius:5px;}
        .error{color:red;margin-top:20px;}
        .success{color:green;margin-top:20px;}
        .box{border:1px solid #ddd;padding:20px;border-radius:5px;margin-bottom:20px;}
    </style>
</head>
<body>
    <h1>Consulta de Código IBGE</h1>
    
    <div class="box">
        <h3>Atualizar Dados</h3>
        <form action="/atualizar" method="POST">
            <button type="submit">↻ Atualizar Lista de Municípios</button>
        </form>
    </div>
    
    <div class="box">
        <h3>Consultar Município</h3>
        <form method="POST" action="/">
            <input type="text" name="municipio" placeholder="Ex: Florianópolis" required>
            <button type="submit">🔍 Buscar</button>
        </form>
        {% if resultado %}
        <div class="result">
            <p><strong>Código IBGE:</strong> {{ resultado.codigo }}</p>
            <p><strong>Município:</strong> {{ resultado.nome }}</p>
            <p><strong>UF:</strong> {{ resultado.uf }}</p>
        </div>
        {% endif %}
        {% if mensagem %}
        <div class="{{ 'success' if mensagem.startswith('Lista') else 'error' }}">{{ mensagem }}</div>
        {% endif %}
    </div>
</body>
</html>
"""

def buscar_municipios_ibge():
    """Busca os municípios da API do IBGE e salva no arquivo"""
    try:
        print("Conectando ao IBGE...")
        url = f'https://servicodados.ibge.gov.br/api/v1/localidades/estados/{UF_PADRAO}/municipios'
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        municipios = []
        for municipio in response.json():
            municipios.append(f"{municipio['id']}: {municipio['nome']}")
        
        with open(ARQUIVO_MUNICIPIOS, 'w', encoding='utf-8') as f:
            f.write('\n'.join(municipios))
        
        msg = f"Lista atualizada! {len(municipios)} municípios de {UF_PADRAO} salvos."
        print(msg)
        return True, msg
    except Exception as e:
        msg = f"Erro ao acessar IBGE: {str(e)}"
        print(msg)
        return False, msg

@app.route('/', methods=['GET', 'POST'])
def home():
    resultado = None
    mensagem = None
    
    if request.method == 'POST':
        termo = request.form['municipio'].strip().lower()
        
        if os.path.exists(ARQUIVO_MUNICIPIOS):
            with open(ARQUIVO_MUNICIPIOS, 'r', encoding='utf-8') as f:
                for linha in f:
                    if termo in linha.lower():
                        partes = linha.strip().split(':')
                        resultado = {
                            'codigo': partes[0].strip(),
                            'nome': partes[1].strip(),
                            'uf': UF_PADRAO
                        }
                        break
            if not resultado:
                mensagem = f"Nenhum município encontrado com '{termo.capitalize()}'"
        else:
            mensagem = "Arquivo não encontrado. Atualize a lista primeiro."
    
    return render_template_string(HTML, resultado=resultado, mensagem=mensagem)

@app.route('/atualizar', methods=['POST'])
def atualizar():
    sucesso, mensagem = buscar_municipios_ibge()
    return render_template_string(HTML, resultado=None, mensagem=mensagem)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)  # Adicione esta linha
    if not os.path.exists(ARQUIVO_MUNICIPIOS):
        buscar_municipios_ibge()
    app.run(debug=True)