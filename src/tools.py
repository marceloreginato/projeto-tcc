# Bibliotecas necessárias
import re
import ipaddress
from urllib.parse import urlparse

# DEFINIÇÃO DE CONSTANTES

# Número máximo de URLs analisadas por e-mail (evitar e-mails com centenas de URLs)
MAX_URLS = 10

# Definindo padrão da URL
PADRAO_URL = re.compile(r'(?:https?://|www\.)[^\s<>"\'()\[\]]+')

# Definindo alguns tlds genéricos
TLDS_GENERICOS = {'com', 'net', 'org', 'edu', 'gov', 'mil', 'int', 'info', 'biz', 'name', 'pro',
                 'xyz', 'top', 'click', 'work', 'online', 'site', 'website', 'club', 'shop', 'app', 'io'}

# Listas de sinais suspeitos (citar fonte na monografia (Spamhaus))
TLDS_SUSPEITOS = {'tk', 'ml', 'ga', 'cf', 'gq', 'pw', 'xyz', 'top', 'click', 'work'}

ENCURTADORES = {'bit.ly', 'tinyurl.com', 'goo.gl', 't.co', 'ow.ly', 'is.gd', 'buff.ly', 'cutt.ly', 'rebrand.ly'}

HOSPEDAGEM_GRATUITA = ('godaddysites.com', 'my-free.website', '000webhostapp.com', 'weebly.com',
                       'wixsite.com', 'firebaseapp.com', 'web.app', 'blogspot.com', 'sites.google.com')

# Definindo algumas palavras sesíveis comumente utilizadas em e-mails de phishing
PALAVRAS_SENSIVEIS = ('login', 'signin', 'verify', 'account', 'password', 'secure', 'update', 'confirm', 'banking')

# Normalizando as URLs
def normalizar(texto):
    texto = re.sub(r'(https?)\s*:\s*/\s*/\s*', r'\1://', texto)
    texto = re.sub(r'(?<=[a-z0-9])\s+([./\-?=&_])\s+(?=[a-z0-9])', r'\1', texto)
    return texto

def extrair_urls(texto):
    urls = [u.rstrip('.,;:!?') for u in PADRAO_URL.findall(texto)]
    return list(dict.fromkeys(urls))


def eh_ip(dominio):
    try:
        ipaddress.ip_address(dominio)
        return True
    except ValueError:
        return False

def tld_valido(parte):
    return parte in TLDS_GENERICOS or (len(parte) == 2 and parte.isalpha())

def extrair_dominio(url):
    if url.startswith('www.'):
        url = 'http://' + url
    try:
        dominio = urlparse(url).hostname
    except ValueError:
        return None
    if not dominio:
        return None
    if eh_ip(dominio):
        return dominio
    # Heurística para Enron
    partes = dominio.split('.')
    while len(partes) > 2 and not tld_valido(partes[-1]):
        partes.pop()
    return '.'.join(partes)

def sinais(url, dominio):
    encontrados = []
    if eh_ip(dominio):
        encontrados.append('ip_no_lugar_de_dominio')
    if '@' in urlparse(url if '://' in url else 'https://' + url).netloc:
        encontrados.append('arroba_na_url')
    if 'xn--' in dominio:
        encontrados.append('punycode')
    if dominio in ENCURTADORES:
        encontrados.append('encurtador')
    if dominio.rsplit('.', 1)[-1] in TLDS_SUSPEITOS:
        encontrados.append('tld_suspeito')
    if dominio.count('.') >=4:
        encontrados.append('muitos_subdominios')
    if any(p in url.lower() for p in PALAVRAS_SENSIVEIS):
        encontrados.append('palavras_sensiveis')
    if dominio.endswith(HOSPEDAGEM_GRATUITA):
        encontrados.append('hospedagem_gratuita')
    return encontrados
    

# Função para analisar URLs dos e-mails
def analisar_urls(texto: str)-> dict:
    urls = extrair_urls(normalizar(texto))
    analises = []
    for url in urls[:MAX_URLS]:
        dominio = extrair_dominio(url)
        if dominio is None:
            continue
        analises.append({'dominio': dominio, 'sinais': sinais(url, dominio)})
    return{
        'total_urls': len(urls),
        'urls_suspeitas': sum(1 for a in analises if a['sinais']),
        'analises': analises,
    }
