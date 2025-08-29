export default function getFileName(fileList: FileList | null): string {
  if (fileList) {
    return fileList[0].name;
  }

  return "";
}
