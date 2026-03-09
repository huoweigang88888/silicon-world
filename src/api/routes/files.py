"""
文件上传路由

支持图片、文件上传
"""

from fastapi import APIRouter, UploadFile, File, HTTPException, Form
from typing import Optional
import uuid
import os
from pathlib import Path
from datetime import datetime

router = APIRouter(tags=["Files"])

# 上传目录
UPLOAD_DIR = Path(__file__).parent.parent.parent / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)

# 允许的文件类型
ALLOWED_IMAGE_TYPES = ["image/jpeg", "image/png", "image/gif", "image/webp"]
ALLOWED_FILE_TYPES = [
    "application/pdf",
    "application/msword",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "application/vnd.ms-excel",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    "text/plain",
    "text/csv",
    "application/zip",
    "application/x-zip-compressed",
]

# 最大文件大小 (10MB)
MAX_FILE_SIZE = 10 * 1024 * 1024


@router.post("/api/v1/files/upload/image")
async def upload_image(file: UploadFile = File(...)):
    """
    上传图片
    
    - **file**: 图片文件
    
    支持的格式：JPEG, PNG, GIF, WebP
    最大大小：10MB
    """
    # 检查文件类型
    if file.content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"不支持的图片类型：{file.content_type}"
        )
    
    # 检查文件大小
    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"文件过大，最大支持 10MB"
        )
    
    # 生成文件名
    file_ext = file.filename.split(".")[-1] if "." in file.filename else "jpg"
    file_name = f"{uuid.uuid4().hex}.{file_ext}"
    file_path = UPLOAD_DIR / "images" / file_name
    
    # 创建目录
    file_path.parent.mkdir(exist_ok=True)
    
    # 保存文件
    with open(file_path, "wb") as f:
        f.write(content)
    
    # 生成访问 URL
    file_url = f"/api/v1/files/images/{file_name}"
    
    return {
        "success": True,
        "file_id": file_name,
        "file_url": file_url,
        "file_type": file.content_type,
        "file_size": len(content),
        "uploaded_at": datetime.utcnow().isoformat()
    }


@router.post("/api/v1/files/upload/document")
async def upload_document(file: UploadFile = File(...)):
    """
    上传文档
    
    - **file**: 文档文件
    
    支持的格式：PDF, DOC, DOCX, XLS, XLSX, TXT, CSV, ZIP
    最大大小：10MB
    """
    # 检查文件类型
    if file.content_type not in ALLOWED_FILE_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"不支持的文件类型：{file.content_type}"
        )
    
    # 检查文件大小
    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"文件过大，最大支持 10MB"
        )
    
    # 生成文件名
    file_ext = file.filename.split(".")[-1] if "." in file.filename else "dat"
    file_name = f"{uuid.uuid4().hex}.{file_ext}"
    file_path = UPLOAD_DIR / "documents" / file_name
    
    # 创建目录
    file_path.parent.mkdir(exist_ok=True)
    
    # 保存文件
    with open(file_path, "wb") as f:
        f.write(content)
    
    # 生成访问 URL
    file_url = f"/api/v1/files/documents/{file_name}"
    
    return {
        "success": True,
        "file_id": file_name,
        "file_url": file_url,
        "file_type": file.content_type,
        "file_size": len(content),
        "original_name": file.filename,
        "uploaded_at": datetime.utcnow().isoformat()
    }


@router.get("/api/v1/files/images/{file_id}")
async def get_image(file_id: str):
    """
    获取图片
    
    - **file_id**: 图片 ID
    """
    file_path = UPLOAD_DIR / "images" / file_id
    
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="图片不存在")
    
    from fastapi.responses import FileResponse
    return FileResponse(file_path, media_type="image/jpeg")


@router.get("/api/v1/files/documents/{file_id}")
async def get_document(file_id: str):
    """
    获取文档
    
    - **file_id**: 文档 ID
    """
    file_path = UPLOAD_DIR / "documents" / file_id
    
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="文档不存在")
    
    from fastapi.responses import FileResponse
    return FileResponse(file_path, media_type="application/octet-stream")


@router.delete("/api/v1/files/{file_id}")
async def delete_file(file_id: str, file_type: str = Form(...)):
    """
    删除文件
    
    - **file_id**: 文件 ID
    - **file_type**: 文件类型 (image/document)
    """
    if file_type == "image":
        file_path = UPLOAD_DIR / "images" / file_id
    elif file_type == "document":
        file_path = UPLOAD_DIR / "documents" / file_id
    else:
        raise HTTPException(status_code=400, detail="无效的文件类型")
    
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="文件不存在")
    
    os.remove(file_path)
    
    return {
        "success": True,
        "message": "文件已删除"
    }
