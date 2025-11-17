"""
JSON schema validation for simulator input files.

This module validates exported JSON files against the simulator input schema.

Requirements:
- TSE-FUNC-088: Validate JSON against schema
- TSE-INTF-020: Use JSON schema for validation
"""

import json
from pathlib import Path
from typing import Dict, Any, List, Tuple, Optional
import jsonschema
from jsonschema import Draft7Validator, ValidationError


# Path to schema file
SCHEMA_PATH = Path(__file__).parent.parent.parent / "resources" / "simulator_input_schema.json"


def load_schema() -> Dict[str, Any]:
    """
    Load the simulator input JSON schema.

    Returns:
        Dictionary containing the JSON schema

    Raises:
        FileNotFoundError: If schema file not found
        ValueError: If schema is invalid JSON
    """
    if not SCHEMA_PATH.exists():
        raise FileNotFoundError(f"Schema file not found: {SCHEMA_PATH}")

    try:
        with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
            schema = json.load(f)
        return schema
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in schema file: {e}")


def validate_json_file(file_path: str) -> Tuple[bool, List[str]]:
    """
    Validate a JSON file against the simulator input schema.

    Args:
        file_path: Path to JSON file to validate

    Returns:
        Tuple of (is_valid, error_messages)
        - is_valid: True if validation passed, False otherwise
        - error_messages: List of validation error messages (empty if valid)

    Raises:
        FileNotFoundError: If JSON file not found

    Requirements: TSE-FUNC-088, TSE-INTF-020
    """
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"JSON file not found: {path}")

    # Load JSON data
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        return False, [f"Invalid JSON: {e}"]

    # Validate against schema
    return validate_json_data(data)


def validate_json_data(data: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """
    Validate JSON data against the simulator input schema.

    Args:
        data: Dictionary containing JSON data to validate

    Returns:
        Tuple of (is_valid, error_messages)
        - is_valid: True if validation passed, False otherwise
        - error_messages: List of validation error messages (empty if valid)

    Requirements: TSE-FUNC-088, TSE-INTF-020
    """
    # Load schema
    try:
        schema = load_schema()
    except Exception as e:
        return False, [f"Failed to load schema: {e}"]

    # Create validator
    validator = Draft7Validator(schema)

    # Collect all validation errors
    errors = []
    for error in validator.iter_errors(data):
        # Format error message with path
        path = ".".join(str(p) for p in error.path) if error.path else "root"
        errors.append(f"{path}: {error.message}")

    if errors:
        return False, errors
    else:
        return True, []


def validate_json_string(json_string: str) -> Tuple[bool, List[str]]:
    """
    Validate a JSON string against the simulator input schema.

    Args:
        json_string: JSON string to validate

    Returns:
        Tuple of (is_valid, error_messages)
        - is_valid: True if validation passed, False otherwise
        - error_messages: List of validation error messages (empty if valid)
    """
    try:
        data = json.loads(json_string)
    except json.JSONDecodeError as e:
        return False, [f"Invalid JSON: {e}"]

    return validate_json_data(data)


def get_schema_version() -> str:
    """
    Get the version of the loaded schema.

    Returns:
        Schema version string

    Raises:
        FileNotFoundError: If schema file not found
        ValueError: If schema is invalid
    """
    schema = load_schema()
    # Extract version from schema ID or return default
    schema_id = schema.get("$id", "")
    if "v" in schema_id:
        return schema_id.split("v")[-1].split(".json")[0]
    return "1.0"


def validate_with_details(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate JSON data and return detailed validation report.

    Args:
        data: Dictionary containing JSON data to validate

    Returns:
        Dictionary with validation results:
        {
            "valid": bool,
            "error_count": int,
            "warning_count": int,
            "errors": List[str],
            "warnings": List[str],
            "schema_version": str,
        }
    """
    is_valid, errors = validate_json_data(data)

    # Currently no warnings, but structure is ready for future enhancements
    warnings = []

    return {
        "valid": is_valid,
        "error_count": len(errors),
        "warning_count": len(warnings),
        "errors": errors,
        "warnings": warnings,
        "schema_version": get_schema_version(),
    }
