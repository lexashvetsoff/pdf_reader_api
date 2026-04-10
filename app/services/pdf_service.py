import tempfile
import os
from fastapi import UploadFile


async def save_upload_file_to_temp(upload_file: UploadFile) -> str:
    suffix = ".pdf"
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        content = await upload_file.read()
        tmp.write(content)
        return tmp.name


def delete_temp_file(file_path: str) -> None:
    try:
        os.unlink(file_path)
    except OSError:
        pass
