from pathlib import Path

from fastapi import APIRouter, File, Header, HTTPException, Request, UploadFile
from fastapi.responses import FileResponse, JSONResponse, StreamingResponse

router = APIRouter()
UPLOAD_DIRECTORY = Path("uploads")
UPLOAD_DIRECTORY.mkdir(exist_ok=True)
allowed_content_types = ["application/pdf", "image/jpeg", "image/png", "video/mp4"]
content_type_to_folder = {
    "application/pdf": "pdfs",
    "image/jpeg": "images",
    "image/png": "images",
    "video/mp4": "videos",
}

EXTENSION_TO_TYPE = {
    ".pdf": "pdfs",
    ".jpeg": "images",
    ".jpg": "images",
    ".png": "images",
    ".mp4": "videos",
    # Add more extensions as needed
}


@router.post("/upload")
async def document_upload(request: Request, file: UploadFile = File(...)):
    if file.content_type not in allowed_content_types:
        raise HTTPException(
            status_code=400, detail=f"File type {file.content_type} is not allowed"
        )

    user = request.state.user
    if not user:
        raise HTTPException(status_code=401, detail="User not authenticated")
    user_folder = UPLOAD_DIRECTORY / str(user["_id"])  # e.g., uploads/<user_id>
    type_folder = user_folder / content_type_to_folder[file.content_type]
    # Create directories if they don't exist
    type_folder.mkdir(parents=True, exist_ok=True)

    # Set the file path where the file will be saved
    file_path = type_folder / file.filename

    try:
        with file_path.open("wb") as buffer:
            buffer.write(await file.read())
        return JSONResponse(
            {"filename": file.filename, "content_type": file.content_type}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to upload file") from e


@router.get("/download/{filename}")
async def document_download(request: Request, filename: str):
    user = request.state.user
    if not user:
        raise HTTPException(status_code=401, detail="User not authenticated")

    # Get the file extension
    file_extension = Path(filename).suffix.lower()

    # Get the corresponding folder based on the file extension
    file_type = EXTENSION_TO_TYPE.get(file_extension)
    if not file_type:
        raise HTTPException(status_code=400, detail="Unsupported file type")

    # Determine the user's folder and content-type-specific subfolder
    user_folder = UPLOAD_DIRECTORY / str(user["user_id"])  # e.g., uploads/<user_id>
    type_folder = user_folder / file_type  # e.g., uploads/<user_id>/pdfs

    # Set the file path
    file_path = type_folder / filename

    # Check if the file exists and return it, or raise an error
    if file_path.exists():
        return FileResponse(file_path)
    raise HTTPException(status_code=404, detail="File not found")


def file_streamer(file_path: Path, chunk_size: int = 1024 * 1024):
    """Generator to read a file in chunks."""
    with file_path.open("rb") as file:
        while chunk := file.read(chunk_size):
            yield chunk


@router.get("/stream/{filename}")
async def stream_file(request: Request, filename: str, range: str = Header(None)):
    user = request.state.user
    if not user:
        raise HTTPException(status_code=401, detail="User not authenticated")

    # Get the file extension
    file_extension = Path(filename).suffix.lower()

    # Get the corresponding folder based on the file extension
    file_type = EXTENSION_TO_TYPE.get(file_extension)
    if not file_type:
        raise HTTPException(status_code=400, detail="Unsupported file type")

    # Determine the user's folder and content-type-specific subfolder
    user_folder = UPLOAD_DIRECTORY / str(user["_id"])  # e.g., uploads/<user_id>
    type_folder = user_folder / file_type  # e.g., uploads/<user_id>/pdfs

    # Set the file path
    file_path = type_folder / filename

    # Check if the file exists
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")

    file_size = file_path.stat().st_size

    # Handle range requests for video files
    if range:
        start, end = range.replace("bytes=", "").split("-")
        start = int(start)
        end = int(end) if end else file_size - 1
        chunk_size = end - start + 1
        headers = {
            "Content-Range": f"bytes {start}-{end}/{file_size}",
            "Accept-Ranges": "bytes",
            "Content-Length": str(chunk_size),
            "Content-Type": (
                "video/mp4" if file_extension == ".mp4" else "application/octet-stream"
            ),
        }
        return StreamingResponse(
            file_streamer(file_path), headers=headers, status_code=206
        )

    # For non-range requests, return the entire file as a stream
    headers = {
        "Content-Length": str(file_size),
        "Content-Type": (
            "video/mp4" if file_extension == ".mp4" else "application/octet-stream"
        ),
    }
    return StreamingResponse(file_streamer(file_path), headers=headers)
