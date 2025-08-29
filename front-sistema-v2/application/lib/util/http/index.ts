export const downloadBlob = (blob: Blob, nome: string) => {
  const a = document.createElement("a");
  const url = URL.createObjectURL(blob);
  a.href = url;
  a.target = "_blank";
  a.rel = "noopener noreferrer";
  a.download = nome;
  a.click();
  URL.revokeObjectURL(url);
};
