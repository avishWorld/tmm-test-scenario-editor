"""
ID generation utilities.

Requirements:
- TSE-FUNC-023: Unique Target ID auto-assignment
- TSE-FUNC-028: MMSI auto-generation
"""

from typing import Set


class MMSIGenerator:
    """
    Generates unique MMSI (Maritime Mobile Service Identity) numbers.

    MMSI is a 9-digit number used to uniquely identify ships.
    This generator creates valid test MMSI numbers in the range
    111000000-111999999 (reserved for testing/simulation).

    Requirements: TSE-FUNC-028
    """

    def __init__(self, start_number: int = 111000001):
        """
        Initialize MMSI generator.

        Args:
            start_number: Starting MMSI number (default: 111000001)
        """
        if not 111000000 <= start_number <= 999999999:
            raise ValueError(f"MMSI must be 9 digits: {start_number}")

        self._current = start_number
        self._used: Set[int] = set()

    def generate(self) -> int:
        """
        Generate next unique MMSI number.

        Returns:
            Unique 9-digit MMSI number

        Raises:
            RuntimeError: If all MMSI numbers in range are exhausted
        """
        if self._current > 111999999:
            raise RuntimeError("MMSI range exhausted (111000001-111999999)")

        mmsi = self._current
        self._used.add(mmsi)
        self._current += 1

        return mmsi

    def mark_used(self, mmsi: int) -> None:
        """
        Mark an MMSI number as used (for manually assigned MMSIs).

        Args:
            mmsi: MMSI number to mark as used

        Raises:
            ValueError: If MMSI is invalid or already used
        """
        if not 100000000 <= mmsi <= 999999999:
            raise ValueError(f"MMSI must be 9 digits: {mmsi}")

        if mmsi in self._used:
            raise ValueError(f"MMSI {mmsi} already in use")

        self._used.add(mmsi)

        # Advance current counter if necessary
        if 111000000 <= mmsi <= 111999999 and mmsi >= self._current:
            self._current = mmsi + 1

    def is_used(self, mmsi: int) -> bool:
        """
        Check if an MMSI number is already used.

        Args:
            mmsi: MMSI number to check

        Returns:
            True if MMSI is already used, False otherwise
        """
        return mmsi in self._used

    def reset(self) -> None:
        """Reset generator to initial state."""
        self._current = 111000001
        self._used.clear()


class TargetIDGenerator:
    """
    Generates unique target IDs (T1, T2, T3, ...).

    Requirements: TSE-FUNC-023
    """

    def __init__(self, prefix: str = "T"):
        """
        Initialize Target ID generator.

        Args:
            prefix: Prefix for target IDs (default: "T")
        """
        self._prefix = prefix
        self._current = 1
        self._used: Set[str] = set()

    def generate(self) -> str:
        """
        Generate next unique target ID.

        Returns:
            Unique target ID (e.g., "T1", "T2", ...)
        """
        target_id = f"{self._prefix}{self._current}"
        self._used.add(target_id)
        self._current += 1

        return target_id

    def mark_used(self, target_id: str) -> None:
        """
        Mark a target ID as used (for manually assigned IDs).

        Args:
            target_id: Target ID to mark as used

        Raises:
            ValueError: If target ID is already used
        """
        if target_id in self._used:
            raise ValueError(f"Target ID {target_id} already in use")

        self._used.add(target_id)

        # Try to extract number and advance counter if necessary
        if target_id.startswith(self._prefix):
            try:
                num = int(target_id[len(self._prefix):])
                if num >= self._current:
                    self._current = num + 1
            except ValueError:
                pass  # Non-numeric suffix, ignore

    def is_used(self, target_id: str) -> bool:
        """
        Check if a target ID is already used.

        Args:
            target_id: Target ID to check

        Returns:
            True if target ID is already used, False otherwise
        """
        return target_id in self._used

    def reset(self) -> None:
        """Reset generator to initial state."""
        self._current = 1
        self._used.clear()


# Global instances for convenience
_mmsi_generator = MMSIGenerator()
_target_id_generator = TargetIDGenerator()


def generate_mmsi() -> int:
    """
    Generate a unique MMSI number using the global generator.

    Returns:
        Unique 9-digit MMSI number

    Requirements: TSE-FUNC-028
    """
    return _mmsi_generator.generate()


def generate_target_id() -> str:
    """
    Generate a unique target ID using the global generator.

    Returns:
        Unique target ID (e.g., "T1", "T2", ...)

    Requirements: TSE-FUNC-023
    """
    return _target_id_generator.generate()


def mark_mmsi_used(mmsi: int) -> None:
    """Mark an MMSI as used in the global generator."""
    _mmsi_generator.mark_used(mmsi)


def mark_target_id_used(target_id: str) -> None:
    """Mark a target ID as used in the global generator."""
    _target_id_generator.mark_used(target_id)


def reset_generators() -> None:
    """Reset all global ID generators."""
    _mmsi_generator.reset()
    _target_id_generator.reset()
