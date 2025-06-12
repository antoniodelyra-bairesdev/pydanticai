from config.swagger import token_field
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from fastapi.responses import Response
from requests_toolbelt import MultipartEncoder
from modules.util.mediatypes import XLSX, TXT, CSV

from .service import PassivoService

router = APIRouter(
    prefix="/enquadramento", tags=["Enquadramento"], dependencies=[token_field]
)


def get_service():
    return PassivoService()


@router.post("/omnis/passivo")
async def omnis_passivo(
    arquivo: UploadFile = File(...), service: PassivoService = Depends(get_service)
):
    valida_arquivo(
        arquivo=arquivo,
        mensagem_erro="Input inválido. O arquivo deve ser um .txt ou .csv",
    )

    (planilha_buffer, avisos_json) = await service.get_omnis_arquivo_passivo(
        arquivo=arquivo
    )

    multipart = MultipartEncoder(
        fields={
            "avisos": avisos_json,
            "arquivo": ("passivo_omnis.xlsx", planilha_buffer, XLSX),
        }
    )

    return Response(
        multipart.to_string(),
        media_type=multipart.content_type,
    )


def valida_arquivo(arquivo: UploadFile, mensagem_erro: str) -> None:
    if arquivo.content_type != TXT and arquivo.content_type != CSV:
        raise HTTPException(status_code=415, detail=mensagem_erro)
