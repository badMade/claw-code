from __future__ import annotations

import argparse

from .bootstrap_graph import build_bootstrap_graph
from .command_graph import build_command_graph
from .commands import execute_command, get_command, get_commands, render_command_index
from .direct_modes import run_deep_link, run_direct_connect
from .parity_audit import run_parity_audit
from .permissions import ToolPermissionContext
from .port_manifest import PortManifest, build_port_manifest
from .query_engine import QueryEnginePort
from .remote_runtime import run_remote_mode, run_ssh_mode, run_teleport_mode
from .runtime import PortRuntime
from .session_store import load_session
from .setup import run_setup
from .tool_pool import assemble_tool_pool
from .tools import execute_tool, get_tool, get_tools, render_tool_index


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Python porting workspace for the Claude Code rewrite effort"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser(
        "summary", help="render a Markdown summary of the Python porting workspace"
    )
    subparsers.add_parser(
        "manifest", help="print the current Python workspace manifest"
    )
    subparsers.add_parser(
        "parity-audit",
        help="compare the Python workspace against the local ignored TypeScript archive when available",
    )
    subparsers.add_parser(
        "setup-report", help="render the startup/prefetch setup report"
    )
    subparsers.add_parser("command-graph", help="show command graph segmentation")
    subparsers.add_parser(
        "tool-pool", help="show assembled tool pool with default settings"
    )
    subparsers.add_parser(
        "bootstrap-graph", help="show the mirrored bootstrap/runtime graph stages"
    )
    list_parser = subparsers.add_parser(
        "subsystems", help="list the current Python modules in the workspace"
    )
    list_parser.add_argument("--limit", type=int, default=32)

    commands_parser = subparsers.add_parser(
        "commands", help="list mirrored command entries from the archived snapshot"
    )
    commands_parser.add_argument("--limit", type=int, default=20)
    commands_parser.add_argument("--query")
    commands_parser.add_argument("--no-plugin-commands", action="store_true")
    commands_parser.add_argument("--no-skill-commands", action="store_true")

    tools_parser = subparsers.add_parser(
        "tools", help="list mirrored tool entries from the archived snapshot"
    )
    tools_parser.add_argument("--limit", type=int, default=20)
    tools_parser.add_argument("--query")
    tools_parser.add_argument("--simple-mode", action="store_true")
    tools_parser.add_argument("--no-mcp", action="store_true")
    tools_parser.add_argument("--deny-tool", action="append", default=[])
    tools_parser.add_argument("--deny-prefix", action="append", default=[])

    route_parser = subparsers.add_parser(
        "route", help="route a prompt across mirrored command/tool inventories"
    )
    route_parser.add_argument("prompt")
    route_parser.add_argument("--limit", type=int, default=5)

    bootstrap_parser = subparsers.add_parser(
        "bootstrap",
        help="build a runtime-style session report from the mirrored inventories",
    )
    bootstrap_parser.add_argument("prompt")
    bootstrap_parser.add_argument("--limit", type=int, default=5)

    loop_parser = subparsers.add_parser(
        "turn-loop", help="run a small stateful turn loop for the mirrored runtime"
    )
    loop_parser.add_argument("prompt")
    loop_parser.add_argument("--limit", type=int, default=5)
    loop_parser.add_argument("--max-turns", type=int, default=3)
    loop_parser.add_argument("--structured-output", action="store_true")

    flush_parser = subparsers.add_parser(
        "flush-transcript", help="persist and flush a temporary session transcript"
    )
    flush_parser.add_argument("prompt")

    load_session_parser = subparsers.add_parser(
        "load-session", help="load a previously persisted session"
    )
    load_session_parser.add_argument("session_id")

    remote_parser = subparsers.add_parser(
        "remote-mode", help="simulate remote-control runtime branching"
    )
    remote_parser.add_argument("target")
    ssh_parser = subparsers.add_parser(
        "ssh-mode", help="simulate SSH runtime branching"
    )
    ssh_parser.add_argument("target")
    teleport_parser = subparsers.add_parser(
        "teleport-mode", help="simulate teleport runtime branching"
    )
    teleport_parser.add_argument("target")
    direct_parser = subparsers.add_parser(
        "direct-connect-mode", help="simulate direct-connect runtime branching"
    )
    direct_parser.add_argument("target")
    deep_link_parser = subparsers.add_parser(
        "deep-link-mode", help="simulate deep-link runtime branching"
    )
    deep_link_parser.add_argument("target")

    show_command = subparsers.add_parser(
        "show-command", help="show one mirrored command entry by exact name"
    )
    show_command.add_argument("name")
    show_tool = subparsers.add_parser(
        "show-tool", help="show one mirrored tool entry by exact name"
    )
    show_tool.add_argument("name")

    exec_command_parser = subparsers.add_parser(
        "exec-command", help="execute a mirrored command shim by exact name"
    )
    exec_command_parser.add_argument("name")
    exec_command_parser.add_argument("prompt")

    exec_tool_parser = subparsers.add_parser(
        "exec-tool", help="execute a mirrored tool shim by exact name"
    )
    exec_tool_parser.add_argument("name")
    exec_tool_parser.add_argument("payload")
    return parser


