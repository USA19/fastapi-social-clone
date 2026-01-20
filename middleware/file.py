from fastapi import UploadFile, HTTPException, status
from typing import Optional

ALLOWED_MIME_TYPES = {
    "image/jpeg",
    "image/png",
}

MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB


async def validateUpload(file: Optional[UploadFile] = None):
    if not file:
        return None  # file is optional

    # 1️⃣ Check mime type
    if file.content_type not in ALLOWED_MIME_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file type. Only JPG and PNG are allowed.",
        )

    # 2️⃣ Check file size
    contents = await file.read()
    size = len(contents)

    if size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File size exceeds 5MB limit.",
        )

    # Reset file pointer for later use
    await file.seek(0)

    return file
