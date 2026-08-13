from pathlib import Path

from config.settings import LANGUAGETOOL_DIR, LANGUAGETOOL_ENABLED, LANGUAGETOOL_LOCAL_SERVER_URL

try:
    import language_tool_python
except ModuleNotFoundError:
    language_tool_python = None

_tool_instance = None
_tool_failed = False


def get_languagetool():
    global _tool_instance, _tool_failed

    if not LANGUAGETOOL_ENABLED or language_tool_python is None:
        return None
    if _tool_failed:
        return None
    if _tool_instance is not None:
        return _tool_instance

    jar_dir = Path(LANGUAGETOOL_DIR)
    try:
        # Strictly offline mode: only connect to a locally running LT server.
        # If local resources/server are missing, we fallback to heuristic grammar checks.
        if not jar_dir.exists():
            return None
        _tool_instance = language_tool_python.LanguageTool(
            "en-US",
            remote_server=LANGUAGETOOL_LOCAL_SERVER_URL,
            config={"cacheSize": 1000, "pipelineCaching": True},
        )
    except Exception:
        _tool_failed = True
        _tool_instance = None

    return _tool_instance
