from io import BytesIO

TXT = "text/plain"
PDF = "application/pdf"
XLSX = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
CSV = "text/csv"
ZIP = "application/x-zip-compressed"


def stream(file: BytesIO, block_size=4 * 1024 * 1024):
    while True:
        data = file.read(block_size)
        if data != b"":
            yield data
        else:
            break
