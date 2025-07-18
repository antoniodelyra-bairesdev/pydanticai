# Configurações para desabilitar SSL
# Isso é necessário para evitar erros de verificação de certificado
#######################################################

import os
import ssl
import urllib.request

import requests
import urllib3
from urllib3.connection import HTTPSConnection

# Definir variáveis de ambiente para desabilitar SSL
os.environ["PYTHONHTTPSVERIFY"] = "0"
os.environ["CURL_CA_BUNDLE"] = ""

# Desabilitar avisos
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Configuração para ignorar verificação de certificado
old_init = HTTPSConnection.__init__


def new_init(self, *args, **kwargs):
    kwargs["ssl_context"] = ssl.create_default_context()
    kwargs["ssl_context"].check_hostname = False
    kwargs["ssl_context"].verify_mode = ssl.CERT_NONE
    old_init(self, *args, **kwargs)


HTTPSConnection.__init__ = new_init

# Configurar requests para não verificar SSL
old_merge_environment_settings = requests.Session.merge_environment_settings


def merge_environment_settings(self, url, proxies, stream, verify, cert):
    settings = old_merge_environment_settings(self, url, proxies, stream, verify, cert)
    settings["verify"] = False
    return settings


requests.Session.merge_environment_settings = merge_environment_settings

# Configurar httpx também (usado pelo Docling)
try:
    import httpx

    # Monkey patch httpx para não verificar SSL
    old_httpx_verify = httpx.Client.__init__

    def new_httpx_init(self, *args, **kwargs):
        kwargs["verify"] = False
        old_httpx_verify(self, *args, **kwargs)

    httpx.Client.__init__ = new_httpx_init
except ImportError:
    pass

# Configurar urllib.request (usado pelo EasyOCR)
try:
    # Monkey patch urllib.request para não verificar SSL
    old_urlopen = urllib.request.urlopen

    def new_urlopen(
        url, data=None, timeout=None, *, cafile=None, capath=None, cadefault=False, context=None
    ):
        if context is None:
            context = ssl.create_default_context()
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE
        return old_urlopen(
            url, data, timeout, cafile=cafile, capath=capath, cadefault=cadefault, context=context
        )

    urllib.request.urlopen = new_urlopen
except Exception:
    pass

#######################################################
