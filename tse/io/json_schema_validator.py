"""
JSON schema validation for simulator input files.

Requirements:
- TSE-FUNC-088: JSON schema validation
- TSE-INTF-020: Simulator input format compliance
"""

import json
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
import jsonschema
from jsonschema import validate, ValidationError, SchemaError


class JSONSchemaValidator:
    """
    Validates JSON files against the simulator input schema.

    Requirements: TSE-FUNC-088, TSE-INTF-020
    """

    def __init__(self, schema_path: Optional[str] = None):
        """
        Initialize schema validator.

        Args:
            schema_path: Path to JSON schema file (None = use default)
        """
        if schema_path is None:
            # Use default schema from resources
            project_root = Path(__file__).parent.parent.parent
            schema_path = project_root / "resources" / "simulator_input_schema.json"

        self._schema_path = Path(schema_path)
        self._schema = self._load_schema()

    def _load_schema(self) -> Dict[str, Any]:
        """Load JSON schema from file."""
        try:
            with open(self._schema_path, 'r', encoding='utf-8') as f:
                schema = json.load(f)
            return schema
        except FileNotFoundError:
            raise FileNotFoundError(f"Schema file not found: {self._schema_path}")
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in schema file: {e}")

    def validate_json_data(self, json_data: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """
        Validate JSON data against schema.

        Args:
            json_data: Dictionary representing JSON data

        Returns:
            Tuple of (is_valid, error_message)

        Requirements: TSE-FUNC-088
        """
        try:
            validate(instance=json_data, schema=self._schema)
            return (True, None)

        except ValidationError as e:
            error_msg = self._format_validation_error(e)
            return (False, error_msg)

        except SchemaError as e:
            return (False, f"Schema error: {e.message}")

    def validate_json_file(self, filepath: str) -> Tuple[bool, Optional[str]]:
        """
        Validate JSON file against schema.

        Args:
            filepath: Path to JSON file

        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                json_data = json.load(f)

            return self.validate_json_data(json_data)

        except FileNotFoundError:
            return (False, f"File not found: {filepath}")

        except json.JSONDecodeError as e:
            return (False, f"Invalid JSON: {e}")

    def validate_json_string(self, json_string: str) -> Tuple[bool, Optional[str]]:
        """
        Validate JSON string against schema.

        Args:
            json_string: JSON as string

        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            json_data = json.loads(json_string)
            return self.validate_json_data(json_data)

        except json.JSONDecodeError as e:
            return (False, f"Invalid JSON: {e}")

    def _format_validation_error(self, error: ValidationError) -> str:
        """
        Format validation error for user display.

        Args:
            error: ValidationError object

        Returns:
            Formatted error message
        """
        # Get path to error
        path = " -> ".join(str(p) for p in error.path) if error.path else "root"

        # Build error message
        message = f"Validation error at '{path}': {error.message}"

        # Add context if available
        if error.context:
            message += "\n\nRelated errors:"
            for ctx_error in error.context:
                ctx_path = " -> ".join(str(p) for p in ctx_error.path) if ctx_error.path else "root"
                message += f"\n  • {ctx_path}: {ctx_error.message}"

        return message

    def get_validation_errors(self, json_data: Dict[str, Any]) -> List[str]:
        """
        Get all validation errors (not just first one).

        Args:
            json_data: Dictionary representing JSON data

        Returns:
            List of error messages
        """
        errors = []

        try:
            validator = jsonschema.Draft7Validator(self._schema)

            for error in validator.iter_errors(json_data):
                error_msg = self._format_validation_error(error)
                errors.append(error_msg)

        except SchemaError as e:
            errors.append(f"Schema error: {e.message}")

        return errors

    def is_valid(self, json_data: Dict[str, Any]) -> bool:
        """
        Quick check if JSON data is valid.

        Args:
            json_data: Dictionary representing JSON data

        Returns:
            True if valid, False otherwise
        """
        is_valid, _ = self.validate_json_data(json_data)
        return is_valid

    def get_schema(self) -> Dict[str, Any]:
        """Get the loaded schema."""
        return self._schema

    def get_schema_version(self) -> Optional[str]:
        """Get schema version if specified."""
        return self._schema.get("$schema")
