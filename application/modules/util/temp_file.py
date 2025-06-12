import aiofiles
import uuid
import os
import logging
import glob

from fastapi.datastructures import UploadFile


class TempFileHelper:
    CAMINHO_PASTA_ARQUIVOS_TEMPORARIOS: str = "files/temp"

    @staticmethod
    async def cria_arqs_temporarios(
        arqs: list[UploadFile], identificador_arqs_temp
    ) -> list[str]:
        nomes_arqs: list[str] = []

        for arq in arqs:
            nome_arq: str = await TempFileHelper.async_cria(
                arq, identificador_arqs_temp
            )
            nomes_arqs.append(nome_arq)

        return nomes_arqs

    @staticmethod
    async def async_cria(file: UploadFile, identificador: str) -> str:
        output_file_name: str = f"{identificador}_{str(uuid.uuid4())}"

        async with aiofiles.open(
            file=f"{TempFileHelper.CAMINHO_PASTA_ARQUIVOS_TEMPORARIOS}/{output_file_name}",
            mode="wb",
        ) as output_stream:
            content = await file.read()
            await output_stream.write(content)

        return output_file_name

    @staticmethod
    def sync_cria(file: bytes, identificador: str) -> str:
        output_file_name: str = f"{identificador}_{str(uuid.uuid4())}"

        with open(
            file=f"{TempFileHelper.CAMINHO_PASTA_ARQUIVOS_TEMPORARIOS}/{output_file_name}",
            mode="wb",
        ) as output_stream:
            content = file
            output_stream.write(content)

        return output_file_name

    @staticmethod
    def get_conteudo_e_deleta(file_name: str) -> bytes:
        file_path: str = (
            f"{TempFileHelper.CAMINHO_PASTA_ARQUIVOS_TEMPORARIOS}/{file_name}"
        )
        with open(
            file=file_path,
            mode="rb",
        ) as file_buffer:
            content = file_buffer.read()

        if os.path.exists(file_path):
            os.remove(file_path)
        else:
            msg: str = TempFileHelper.__get_msg_arquivo_nao_encontrado_delecao(
                file_path=file_path
            )
            logging.warning(msg)

        return content

    @staticmethod
    def deleta_arquivo(file_name: str) -> None:
        file_path: str = (
            f"{TempFileHelper.CAMINHO_PASTA_ARQUIVOS_TEMPORARIOS}/{file_name}"
        )
        if os.path.exists(file_path):
            os.remove(file_path)
        else:
            msg: str = TempFileHelper.__get_msg_arquivo_nao_encontrado_delecao(
                file_path=file_path
            )
            logging.warning(msg)

    @staticmethod
    def deleta_arquivos_temp_relacionados(identificador: str) -> None:
        dir_path: str = TempFileHelper.CAMINHO_PASTA_ARQUIVOS_TEMPORARIOS
        files: list[str] = glob.glob(os.path.join(dir_path, "*"))
        for file in files:
            if (
                os.path.isfile(file)
                and file.startswith(identificador)
                and file != ".gitkeep"
            ):
                os.remove(file)

        return

    @staticmethod
    def __get_msg_arquivo_nao_encontrado_delecao(file_path: str) -> str:
        return f"Arquivo {file_path} não encontrado para deleção"
