import sys, csv, time, argparse
from pathlib import Path
import pandas as pd

RAIZ = Path(__file__).resolve().parent.parent
sys.path.append(str(RAIZ / 'src'))
import agent, ml_model

parser = argparse.ArgumentParser()
parser.add_argument('modo', choices=['llm', 'agente', 'hibrido'])
parser.add_argument('--n', type=int, default=100, help='amostras por classe')
args = parser.parse_args()

saida = RAIZ / 'reports' / f'classification-email-{args.modo}-n{args.n}.csv'
campos = ['id', 'real', 'previsto', 'segundos', 'n_chamadas', 'score_ml', 'caminho']

# Lê só as colunas necessárias, para usar menos memória
df = pd.read_csv(RAIZ / 'data' / 'processed' / 'phishing-dataset-merged.csv',
                 usecols=['subject', 'body', 'tipo'], keep_default_na=False)
ids_teste = pd.read_csv(RAIZ / 'data' / 'processed' / 'test_ids.csv')['id']
amostra = df.loc[ids_teste].groupby('tipo').sample(args.n, random_state=2026)
del df

# Retoma de onde parou, se o arquivo já existir
feitos = set(pd.read_csv(saida)['id']) if saida.exists() else set()
conta_emails = 0

with open(saida, 'a', newline='', encoding='utf-8') as f:
    w = csv.DictWriter(f, fieldnames=campos)
    if f.tell() == 0:
        w.writeheader()
    for k, (i, linha) in enumerate(amostra.iterrows(), 1):
        conta_emails += 1
        if i in feitos:
            continue
        inicio = time.time()
        n = 0
        caminho = args.modo
        score = None
        try:
            if args.modo == 'llm':
                previsto = agent.classificar(linha['subject'], linha['body']).classificacao
            elif args.modo == 'agente':
                v, n = agent.classificar_com_ferramentas(linha['subject'], linha['body'])
                previsto = v.classificacao
            elif args.modo == 'hibrido': # hibrido
                previsto, caminho, score = agent.classificar_hibrido(linha['subject'], linha['body'])
        except Exception as e:
            previsto = 'erro'
        segundos = round(time.time() - inicio, 1)

        if score is None:   # só os modos llm/agente (ou erro) precisam do score
            score = ml_model.pontuar(linha['subject'], linha['body'])

        w.writerow({'id': i, 'real': linha['tipo'], 'previsto': previsto,
                'segundos': segundos, 'n_chamadas': n,
                'score_ml': round(score, 4), 'caminho': caminho})
        
        f.flush()
        if k % 25 == 0:
            print(f'{k}/{len(amostra)}', flush=True)