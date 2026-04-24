from __future__ import annotations

import unittest
import unittest.mock
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
    PORTED_TOOLS
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
            self.assertEqual(tool.status, 'mirrored')

    def test_build_tool_backlog(self) -> None:
        backlog = build_tool_backlog()
        self.assertIsInstance(backlog, PortingBacklog)
        self.assertEqual(backlog.title, 'Tool surface')
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




    @unittest.mock.patch('src.tools.PORTED_TOOLS')
    def test_get_tools_with_mocks(self, mock_ported_tools) -> None:
        mock_tools = (
            PortingModule(name="BashTool", responsibility="", source_hint="", status="mirrored"),
            PortingModule(name="FileReadTool", responsibility="", source_hint="", status="mirrored"),
            PortingModule(name="SomeMCPTool", responsibility="", source_hint="mcp", status="mirrored"),
            PortingModule(name="AnotherTool", responsibility="", source_hint="other", status="mirrored"),
            PortingModule(name="McpAuthTool", responsibility="", source_hint="other", status="mirrored"),
        )
        mock_ported_tools.__iter__.side_effect = lambda: iter(mock_tools)

        # Default
        all_tools = get_tools()
        self.assertEqual(len(all_tools), 5)

        # simple_mode
        simple_tools = get_tools(simple_mode=True)
        self.assertEqual({t.name for t in simple_tools}, {"BashTool", "FileReadTool"})

        # include_mcp=False
        no_mcp_tools = get_tools(include_mcp=False)
        self.assertEqual({t.name for t in no_mcp_tools}, {"BashTool", "FileReadTool", "AnotherTool"})

        # Permission Context
        context = ToolPermissionContext.from_iterables(deny_names=["AnotherTool"])
        filtered = get_tools(permission_context=context)
        self.assertEqual(len(filtered), 4)
        self.assertNotIn("AnotherTool", {t.name for t in filtered})

        # Combine simple_mode and permission_context
        filtered_simple = get_tools(simple_mode=True, permission_context=ToolPermissionContext.from_iterables(deny_names=["BashTool"]))
        self.assertEqual({t.name for t in filtered_simple}, {"FileReadTool"})

        # Context with prefix
        context_prefix = ToolPermissionContext.from_iterables(deny_prefixes=["Mcp"])
        no_mcp_prefix = get_tools(permission_context=context_prefix)
        self.assertEqual({t.name for t in no_mcp_prefix}, {"BashTool", "FileReadTool", "AnotherTool", "SomeMCPTool"})

        # Combine all
        all_filtered = get_tools(simple_mode=False, include_mcp=False, permission_context=context_prefix)
        self.assertEqual({t.name for t in all_filtered}, {"BashTool", "FileReadTool", "AnotherTool"})

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

if __name__ == '__main__':
    unittest.main()
