# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""
Test for code actions over LSP.
"""

import os

import pytest
from hamcrest import assert_that, is_

from .lsp_test_client import constants, session, utils

TEST_FILE_PATH = constants.TEST_DATA / "sample1" / "sample.py"
TEST_FILE_URI = utils.as_uri(str(TEST_FILE_PATH))
LINTER = utils.get_server_info_defaults()["name"]


@pytest.mark.parametrize(
    ("code", "contents", "command"),
    [
        (
            "E201",
            "print ( 'Open parentheses should not have any space before or after them.')",
            {
                "title": f"{LINTER}: Run document formatting",
                "command": "editor.action.formatDocument",
            },
        ),
        (
            "E202",
            "print('Closing parentheses should not have any whitespace before them.' )",
            {
                "title": f"{LINTER}: Run document formatting",
                "command": "editor.action.formatDocument",
            },
        ),
        (
            "E241",
            "x = [1,   2]",
            {
                "title": f"{LINTER}: Run document formatting",
                "command": "editor.action.formatDocument",
            },
        ),
        (
            "E242",
            "a,	b = 1, 2",
            {
                "title": f"{LINTER}: Run document formatting",
                "command": "editor.action.formatDocument",
            },
        ),
        (
            "E262",
            "a = 1  #This comment needs a space",
            {
                "title": f"{LINTER}: Run document formatting",
                "command": "editor.action.formatDocument",
            },
        ),
        (
            "E271",
            "from collections import    (namedtuple, defaultdict)",
            {
                "title": f"{LINTER}: Run document formatting",
                "command": "editor.action.formatDocument",
            },
        ),
        (
            "E272",
            "from collections import (namedtuple, defaultdict)     ",
            {
                "title": f"{LINTER}: Run document formatting",
                "command": "editor.action.formatDocument",
            },
        ),
        (
            "E273",
            "x = 1 in\t[1, 2, 3]",
            {
                "title": f"{LINTER}: Run document formatting",
                "command": "editor.action.formatDocument",
            },
        ),
        (
            "E274",
            "x = 1\tin [1, 2, 3]",
            {
                "title": f"{LINTER}: Run document formatting",
                "command": "editor.action.formatDocument",
            },
        ),
        (
            "E275",
            "from collections import(namedtuple, defaultdict)",
            {
                "title": f"{LINTER}: Run document formatting",
                "command": "editor.action.formatDocument",
            },
        ),
    ],
)
def test_command_code_action(code, contents, command):
    """Tests for code actions which run a command."""
    with utils.python_file(contents, TEST_FILE_PATH.parent) as temp_file:
        uri = utils.as_uri(os.fspath(temp_file))
        with session.LspSession() as ls_session:
            ls_session.initialize()

            ls_session.notify_did_open(
                {
                    "textDocument": {
                        "uri": uri,
                        "languageId": "python",
                        "version": 1,
                        "text": contents,
                    }
                }
            )

            diagnostics = [
                {
                    "range": {
                        "start": {"line": 0, "character": 0},
                        "end": {"line": 1, "character": 0},
                    },
                    "message": "",
                    "severity": 1,
                    "code": code,
                    "source": LINTER,
                }
            ]

            actual_code_actions = ls_session.text_document_code_action(
                {
                    "textDocument": {"uri": uri},
                    "range": {
                        "start": {"line": 0, "character": 0},
                        "end": {"line": 1, "character": 0},
                    },
                    "context": {"diagnostics": diagnostics},
                }
            )

            expected = {
                "title": command["title"],
                "kind": "quickfix",
                "diagnostics": diagnostics,
                "command": command,
            }

        assert_that(actual_code_actions, is_([expected]))
