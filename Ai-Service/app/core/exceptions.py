class DocumentNotFoundError(Exception):
    """Raised when a document cannot be found or the user doesn't own it."""
    pass


class ExtractionPendingError(Exception):
    """Raised when AI extraction for a document has not yet completed."""
    pass


class ExtractionFailedError(Exception):
    """Raised when AI extraction for a document failed."""
    pass
