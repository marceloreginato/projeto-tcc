# Bibliotecas necessárias
from pathlib import Path

# Definição de caminhos
RAIZ = Path(__file__).resolve().parent.parent
CAMINHO_MODELO_ML = RAIZ / 'model' / 'risk_model.joblib'
CAMINHO_IDS_TESTE = RAIZ / 'data' / 'processed' / 'test_ids.csv'

# Modelo utilizado
MODELO = 'llama3.2:3b'

# Número máximo de tokens para cada resposta
NUM_TOKENS = 1024

# Número máximo de segundos para cada resposta
MAX_TEMPO = {'timeout': 300}

# Número máximo de iterações do agente
MAX_PASSOS = 10