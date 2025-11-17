"""
File I/O and data access layer.
"""

from .project_file import (
    save_project,
    load_project,
    get_project_metadata,
    PROJECT_FILE_VERSION,
)
from .json_exporter import (
    export_to_json,
    export_to_string,
    get_export_summary,
)
from .json_schema_validator import (
    validate_json_file,
    validate_json_data,
    validate_json_string,
    validate_with_details,
    get_schema_version,
    load_schema,
)

__all__ = [
    # Project file I/O
    "save_project",
    "load_project",
    "get_project_metadata",
    "PROJECT_FILE_VERSION",
    # JSON export
    "export_to_json",
    "export_to_string",
    "get_export_summary",
    # Schema validation
    "validate_json_file",
    "validate_json_data",
    "validate_json_string",
    "validate_with_details",
    "get_schema_version",
    "load_schema",
]
