from __future__ import annotations

import json
from typing import Any, Final
from pathlib import Path

from ansible.errors import AnsibleFileNotFound, AnsibleLookupError
from ansible.module_utils.basic import missing_required_lib
from ansible.parsing.ajson import AnsibleJSONEncoder
from ansible.plugins.lookup import LookupBase
from ansible.vars.hostvars import HostVars

__metaclass__ = type

_ANSIBLE_FACTS: Final = "ansible_facts"

DOCUMENTATION: Final = """
    name: jsonnet
    author: Stephan Wolski
    version_added: "1.0"
    short_description: evaluate Jsonnet files
    description:
        - Evaluates Jsonnet files
    options:
      _terms:
        description: path(s) of files to evaluate
        required: True
    notes:
      - You can access facts by importing `ansible_facts` in the Jsonnet file(s).
"""

EXAMPLES: Final = """
# Search for `foo.jsonnet` in the `files` subdirectory and return the evaluted object
- ansible.builtin.debug:
    msg: "{{ lookup('slowki.jsonnet.jsonnet', 'foo.jsonnet') }}"
"""

RETURN: Final = """
    _raw:
        description:
            - The evaluated contents of the jsonnet file(s)
"""


class LookupModule(LookupBase):
    """A plugin that evaluates Jsonnet files."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)

    def _import_callback(self, directory: str, relative_path: str) -> tuple[str, str]:
        """Jsonnet import callback.

        Args:
            directory: The directory the file is being imported from.
            relative_path: The path being imported.

        Returns:
            A tuple containing the resolved path and the file contents.
        """
        resolved_path = Path(directory) / relative_path
        if resolved_path.exists():
            return str(resolved_path), resolved_path.read_bytes()

        raise AnsibleFileNotFound(
            f"Could not import {relative_path}",
            paths=[directory],
            file_name=relative_path,
        )

    def run(self, terms: list[Any], variables: HostVars = None, **kwargs: Any) -> list:
        """Run the lookup plugin.

        Args:
            terms: The files toe evaluate.
            variables: The ansible variables in scope.
            **kwargs: Unused.
        """
        try:
            import _jsonnet as jsonnet
        except ImportError as e:
            raise AnsibleLookupError(
                missing_required_lib(library="jsonnet", reason=str(e))
            )

        if kwargs:
            raise AnsibleLookupError(f"Expected arguments: {kwargs!r}")

        def import_callback(directory: str, relative_path: str) -> tuple[str, str]:
            if relative_path == _ANSIBLE_FACTS:
                return (
                    relative_path,
                    json.dumps(variables, cls=AnsibleJSONEncoder, indent=4).encode(),
                )
            return self._import_callback(directory, relative_path)

        return [
            jsonnet.evaluate_file(
                self.find_file_in_search_path(variables, "files", file),
                import_callback=import_callback,
            )
            for file in terms
        ]
