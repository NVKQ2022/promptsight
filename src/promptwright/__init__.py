"""Backward-compatibility shim for promptwright -> promptsight transition."""

import sys
import warnings

import promptsight as promptsight
from promptsight import *  # noqa: F403

# Re-export all submodules so `import promptwright.builder` works seamlessly
for mod_name, mod in list(sys.modules.items()):
    if mod_name.startswith("promptsight"):
        alias_name = "promptwright" + mod_name[len("promptsight") :]
        sys.modules[alias_name] = mod

warnings.warn(
    "The 'promptwright' package has been renamed to 'promptsight'. "
    "Please update your imports to 'promptsight'.",
    DeprecationWarning,
    stacklevel=2,
)
