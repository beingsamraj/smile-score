from pydantic import BaseModel
from typing import List, Dict, Any, Optional

class CsvRowError(BaseModel):
    row: int
    errors: List[str]

class CsvValidationPreview(BaseModel):
    valid: bool
    total_rows: int
    valid_rows: int
    invalid_rows: int
    errors: List[CsvRowError]

class CsvImportResponse(BaseModel):
    success: bool
    imported_count: int
    message: str
