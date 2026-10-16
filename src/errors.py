"""Only deliberately authored messages may appear in the CSV/log diagnostics."""
from urllib.error import HTTPError, URLError

class SafeError(ValueError):
    """Message is constructed by this application and must never include secrets/URLs."""

def safe_error(exc):
    if isinstance(exc,SafeError):return str(exc)
    if isinstance(exc,HTTPError):
        return {401:'API rejected authentication (HTTP 401). Check the provider key.',
                403:'API denied access (HTTP 403). Check account permissions and plan access.',
                429:'API request limit reached (HTTP 429). Wait before retrying.'}.get(exc.code,f'API request failed (HTTP {exc.code}).')
    if isinstance(exc,(TimeoutError,URLError)):return 'Network request failed or timed out. Retry later.'
    return f'{type(exc).__name__}: unexpected failure; raw provider details are withheld to protect credentials.'
