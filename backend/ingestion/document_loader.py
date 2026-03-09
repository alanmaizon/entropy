"""
Document Loader.

Loads raw text from various sources (plain text, file paths, URLs)
and normalises it into a single string for downstream processing.
"""

import pathlib


class DocumentLoader:
    """Load and normalise documents from various sources."""

    def load_text(self, text: str) -> str:
        """Return a pre-loaded string as-is after basic cleanup.

        Args:
            text: Raw input text.

        Returns:
            Cleaned text string.
        """
        return text.strip()

    def load_file(self, path: str | pathlib.Path) -> str:
        """Read and return the contents of a local text file.

        Args:
            path: Filesystem path to the text file.

        Returns:
            File contents as a string.

        Raises:
            FileNotFoundError: If the file does not exist.
        """
        return pathlib.Path(path).read_text(encoding="utf-8").strip()
