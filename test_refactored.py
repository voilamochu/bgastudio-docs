import json
import logging
import sys
import types
import unittest

requests_stub = types.SimpleNamespace(
    Session=lambda: types.SimpleNamespace(headers={}, request=lambda *args, **kwargs: None),
    Response=object,
    exceptions=types.SimpleNamespace(
        Timeout=Exception,
        ConnectionError=Exception,
        RequestException=Exception,
    ),
)
sys.modules.setdefault("requests", requests_stub)

from common import StructuredJSONFormatter, canonicalize_url, should_ignore_url


class CanonicalizeUrlTests(unittest.TestCase):
    def test_index_php_title_collapses_to_short_url(self):
        self.assertEqual(
            canonicalize_url("https://en.doc.boardgamearena.com/index.php?title=Main_game_logic:_Game.php"),
            "https://en.doc.boardgamearena.com/Main_game_logic:_Game.php",
        )

    def test_fragment_and_duplicate_slashes_are_removed(self):
        self.assertEqual(
            canonicalize_url("https://en.doc.boardgamearena.com//Studio/#section"),
            "https://en.doc.boardgamearena.com/Studio",
        )

    def test_relative_urls_and_spaces_are_normalized(self):
        self.assertEqual(
            canonicalize_url("../My Page", "https://en.doc.boardgamearena.com/docs/Studio"),
            "https://en.doc.boardgamearena.com/My_Page",
        )


class IgnoreRuleTests(unittest.TestCase):
    def test_special_namespace_is_ignored(self):
        self.assertEqual(
            should_ignore_url("https://en.doc.boardgamearena.com/index.php?title=Special:RecentChanges"),
            (True, "namespace_special"),
        )

    def test_help_root_page_is_allowed(self):
        self.assertEqual(should_ignore_url("https://en.doc.boardgamearena.com/Help"), (False, ""))

    def test_action_query_is_ignored(self):
        self.assertEqual(
            should_ignore_url("https://en.doc.boardgamearena.com/Studio?action=edit"),
            (True, "action_edit"),
        )


class StructuredLoggingTests(unittest.TestCase):
    def test_json_formatter_outputs_expected_fields(self):
        formatter = StructuredJSONFormatter()
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname=__file__,
            lineno=1,
            msg="hello",
            args=(),
            exc_info=None,
        )
        record.title = "Studio"
        record.canonical_url = "https://en.doc.boardgamearena.com/Studio"
        record.depth = 0
        record.status = "success"
        record.elapsed = 1.5

        payload = json.loads(formatter.format(record))
        self.assertEqual(payload["message"], "hello")
        self.assertEqual(payload["title"], "Studio")
        self.assertEqual(payload["status"], "success")


if __name__ == "__main__":
    unittest.main()