def _handle_summary(args: argparse.Namespace, manifest: PortManifest) -> int:
    print(QueryEnginePort(manifest).render_summary())
    return 0


def _handle_manifest(args: argparse.Namespace, manifest: PortManifest) -> int:
    print(manifest.to_markdown())
    return 0


def _handle_parity_audit(args: argparse.Namespace, manifest: PortManifest) -> int:
    print(run_parity_audit().to_markdown())
    return 0


def _handle_setup_report(args: argparse.Namespace, manifest: PortManifest) -> int:
    print(run_setup().as_markdown())
    return 0


def _handle_command_graph(args: argparse.Namespace, manifest: PortManifest) -> int:
    print(build_command_graph().as_markdown())
    return 0


def _handle_tool_pool(args: argparse.Namespace, manifest: PortManifest) -> int:
    print(assemble_tool_pool().as_markdown())
    return 0


def _handle_bootstrap_graph(args: argparse.Namespace, manifest: PortManifest) -> int:
    print(build_bootstrap_graph().as_markdown())
    return 0


def _handle_subsystems(args: argparse.Namespace, manifest: PortManifest) -> int:
    for subsystem in manifest.top_level_modules[: args.limit]:
        print(f"{subsystem.name}\t{subsystem.file_count}\t{subsystem.notes}")
    return 0


def _handle_commands(args: argparse.Namespace, manifest: PortManifest) -> int:
    if args.query:
        print(render_command_index(limit=args.limit, query=args.query))
    else:
        commands = get_commands(
            include_plugin_commands=not args.no_plugin_commands,
            include_skill_commands=not args.no_skill_commands,
        )
        output_lines = [f"Command entries: {len(commands)}", ""]
        output_lines.extend(
            f"- {module.name} — {module.source_hint}"
            for module in commands[: args.limit]
        )
        print("\n".join(output_lines))
    return 0


def _handle_tools(args: argparse.Namespace, manifest: PortManifest) -> int:
    if args.query:
        print(render_tool_index(limit=args.limit, query=args.query))
    else:
        permission_context = ToolPermissionContext.from_iterables(
            args.deny_tool, args.deny_prefix
        )
        tools = get_tools(
            simple_mode=args.simple_mode,
            include_mcp=not args.no_mcp,
            permission_context=permission_context,
        )
        output_lines = [f"Tool entries: {len(tools)}", ""]
        output_lines.extend(
            f"- {module.name} — {module.source_hint}" for module in tools[: args.limit]
        )
        print("\n".join(output_lines))
    return 0


def _handle_route(args: argparse.Namespace, manifest: PortManifest) -> int:
    matches = PortRuntime().route_prompt(args.prompt, limit=args.limit)
    if not matches:
        print("No mirrored command/tool matches found.")
        return 0
    for match in matches:
        print(f"{match.kind}\t{match.name}\t{match.score}\t{match.source_hint}")
    return 0


def _handle_bootstrap(args: argparse.Namespace, manifest: PortManifest) -> int:
    print(PortRuntime().bootstrap_session(args.prompt, limit=args.limit).as_markdown())
    return 0


