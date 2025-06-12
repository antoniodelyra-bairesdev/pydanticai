from datetime import datetime
from pydantic import BaseModel as Schema


class DadosEmailSchema(Schema):
    para: list[str]
    assunto: str
    conteudo: str
    copia: list[str] = []
    copia_oculta: list[str] = []


class EmailTemplateSchema(Schema):
    titulo: str
    conteudo_html: str

    def html(self):
        agora = datetime.now()
        return f"""
<!DOCTYPE html>
<html lang="pt-br">
    <head>
        <meta http-equiv="Content-Type" content="text/html; charset=iso-8859-1">
    </head>
    <body>
        <div style="display: flex; flex-direction: column; align-items: stretch; min-height: 1080px; background-color: #F6F7F8; font-family: sans-serif;">
            <div style="position: relative; height: 64px; background-color: #1B3157; display: flex; flex-direction: row; justify-content: flex-end;">
                <div style="position: absolute; left: 0; top: 0; display: flex; flex-direction: column; align-items: center;">
                    <img height="64" src="{logo_b64}">
                </div>
                <div style="width: 25%; margin-right: -64px; background-color: #0D6696; clip-path: polygon(64px 0, 100% 0, 100% 100%, 0 100%);">
                </div>
                <div style="width: 25%; margin-right: -64px; background-color: #2E96BF; clip-path: polygon(64px 0, 100% 0, 100% 100%, 0 100%);">
                </div>
                <div style="width: calc(25% - 64px); background-color: #00BADB; clip-path: polygon(64px 0, 100% 0, 100% 100%, 0 100%);">
                </div>
            </div>
            <div style="display: flex; flex-direction: column; justify-content: space-between; background-color: white; flex: 1; margin: 24px; padding: 0 32px">
                <div style="padding: 24px 0 0 0; color: black">
                    <h2 style="font-size: 20px; text-align: justify">{self.titulo}</h2>
                    <hr style="border: 1px solid #F6F7F8">
                    {self.conteudo_html}
                </div>
                <hr style="border: 1px solid #F6F7F8">
                <div style="font-size: 12px; margin-bottom: 24px; color: #A6A7A8">
                    <p>Enviado às {agora.strftime("%H:%M:%S - %d/%m/%Y")}</p>
                </div>
            </div>
        </div>
    </body>
</html>
"""


logo_b64 = ""
with open("public/logob64.txt") as arquivo:
    logo_b64 = arquivo.read()
