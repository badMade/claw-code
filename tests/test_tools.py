from __future__ import annotations

import unittest
import json
from unittest.mock import patch
from src.tools import (
    load_tool_snapshot,
    build_tool_backlog,
    tool_names,
    get_tool,
    filter_tools_by_permission_context,
    get_tools,
    find_tools,
    execute_tool,
    render_tool_index,
    PORTED_TOOLS,
)
from src.models import PortingBacklog
from src.permissions import ToolPermissionContext


class TestTools(unittest.TestCase):
    def test_load_tool_snapshot_happy_path(self) -> None:
        load_tool_snapshot.cache_clear()
        mock_data = [
            {
                "name": "TestTool1",
                "responsibility": "Test resp 1",
                "source_hint": "hint1",
            },
            {
                "name": "TestTool2",
                "responsibility": "Test resp 2",
                "source_hint": "hint2",
            },
        ]
        with patch("pathlib.Path.read_text", return_value=json.dumps(mock_data)):
            tools = load_tool_snapshot()

            self.assertIsInstance(tools, tuple)
            self.assertEqual(len(tools), 2)
            self.assertEqual(tools[0].name, "TestTool1")
            self.assertEqual(tools[0].responsibility, "Test resp 1")
            self.assertEqual(tools[0].source_hint, "hint1")
            self.assertEqual(tools[0].status, "mirrored")

            self.assertEqual(tools[1].name, "TestTool2")
            self.assertEqual(tools[1].responsibility, "Test resp 2")
            self.assertEqual(tools[1].source_hint, "hint2")
            self.assertEqual(tools[1].status, "mirrored")
        load_tool_snapshot.cache_clear()

    def test_load_tool_snapshot_caching(self) -> None:
        load_tool_snapshot.cache_clear()
        mock_data = [
            {"name": "CacheTool", "responsibility": "resp", "source_hint": "hint"}
        ]

        with patch(
            "pathlib.Path.read_text", return_value=json.dumps(mock_data)
        ) as mock_read_text:
            # First call should read the file
            tools1 = load_tool_snapshot()
            self.assertEqual(len(tools1), 1)
            self.assertEqual(tools1[0].name, "CacheTool")
            mock_read_text.assert_called_once()

            # Second call should use cache
            tools2 = load_tool_snapshot()
            self.assertEqual(len(tools2), 1)
            self.assertIs(tools1, tools2)
            mock_read_text.assert_called_once()  # Call count should still be 1

        load_tool_snapshot.cache_clear()

    def test_load_tool_snapshot_file_not_found(self) -> None:
        load_tool_snapshot.cache_clear()
        with patch("pathlib.Path.read_text", side_effect=FileNotFoundError):
            with self.assertRaises(FileNotFoundError):
                load_tool_snapshot()
        load_tool_snapshot.cache_clear()

    def test_load_tool_snapshot_invalid_json(self) -> None:
        load_tool_snapshot.cache_clear()
        with patch("pathlib.Path.read_text", return_value="invalid json"):
            with self.assertRaises(json.JSONDecodeError):
                load_tool_snapshot()
        load_tool_snapshot.cache_clear()

    def test_load_tool_snapshot_missing_keys(self) -> None:
        load_tool_snapshot.cache_clear()
        # Missing 'responsibility' key
        mock_data = [{"name": "BadTool", "source_hint": "hint"}]
        with patch("pathlib.Path.read_text", return_value=json.dumps(mock_data)):
            with self.assertRaises(KeyError):
                load_tool_snapshot()
        load_tool_snapshot.cache_clear()

    def test_build_tool_backlog(self) -> None:
        backlog = build_tool_backlog()
        self.assertIsInstance(backlog, PortingBacklog)
        self.assertEqual(backlog.title, "Tool surface")
        self.assertEqual(len(backlog.modules), len(PORTED_TOOLS))
        self.assertEqual(backlog.modules, list(PORTED_TOOLS))

    def test_tool_names(self) -> None:
        names = tool_names()
        self.assertIsInstance(names, list)
        self.assertEqual(len(names), len(PORTED_TOOLS))
        self.assertEqual(names, [m.name for m in PORTED_TOOLS])

    def test_get_tool(self) -> None:
        if not PORTED_TOOLS:
            self.skipTest("No tools available in snapshot")

        first_tool = PORTED_TOOLS[0]
        # Exact match
        self.assertEqual(get_tool(first_tool.name), first_tool)
        # Case-insensitive match
        self.assertEqual(get_tool(first_tool.name.lower()), first_tool)
        self.assertEqual(get_tool(first_tool.name.upper()), first_tool)
        # Unknown tool
        self.assertIsNone(get_tool("NonExistentToolNamexyz123"))

    def test_filter_tools_by_permission_context(self) -> None:
        tools = PORTED_TOOLS[:5]
        # No context
        self.assertEqual(filter_tools_by_permission_context(tools, None), tools)

        # With context
        deny_name = tools[0].name
        context = ToolPermissionContext.from_iterables(deny_names=[deny_name])
        filtered = filter_tools_by_permission_context(tools, context)
        self.assertEqual(len(filtered), len(tools) - 1)
        self.assertNotIn(tools[0], filtered)

    def test_get_tools(self) -> None:
        # Default
        all_tools = get_tools()
        self.assertEqual(len(all_tools), len(PORTED_TOOLS))

        # simple_mode
        simple_mode_names = {"BashTool", "FileReadTool", "FileEditTool"}
        expected_simple_names = {
            t.name for t in PORTED_TOOLS if t.name in simple_mode_names
        }
        simple_tools = get_tools(simple_mode=True)
        simple_tool_names = {tool.name for tool in simple_tools}
        self.assertEqual(simple_tool_names, expected_simple_names)

        # include_mcp=False
        # First, find if there are any MCP tools to test the filter
        mcp_tools = [
            t
            for t in PORTED_TOOLS
            if "mcp" in t.name.lower() or "mcp" in t.source_hint.lower()
        ]
        if mcp_tools:
            no_mcp_tools = get_tools(include_mcp=False)
            self.assertTrue(len(no_mcp_tools) < len(PORTED_TOOLS))
            for tool in no_mcp_tools:
                self.assertNotIn("mcp", tool.name.lower())
                self.assertNotIn("mcp", tool.source_hint.lower())

        # With permission context
        if len(PORTED_TOOLS) > 0:
            deny_name = PORTED_TOOLS[0].name
            context = ToolPermissionContext.from_iterables(deny_names=[deny_name])
            filtered = get_tools(permission_context=context)
            self.assertNotIn(PORTED_TOOLS[0], filtered)

    def test_find_tools(self) -> None:
        if not PORTED_TOOLS:
            self.skipTest("No tools available in snapshot")

        tool = PORTED_TOOLS[0]
        # Find by name
        matches = find_tools(tool.name)
        self.assertIn(tool, matches)

        # Find by source_hint
        matches = find_tools(tool.source_hint)
        self.assertIn(tool, matches)

        # Limit
        limit = 2
        matches = find_tools("", limit=limit)
        self.assertLessEqual(len(matches), limit)

    def test_execute_tool(self) -> None:
        if not PORTED_TOOLS:
            self.skipTest("No tools available in snapshot")

        tool = PORTED_TOOLS[0]
        # Success
        execution = execute_tool(tool.name, "test payload")
        self.assertTrue(execution.handled)
        self.assertEqual(execution.name, tool.name)
        self.assertEqual(execution.source_hint, tool.source_hint)
        self.assertEqual(execution.payload, "test payload")
        self.assertIn(tool.name, execution.message)
        self.assertIn(tool.source_hint, execution.message)

        # Failure
        unknown_name = "UnknownToolNamexyz123"
        execution = execute_tool(unknown_name)
        self.assertFalse(execution.handled)
        self.assertEqual(execution.name, unknown_name)
        self.assertIn(f"Unknown mirrored tool: {unknown_name}", execution.message)

    def test_render_tool_index(self) -> None:
        # No query
        output = render_tool_index(limit=5)
        self.assertIn(f"Tool entries: {len(PORTED_TOOLS)}", output)

        # With query
        if not PORTED_TOOLS:
            self.skipTest("No tools available in snapshot")

        tool = PORTED_TOOLS[0]
        output = render_tool_index(query=tool.name)
        self.assertIn(f"Filtered by: {tool.name}", output)
        self.assertIn(tool.name, output)


if __name__ == "__main__":
    unittest.main()
