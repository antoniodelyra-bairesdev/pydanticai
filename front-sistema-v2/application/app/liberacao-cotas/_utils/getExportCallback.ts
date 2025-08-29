import { CampoRequestLiberacaoCotas } from "@/lib/types/api/iv/liberacao-cotas";
import { downloadBlob } from "@/lib/util/http";
import { Dispatch, SetStateAction } from "react";

import IVBrowserHTTPClient from "@/lib/util/http/vanguarda/IVBrowserHTTPClient";
import isObjEmpty from "@/lib/util/object";

export default async function getExportCallback({
  httpClient,
  url,
  isExportLoading,
  setIsExportLoading,
  requestBodyFieldsInputs,
  setAvisos,
  setErroMensagem,
  nomeArquivoExportado,
}: {
  httpClient: IVBrowserHTTPClient;
  url: string;
  isExportLoading: boolean;
  setIsExportLoading: Dispatch<SetStateAction<boolean>>;
  requestBodyFieldsInputs: {
    field: CampoRequestLiberacaoCotas;
    fileList: FileList | null;
  }[];
  setAvisos: Dispatch<SetStateAction<any>>;
  setErroMensagem: Dispatch<SetStateAction<string | null>>;
  nomeArquivoExportado?: string;
}): Promise<void> {
  if (isExportLoading) {
    return;
  }

  setAvisos(null);
  setErroMensagem(null);

  setIsExportLoading(true);

  const body = new FormData();
  for (const { field, fileList } of requestBodyFieldsInputs) {
    if (!fileList) {
      setIsExportLoading(false);
      return;
    }

    for (let i = 0; i < fileList.length; ++i) {
      const file: File = fileList[i];
      body.append(field, file);
    }
  }

  const response = await httpClient.fetch(url, {
    method: "POST",
    body: body,
    multipart: true,
    hideToast: {
      clientError: true,
      serverError: true,
    },
  });

  if (!response.ok) {
    const responseJSON = (await response.json()) as
      | {
          detail: { request_id: string; message: string };
        }
      | {
          detail: string;
        };

    if (typeof responseJSON.detail == "string") {
      setErroMensagem(responseJSON.detail);
      setIsExportLoading(false);
      return;
    }

    const errorId = (
      responseJSON as { detail: { request_id: string; message: string } }
    ).detail.request_id;
    const message = (
      responseJSON as { detail: { request_id: string; message: string } }
    ).detail.message;

    setErroMensagem(message + " Código do erro: " + errorId);
    setIsExportLoading(false);
    return;
  }

  const responseFormData = await response.formData();
  const responseAvisosJSON = JSON.parse(
    responseFormData.get("avisos") as string,
  );

  if (!isObjEmpty(responseAvisosJSON)) {
    setAvisos(responseAvisosJSON);
  }

  const nomeArquivo = (responseFormData.get("arquivo") as File).name;
  const blob = responseFormData.get("arquivo") as Blob;
  downloadBlob(blob, nomeArquivoExportado ?? nomeArquivo);

  setIsExportLoading(false);
}
