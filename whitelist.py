"""Vulture whitelist — these symbols are used but vulture can't detect it."""

# Public API — called by external users of the pycodegate package
import pycodegate.api
import pycodegate.constants
import pycodegate.types
import pycodegate.utils.ast_helpers

pycodegate.api.diagnose  # public API function
pycodegate.constants.SCORE_GREAT  # exported threshold constant
pycodegate.constants.SCORE_NEEDS_WORK  # exported threshold constant
pycodegate.types.Diagnostic.column  # used by rules that track column offsets
pycodegate.types.ProjectInfo.has_type_hints  # accessed in output/templates
pycodegate.utils.ast_helpers.parse_file  # utility used by rule checkers
