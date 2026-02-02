"""
API routes for lecture management
"""
from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
import os
import uuid
from pathlib import Path

from ...database import get_db
from ...models import Lecture, Chunk
from ...models.schemas import (
    LectureResponse,
    LectureDetail,
    UploadResponse
)
from ...services.pdf_processor import pdf_processor
from ...services.embeddings import embedding_service
from ...utils.chunking import text_chunker
from ...config import settings

router = APIRouter()


@router.post("/upload", response_model=UploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_lecture(
    file: UploadFile = File(...),
    module_code: str = Form(...),
    week_number: int = Form(...),
    lecture_title: str = Form(...),
    db: Session = Depends(get_db)
):
    """
    Upload a lecture PDF file

    - **file**: PDF file (max 50MB)
    - **module_code**: Module code (e.g., COMP3001)
    - **week_number**: Week number (1-24)
    - **lecture_title**: Title of the lecture
    """
    # Validate file type
    if not file.filename.endswith('.pdf'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF files are allowed"
        )

    # Validate file size
    file_size = 0
    chunk_size = 1024 * 1024  # 1MB chunks
    temp_file = []

    # Read file in chunks to check size
    while True:
        chunk = await file.read(chunk_size)
        if not chunk:
            break
        file_size += len(chunk)
        temp_file.append(chunk)

        if file_size > settings.max_file_size_mb * 1024 * 1024:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"File size exceeds maximum allowed ({settings.max_file_size_mb}MB)"
            )

    # Reset file pointer
    await file.seek(0)

    try:
        # Create unique filename
        file_extension = Path(file.filename).suffix
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        file_path = os.path.join(settings.upload_dir, unique_filename)

        # Save file
        with open(file_path, "wb") as f:
            f.write(b"".join(temp_file))

        # Validate PDF
        if not pdf_processor.validate_pdf(file_path):
            os.remove(file_path)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or corrupted PDF file"
            )

        # Extract text from PDF
        slides, num_pages = pdf_processor.extract_text_from_pdf(file_path)

        # Create lecture record
        lecture = Lecture(
            module_code=module_code.upper(),
            week_number=week_number,
            title=lecture_title,
            filename=unique_filename,
            num_pages=num_pages
        )

        db.add(lecture)
        db.commit()
        db.refresh(lecture)

        # Chunk the slides
        chunks_data = text_chunker.chunk_by_slide(slides)

        # Generate embeddings and create chunk records
        if chunks_data:
            # Extract text content for embedding
            texts = [chunk["content"] for chunk in chunks_data]

            # Generate embeddings in batch
            print(f"Generating embeddings for {len(texts)} chunks...")
            embeddings = embedding_service.embed_batch(texts)

            # Create chunk records
            chunks = []
            for chunk_data, embedding in zip(chunks_data, embeddings):
                chunk = Chunk(
                    lecture_id=lecture.id,
                    content=chunk_data["content"],
                    slide_number=chunk_data["slide_number"],
                    embedding=embedding
                )
                chunks.append(chunk)

            db.bulk_save_objects(chunks)
            db.commit()

            print(f"Created {len(chunks)} chunks for lecture {lecture.id}")

        return UploadResponse(
            status="success",
            message=f"Lecture uploaded and processed successfully",
            lecture=LectureResponse.from_orm(lecture),
            chunks_created=len(chunks_data) if chunks_data else 0
        )

    except Exception as e:
        # Clean up file if upload fails
        if os.path.exists(file_path):
            os.remove(file_path)

        # Rollback database changes
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Upload failed: {str(e)}"
        )


@router.get("", response_model=List[LectureResponse])
async def get_lectures(
    module_code: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Get all lectures, optionally filtered by module code
    """
    query = db.query(Lecture)

    if module_code:
        query = query.filter(Lecture.module_code == module_code.upper())

    lectures = query.order_by(Lecture.week_number).all()

    return [LectureResponse.from_orm(lecture) for lecture in lectures]


@router.get("/{lecture_id}", response_model=LectureDetail)
async def get_lecture(
    lecture_id: str,
    db: Session = Depends(get_db)
):
    """
    Get a specific lecture by ID
    """
    lecture = db.query(Lecture).filter(Lecture.id == lecture_id).first()

    if not lecture:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lecture not found"
        )

    # Count chunks
    chunks_count = db.query(Chunk).filter(Chunk.lecture_id == lecture_id).count()

    lecture_data = LectureResponse.from_orm(lecture)
    return LectureDetail(
        **lecture_data.dict(),
        chunks_count=chunks_count
    )


@router.delete("/{lecture_id}")
async def delete_lecture(
    lecture_id: str,
    db: Session = Depends(get_db)
):
    """
    Delete a lecture and its associated chunks
    """
    lecture = db.query(Lecture).filter(Lecture.id == lecture_id).first()

    if not lecture:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lecture not found"
        )

    # Delete file
    file_path = os.path.join(settings.upload_dir, lecture.filename)
    if os.path.exists(file_path):
        os.remove(file_path)

    # Delete from database (chunks will be cascade deleted)
    db.delete(lecture)
    db.commit()

    return {
        "status": "success",
        "message": f"Lecture {lecture_id} deleted successfully"
    }


@router.get("/modules/list")
async def list_modules(db: Session = Depends(get_db)):
    """
    Get list of all unique module codes
    """
    modules = db.query(Lecture.module_code).distinct().all()
    return {
        "modules": [module[0] for module in modules]
    }
