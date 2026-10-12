# Bibliotecas necessárias 
from langchain.tools import tool
# Arquivos necessários
import ml_model

# Definição ferramenta para verificar o score proveniente do modelo de AM
def criar_ferramenta_score(subject, body):
    @tool
    # Chama a função pontuar e retorna a probabilidade
    def consultar_score_ml() -> str:
        '''Consulta um classificador de ML treinado com milhares de e-mails rotulados.
        Retorna a probabilidade de o e-mail ser malicioso (spam ou phishing). Não recebe argumentos.'''
        p = ml_model.pontuar(subject, body)
        return (f'Probabilidade de ser malicioso segundo o classificador de ML: {p:.2f}. '
                'O classificador distingue apenas malicioso x legítimo, não distingue spam de phishing')
    return consultar_score_ml