def _handle_turn_loop(args: argparse.Namespace, manifest: PortManifest) -> int:
    results = PortRuntime().run_turn_loop(
        args.prompt,
        limit=args.limit,
        max_turns=args.max_turns,
        structured_output=args.structured_output,
    )
    for idx, result in enumerate(results, start=1):
        print(f"## Turn {idx}")
        print(result.output)
        print(f"stop_reason={result.stop_reason}")
    return 0


def _handle_flush_transcript(args: argparse.Namespace, manifest: PortManifest) -> int:
    engine = QueryEnginePort.from_workspace()
    engine.submit_message(args.prompt)
    path = engine.persist_session()
    print(path)
    print(f"flushed={engine.transcript_store.flushed}")
    return 0


def _handle_load_session(args: argparse.Namespace, manifest: PortManifest) -> int:
    session = load_session(args.session_id)
    print(
        f"{session.session_id}\n{len(session.messages)} messages\nin={session.input_tokens} out={session.output_tokens}"
    )
    return 0


def _handle_remote_mode(args: argparse.Namespace, manifest: PortManifest) -> int:
    print(run_remote_mode(args.target).as_text())
    return 0


def _handle_ssh_mode(args: argparse.Namespace, manifest: PortManifest) -> int:
    print(run_ssh_mode(args.target).as_text())
    return 0


def _handle_teleport_mode(args: argparse.Namespace, manifest: PortManifest) -> int:
    print(run_teleport_mode(args.target).as_text())
    return 0


def _handle_direct_connect_mode(
    args: argparse.Namespace, manifest: PortManifest
) -> int:
    print(run_direct_connect(args.target).as_text())
    return 0


def _handle_deep_link_mode(args: argparse.Namespace, manifest: PortManifest) -> int:
    print(run_deep_link(args.target).as_text())
    return 0


def _handle_show_command(args: argparse.Namespace, manifest: PortManifest) -> int:
    module = get_command(args.name)
    if module is None:
        print(f"Command not found: {args.name}")
        return 1
    print("\n".join([module.name, module.source_hint, module.responsibility]))
    return 0


def _handle_show_tool(args: argparse.Namespace, manifest: PortManifest) -> int:
    module = get_tool(args.name)
    if module is None:
        print(f"Tool not found: {args.name}")
        return 1
    print("\n".join([module.name, module.source_hint, module.responsibility]))
    return 0


def _handle_exec_command(args: argparse.Namespace, manifest: PortManifest) -> int:
    result = execute_command(args.name, args.prompt)
    print(result.message)
    return 0 if result.handled else 1


def _handle_exec_tool(args: argparse.Namespace, manifest: PortManifest) -> int:
    result = execute_tool(args.name, args.payload)
    print(result.message)
    return 0 if result.handled else 1


COMMAND_HANDLERS = {
    "summary": _handle_summary,
    "manifest": _handle_manifest,
    "parity-audit": _handle_parity_audit,
    "setup-report": _handle_setup_report,
    "command-graph": _handle_command_graph,
    "tool-pool": _handle_tool_pool,
    "bootstrap-graph": _handle_bootstrap_graph,
    "subsystems": _handle_subsystems,
    "commands": _handle_commands,
    "tools": _handle_tools,
    "route": _handle_route,
    "bootstrap": _handle_bootstrap,
    "turn-loop": _handle_turn_loop,
    "flush-transcript": _handle_flush_transcript,
    "load-session": _handle_load_session,
    "remote-mode": _handle_remote_mode,
    "ssh-mode": _handle_ssh_mode,
    "teleport-mode": _handle_teleport_mode,
    "direct-connect-mode": _handle_direct_connect_mode,
    "deep-link-mode": _handle_deep_link_mode,
    "show-command": _handle_show_command,
    "show-tool": _handle_show_tool,
    "exec-command": _handle_exec_command,
    "exec-tool": _handle_exec_tool,
}


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    manifest = build_port_manifest()

    handler = COMMAND_HANDLERS.get(args.command)
    if handler:
        return handler(args, manifest)

    parser.error(f"unknown command: {args.command}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
