# Bibliotecas necessárias
from langchain_ollama import ChatOllama
from typing import Literal
from pydantic import BaseModel, Field
from langchain.agents import create_agent
from langchain_core.messages import ToolMessage
# Arquivos necessários
import settings
import prompts
import tools

# Formatando e-mail para análise do agente para casos de teste em ambiente real
def formatar_email(subject, body):
    return f'<email>\nAssunto: {subject}\n\n{body[:6000]}\n</email>'

# Instanciando LLM e configurando parametros
llm = ChatOllama(model = settings.MODELO, temperature = 0, num_ctx = 8192, 
                 num_predict = settings.NUM_TOKENS, client_kwargs = settings.MAX_TEMPO)

# Definição do formato de resposta
class Veredito(BaseModel):
    indicadores: list[str] = Field(description='Sinais concretos encontrados no e-mail; lista vazia se não houver')
    justificativa: str = Field(description='Raciocínio curto, em português, antes da decisão')
    classificacao: Literal['legitimo', 'spam', 'phishing']

classificador = llm.with_structured_output(Veredito)

# Função para realizar classificação de e-mails apenas com LLM puro
def classificar(subject: str, body: str) -> Veredito:
    # Realizando decisão estruturada
    return classificador.invoke([
        ('system', prompts.SISTEMA),
        ('user', f'<email>\nAssunto: {subject}\n\n{body[:6000]}\n</email>'),
    ])

# Função para realizar classificação de e-mails com LLM em conjunto com score de risco
def classificar_com_ferramentas(subject: str, body: str):
    # Instanciando ferramenta
    ferramenta = tools.criar_ferramenta_score(subject, body)

    # Formatando entrada para casos de teste em ambiente real
    entrada_formatada = formatar_email(subject, body)

    # Investigação, o agente chama a ferramenta e chega em uma conclusão
    agente = create_agent(model=llm, tools=[ferramenta],
                          system_prompt=prompts.SISTEMA + prompts.INSTRUCAO_FERRAMENTA)
    # Executa o ciclo do agente (LLM -> ferramenta -> LLM) até o LLM responder sem pedir ferramenta
    resultado = agente.invoke({'messages': [('user', entrada_formatada)]},
                              config={'recursion_limit': settings.MAX_PASSOS})
    # Histórico completo
    mensagens = resultado['messages']
    # Guardando apenas as respostas da ferramenta de score
    saidas = [m.content for m in mensagens
              if isinstance(m, ToolMessage) and m.name == ferramenta.name]
    # Última mensagem do histórico (conclusão escrita pelo LLM após ver o score)
    conclusao = mensagens[-1].content

    # Realizando a decisão estruturada
    veredito = classificador.invoke([
        ('system', prompts.SISTEMA),
        ('user', entrada_formatada
                 + f'\n\nResultado da ferramenta: {saidas[0] if saidas else "não consultada"}'
                 + f'\n\nConclusão da investigação: {conclusao}'
                 + '\n\nDê o veredito final, coerente com as evidências acima.'),
    ])
    return veredito, len(saidas)