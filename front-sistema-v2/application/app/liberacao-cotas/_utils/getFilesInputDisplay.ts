export default function getFilesInputDisplay(files: FileList | null): string {
  if (files !== null) {
    const numeroArquivosSelecionados: number = files.length;
    return `${numeroArquivosSelecionados} arquivo(s) selecionado(s)`;
  }

  return "";
}
