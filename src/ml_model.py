import re
import pandas as pd
import numpy as np
import settings
from functools import lru_cache
import joblib

PADRAO_URL = re.compile(r'(?:https?\s*:\s*/\s*/|www\s*\.)', re.IGNORECASE)
PADRAO_MIME = r'content-type:\s*\S+(?:;\s*\S+)*|content-transfer-encoding:\s*\S+|mime-version:?\s*\S*|------=_\S*|boundary=\S*'
LIMITE_CARACTERES = 20000

# Normalização para uso com e-mails reais
def normalizar(serie):
    return serie.fillna('').str.replace(r'\s+', ' ', regex=True).str.strip().str.lower()

# Preparando entrada para conseguir rodar em e-mails reais e também testar na base de dados
def preparar_entrada(df):
    subject = normalizar(df['subject'])
    body = normalizar(df['body'])
    body_limpo = body.str.replace(PADRAO_MIME, '', regex=True).str.slice(0, LIMITE_CARACTERES)
    return pd.DataFrame({
        'texto': subject + ' ' + body_limpo,
        'log_num_urls': np.log1p(body.str.count(PADRAO_URL)),
        'log_num_palavras': np.log1p(body.str.split().str.len()),
    }, index = df.index)

# Carrega arquivo apenas uma vez
@lru_cache(maxsize=1)
def carregar_modelo():
    return joblib.load(settings.CAMINHO_MODELO_ML)

# Função para realizar a pontuação de e-mails novos a partir do modelo salvo
def pontuar(subject, body):
    modelo = carregar_modelo()
    X = preparar_entrada(pd.DataFrame([{'subject': subject, 'body': body}]))
    probabilidade = modelo.predict_proba(X)[0, 1]

    return {'probabilidade': float(probabilidade)}