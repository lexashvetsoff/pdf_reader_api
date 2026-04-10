from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends
from fastapi.responses import JSONResponse, PlainTextResponse
from app.services.parse_service import run_parsing
from app.services.pdf_service import save_upload_file_to_temp, delete_temp_file
from app.core.exceptions import ParsingError, SettingsNotFoundError
from app.config import get_raw_settings


router = APIRouter()


@router.post("/parse")
async def parse_pdf_endpoint(
    file: UploadFile = File(...),
    code: str = Form(...),
    doc_type: str = Form("Reestr"),
    output_format: str = Form(None),
    raw_settings: dict = Depends(get_raw_settings)
):
    if doc_type not in ("Reestr", "Protocol"):
        raise HTTPException(400, "doc_type must be 'Reestr' or 'Protocol'")
    
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(400, "Only PDF files are allowed")
    
    temp_path = None
    try:
        temp_path = await save_upload_file_to_temp(file)
        result, fmt = run_parsing(temp_path, code, doc_type, raw_settings, output_format)
        
        if fmt == "json":
            return JSONResponse(content=result)
        else:
            return PlainTextResponse(content=result, media_type="application/xml")
    except SettingsNotFoundError as e:
        raise HTTPException(400, str(e))
    except ParsingError as e:
        raise HTTPException(422, str(e))
    except Exception as e:
        raise HTTPException(500, f"Internal server error: {str(e)}")
    finally:
        if temp_path:
            delete_temp_file(temp_path)
