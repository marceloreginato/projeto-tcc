# Bibliotecas necessárias
from langchain_ollama import ChatOllama
from typing import Literal
from pydantic import BaseModel, Field
import settings
import prompts

# Instanciando LLM e configurano parametros
llm = ChatOllama(model = settings.MODELO, temperature = 0, num_ctx = 8192, 
                 num_predict = settings.NUM_TOKENS, client_kwargs = settings.TEMPO_MAX)

# CLASSIFICADOR LLM SEM FERRAMENTAS

class Veredito(BaseModel):
    indicadores: list[str] = Field(description='Sinais concretos encontrados no e-mail; lista vazia se não houver')
    justificativa: str = Field(description='Raciocínio curto, em português, antes da decisão')
    classificacao: Literal['legitimo', 'spam', 'phishing']

classificador = llm.with_structured_output(Veredito)

def classificar(subject: str, body: str) -> Veredito:
    return classificador.invoke([
        ('system', prompts.SISTEMA),
        ('user', f'<email>\nAssunto: {subject}\n\n{body[:6000]}\n</email>'),
    ])