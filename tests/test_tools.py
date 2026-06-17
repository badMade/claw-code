from __future__ import annotations

import unittest
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
from src.models import PortingBacklog, PortingModule
from src.permissions import ToolPermissionContext


class TestTools(unittest.TestCase):
    def test_load_tool_snapshot(self) -> None:
        tools = load_tool_snapshot()
        self.assertIsInstance(tools, tuple)
        self.assertTrue(len(tools) > 0)
        for tool in tools:
            self.assertIsInstance(tool, PortingModule)
            self.assertEqual(tool.status, "mirrored")

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

    @patch(
        "src.tools.PORTED_TOOLS",
        new=tuple(
            [
                PortingModule(
                    name="BashTool",
                    responsibility="Run bash commands",
                    source_hint="bash.py",
                    status="mirrored",
                ),
                PortingModule(
                    name="FileReadTool",
                    responsibility="Read files",
                    source_hint="file_read.py",
                    status="mirrored",
                ),
                PortingModule(
                    name="BashTool",
                    responsibility="Duplicate tool",
                    source_hint="bash2.py",
                    status="mirrored",
                ),
                PortingModule(
                    name="lowercase_tool",
                    responsibility="Lower case",
                    source_hint="lower.py",
                    status="mirrored",
                ),
            ]
        ),
    )
    def test_get_tool(self) -> None:
        from src.tools import PORTED_TOOLS

        first_tool = PORTED_TOOLS[0]
        second_tool = PORTED_TOOLS[1]
        dup_tool = PORTED_TOOLS[2]
        lower_tool = PORTED_TOOLS[3]

        # Exact match
        self.assertEqual(get_tool("BashTool"), first_tool)
        # Case-insensitive match for the first tool
        self.assertEqual(get_tool("bashtool"), first_tool)
        self.assertEqual(get_tool("BASHTOOL"), first_tool)

        # Exact match for second tool
        self.assertEqual(get_tool("FileReadTool"), second_tool)

        # Test duplicate resolution (should return first match)
        self.assertEqual(get_tool("bashtool"), first_tool)
        self.assertNotEqual(get_tool("bashtool"), dup_tool)

        # Match for lower_tool
        self.assertEqual(get_tool("lowercase_tool"), lower_tool)
        self.assertEqual(get_tool("LOWERCASE_TOOL"), lower_tool)

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

    @patch(
        "src.tools.PORTED_TOOLS",
        new=tuple(
            [
                PortingModule(
                    name="BashTool",
                    responsibility="Run bash commands",
                    source_hint="bash.py",
                    status="mirrored",
                ),
                PortingModule(
                    name="mcp_tool",
                    responsibility="MCP tool",
                    source_hint="mcp.py",
                    status="mirrored",
                ),
                PortingModule(
                    name="other_mcp",
                    responsibility="Another tool",
                    source_hint="mcp_hint.py",
                    status="mirrored",
                ),
                PortingModule(
                    name="OtherTool",
                    responsibility="Other tool",
                    source_hint="other.py",
                    status="mirrored",
                ),
            ]
        ),
    )
    def test_get_tools(self) -> None:
        from src.tools import PORTED_TOOLS

        # Default
        all_tools = get_tools()
        self.assertEqual(len(all_tools), len(PORTED_TOOLS))

        # simple_mode
        simple_tools = get_tools(simple_mode=True)
        simple_tool_names = {tool.name for tool in simple_tools}
        self.assertEqual(simple_tool_names, {"BashTool"})

        # include_mcp=False
        no_mcp_tools = get_tools(include_mcp=False)
        self.assertEqual(len(no_mcp_tools), 2)
        no_mcp_names = {tool.name for tool in no_mcp_tools}
        self.assertEqual(no_mcp_names, {"BashTool", "OtherTool"})

        # With permission context
        context = ToolPermissionContext.from_iterables(deny_names=["BashTool"])
        filtered = get_tools(permission_context=context)
        filtered_names = {tool.name for tool in filtered}
        self.assertNotIn("BashTool", filtered_names)
        self.assertEqual(len(filtered_names), len(PORTED_TOOLS) - 1)

    @patch(
        "src.tools.PORTED_TOOLS",
        new=tuple(
            [
                PortingModule(
                    name="BashTool",
                    responsibility="Run bash commands",
                    source_hint="bash.py",
                    status="mirrored",
                ),
                PortingModule(
                    name="FileReadTool",
                    responsibility="Read files",
                    source_hint="file_read.py",
                    status="mirrored",
                ),
                PortingModule(
                    name="SomeBashTool",
                    responsibility="Run more bash",
                    source_hint="some_bash.py",
                    status="mirrored",
                ),
            ]
        ),
    )
    def test_find_tools(self) -> None:
        from src.tools import PORTED_TOOLS

        tool = PORTED_TOOLS[0]

        # Find by exact name (case-insensitive)
        matches = find_tools("bashtool")
        self.assertIn(tool, matches)
        self.assertEqual(len(matches), 2)  # BashTool and SomeBashTool

        # Find by partial name
        matches = find_tools("bash")
        self.assertEqual(len(matches), 2)

        # Find by source_hint
        matches = find_tools("file_read")
        self.assertEqual(len(matches), 1)
        self.assertEqual(matches[0].name, "FileReadTool")

        # Limit
        limit = 1
        matches = find_tools("bash", limit=limit)
        self.assertEqual(len(matches), limit)
        self.assertEqual(matches[0].name, "BashTool")

    @patch(
        "src.tools.PORTED_TOOLS",
        new=tuple(
            [
                PortingModule(
                    name="BashTool",
                    responsibility="Run bash commands",
                    source_hint="bash.py",
                    status="mirrored",
                ),
            ]
        ),
    )
    def test_execute_tool(self) -> None:
        from src.tools import PORTED_TOOLS

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

    @patch(
        "src.tools.PORTED_TOOLS",
        new=tuple(
            [
                PortingModule(
                    name="BashTool",
                    responsibility="Run bash commands",
                    source_hint="bash.py",
                    status="mirrored",
                ),
                PortingModule(
                    name="FileReadTool",
                    responsibility="Read files",
                    source_hint="file_read.py",
                    status="mirrored",
                ),
            ]
        ),
    )
    def test_render_tool_index(self) -> None:
        from src.tools import PORTED_TOOLS

        # No query
        output = render_tool_index(limit=5)
        self.assertIn(f"Tool entries: {len(PORTED_TOOLS)}", output)
        self.assertIn("BashTool", output)
        self.assertIn("FileReadTool", output)

        # With query
        tool = PORTED_TOOLS[0]
        output = render_tool_index(query=tool.name)
        self.assertIn(f"Filtered by: {tool.name}", output)
        self.assertIn(tool.name, output)
        self.assertNotIn("FileReadTool", output)


if __name__ == "__main__":
    unittest.main()
