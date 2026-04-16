from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends
from fastapi.responses import JSONResponse, PlainTextResponse
from app.services.parse_service import run_parsing
from app.services.pdf_service import save_upload_file_to_temp, delete_temp_file
from app.core.exceptions import ParsingError, SettingsNotFoundError
from app.schemas.schemas import RequestData
from app.config import get_raw_settings


router = APIRouter()


@router.post("/parse_bin")
async def parse_pdf_endpoint(
    file: UploadFile = File(...),
    code: str = Form(...),
    doc_type: str = Form("Reestr"),
    output_format: str = Form(None),
    raw_settings: dict = Depends(get_raw_settings)
):
    '''На вход получает двоичные данные, возвращает строку'''
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



@router.post("/parse_file")
async def parse_pdf_from_path_endpoint(
    data: RequestData,
    raw_settings: dict = Depends(get_raw_settings)
):
    '''На вход получает путь к файлу, возвращает строку'''
    if data.doc_type not in ("Reestr", "Protocol"):
        raise HTTPException(400, "doc_type must be 'Reestr' or 'Protocol'")
    
    if not data.file_path.lower().endswith('.pdf'):
        raise HTTPException(400, "Only PDF files are allowed")
    
    try:
        result, fmt = run_parsing(data.file_path, data.code, data.doc_type, raw_settings, data.output_format)
        
        if fmt == "json":
            return JSONResponse(content=result)
        else:
            return PlainTextResponse(content=result, media_type="application/xml; charset=windows-1251")
    except SettingsNotFoundError as e:
        raise HTTPException(400, str(e))
    except ParsingError as e:
        raise HTTPException(422, str(e))
    except Exception as e:
        raise HTTPException(500, f"Internal server error: {str(e)}")
    finally:
        if data.file_path:
            delete_temp_file(data.file_path)


# @router.post("/parce_file")
# async def parse_pdf_from_path_endpoint(
#     file_path: str,
#     code: str,
#     doc_type: str = 'Reestr',
#     output_format: str = 'xml',
#     raw_settings: dict = Depends(get_raw_settings)
# ):
#     '''На вход получает путь к файлу, возвращает строку'''
#     if doc_type not in ("Reestr", "Protocol"):
#         raise HTTPException(400, "doc_type must be 'Reestr' or 'Protocol'")
    
#     if not file_path.lower().endswith('.pdf'):
#         raise HTTPException(400, "Only PDF files are allowed")
    
#     try:
#         result, fmt = run_parsing(file_path, code, doc_type, raw_settings, output_format)
        
#         if fmt == "json":
#             return JSONResponse(content=result)
#         else:
#             return PlainTextResponse(content=result, media_type="application/xml")
#     except SettingsNotFoundError as e:
#         raise HTTPException(400, str(e))
#     except ParsingError as e:
#         raise HTTPException(422, str(e))
#     except Exception as e:
#         raise HTTPException(500, f"Internal server error: {str(e)}")
#     finally:
#         if file_path:
#             delete_temp_file(file_path)
