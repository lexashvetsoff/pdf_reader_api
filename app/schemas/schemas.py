from pydantic import BaseModel, Field


class RequestData(BaseModel):
    file_path: str = Field(...)
    code: str = Field(...)
    doc_type: str = Field('Reestr')
    output_format: str = Field('xml')
