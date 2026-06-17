from __future__ import annotations

import unittest
from unittest import mock

from src.models import PortingModule
from src.permissions import ToolPermissionContext
from src.tool_pool import ToolPool, assemble_tool_pool


class TestToolPool(unittest.TestCase):
    def test_tool_pool_as_markdown(self) -> None:
        tools = tuple(
            PortingModule(
                name=f"Tool{i}",
                responsibility=f"Do {i}",
                source_hint=f"src_{i}",
                status="mirrored",
            )
            for i in range(20)
        )
        pool = ToolPool(tools=tools, simple_mode=True, include_mcp=False)
        markdown = pool.as_markdown()

        self.assertIn("# Tool Pool", markdown)
        self.assertIn("Simple mode: True", markdown)
        self.assertIn("Include MCP: False", markdown)
        self.assertIn("Tool count: 20", markdown)

        # Check that the first 15 tools are included
        for i in range(15):
            self.assertIn(f"- Tool{i} — src_{i}", markdown)

        # Check that tools after 15 are excluded
        for i in range(15, 20):
            self.assertNotIn(f"- Tool{i} — src_{i}", markdown)

    @mock.patch("src.tool_pool.get_tools")
    def test_assemble_tool_pool_default_args(
        self, mock_get_tools: mock.MagicMock
    ) -> None:
        mock_tools = (
            PortingModule(
                name="DefaultTool",
                responsibility="R",
                source_hint="S",
                status="mirrored",
            ),
        )
        mock_get_tools.return_value = mock_tools

        pool = assemble_tool_pool()

        mock_get_tools.assert_called_once_with(
            simple_mode=False, include_mcp=True, permission_context=None
        )

        self.assertEqual(pool.tools, mock_tools)
        self.assertFalse(pool.simple_mode)
        self.assertTrue(pool.include_mcp)

    @mock.patch("src.tool_pool.get_tools")
    def test_assemble_tool_pool_custom_args(
        self, mock_get_tools: mock.MagicMock
    ) -> None:
        mock_tools = (
            PortingModule(
                name="CustomTool",
                responsibility="R",
                source_hint="S",
                status="mirrored",
            ),
        )
        mock_get_tools.return_value = mock_tools

        # According to memory directives, instantiate real instance of ToolPermissionContext
        context = ToolPermissionContext(deny_names=frozenset(["test"]))

        pool = assemble_tool_pool(
            simple_mode=True, include_mcp=False, permission_context=context
        )

        mock_get_tools.assert_called_once_with(
            simple_mode=True, include_mcp=False, permission_context=context
        )

        self.assertEqual(pool.tools, mock_tools)
        self.assertTrue(pool.simple_mode)
        self.assertFalse(pool.include_mcp)


if __name__ == "__main__":
    unittest.main()
