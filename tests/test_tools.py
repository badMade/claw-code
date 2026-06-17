from __future__ import annotations

import unittest
from unittest import mock
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
        tools = (
            PortingModule(name='BashTool', responsibility='shell', source_hint='local', status='mirrored'),
            PortingModule(name='FileReadTool', responsibility='files', source_hint='local', status='mirrored'),
            PortingModule(name='AdminTool', responsibility='admin', source_hint='local', status='mirrored'),
        )
        # No context -> return all
        self.assertEqual(filter_tools_by_permission_context(tools, None), tools)

        # With context blocking one tool
        context = ToolPermissionContext.from_iterables(deny_names=['AdminTool'])
        filtered = filter_tools_by_permission_context(tools, context)
        self.assertEqual(len(filtered), 2)
        self.assertNotIn(tools[2], filtered)

        # Context blocking multiple/all tools
        context_all = ToolPermissionContext.from_iterables(deny_names=['BashTool', 'FileReadTool', 'AdminTool'])
        self.assertEqual(filter_tools_by_permission_context(tools, context_all), ())

    @mock.patch('src.tools.PORTED_TOOLS', new=(
            PortingModule(name='BashTool', responsibility='shell', source_hint='local', status='mirrored'),
            PortingModule(name='FileReadTool', responsibility='files', source_hint='local', status='mirrored'),
            PortingModule(name='SomeOtherTool', responsibility='misc', source_hint='local', status='mirrored'),
            PortingModule(name='mcp_server_tool', responsibility='mcp', source_hint='mcp server', status='mirrored'),
            PortingModule(name='NormalTool', responsibility='normal', source_hint='mcp hint', status='mirrored'),
        ))
    def test_get_tools(self) -> None:

        # Default: return all
        self.assertEqual(len(get_tools()), 5)

        # simple_mode=True: only 'BashTool', 'FileReadTool', 'FileEditTool'
        simple_tools = get_tools(simple_mode=True)
        self.assertEqual(len(simple_tools), 2)
        self.assertEqual({t.name for t in simple_tools}, {'BashTool', 'FileReadTool'})

        # include_mcp=False: drop 'mcp_server_tool' and 'NormalTool'
        no_mcp_tools = get_tools(include_mcp=False)
        self.assertEqual(len(no_mcp_tools), 3)
        self.assertEqual({t.name for t in no_mcp_tools}, {'BashTool', 'FileReadTool', 'SomeOtherTool'})

        # permission_context: block 'FileReadTool'
        context = ToolPermissionContext.from_iterables(deny_names=['FileReadTool'])
        filtered_tools = get_tools(permission_context=context)
        self.assertEqual(len(filtered_tools), 4)
        self.assertNotIn('FileReadTool', {t.name for t in filtered_tools})

        # All combined: simple_mode=True, include_mcp=False, block 'BashTool'
        context2 = ToolPermissionContext.from_iterables(deny_names=['BashTool'])
        combined_tools = get_tools(simple_mode=True, include_mcp=False, permission_context=context2)
        self.assertEqual(len(combined_tools), 1)
        self.assertEqual(combined_tools[0].name, 'FileReadTool')

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
