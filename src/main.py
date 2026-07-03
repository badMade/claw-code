from __future__ import annotations

import argparse

from .bootstrap_graph import build_bootstrap_graph
from .command_graph import build_command_graph
from .commands import execute_command, get_command, get_commands, render_command_index
from .direct_modes import run_deep_link, run_direct_connect
from .parity_audit import run_parity_audit
from .permissions import ToolPermissionContext
from .port_manifest import build_port_manifest
from .query_engine import QueryEnginePort
from .remote_runtime import run_remote_mode, run_ssh_mode, run_teleport_mode
from .runtime import PortRuntime
from .session_store import load_session
from .setup import run_setup
from .tool_pool import assemble_tool_pool
from .tools import execute_tool, get_tool, get_tools, render_tool_index


def handle_summary(args: argparse.Namespace) -> int:
    manifest = build_port_manifest()
    print(QueryEnginePort(manifest).render_summary())
    return 0

def _setup_summary_parser(subparsers: argparse._SubParsersAction) -> None:
    parser = subparsers.add_parser('summary', help='render a Markdown summary of the Python porting workspace')
    parser.set_defaults(func=handle_summary)

def handle_manifest(args: argparse.Namespace) -> int:
    manifest = build_port_manifest()
    print(manifest.to_markdown())
    return 0

def _setup_manifest_parser(subparsers: argparse._SubParsersAction) -> None:
    parser = subparsers.add_parser('manifest', help='print the current Python workspace manifest')
    parser.set_defaults(func=handle_manifest)

def handle_parity_audit(args: argparse.Namespace) -> int:
    print(run_parity_audit().to_markdown())
    return 0

def _setup_parity_audit_parser(subparsers: argparse._SubParsersAction) -> None:
    parser = subparsers.add_parser('parity-audit', help='compare the Python workspace against the local ignored TypeScript archive when available')
    parser.set_defaults(func=handle_parity_audit)

def handle_setup_report(args: argparse.Namespace) -> int:
    print(run_setup().as_markdown())
    return 0

def _setup_setup_report_parser(subparsers: argparse._SubParsersAction) -> None:
    parser = subparsers.add_parser('setup-report', help='render the startup/prefetch setup report')
    parser.set_defaults(func=handle_setup_report)

def handle_command_graph(args: argparse.Namespace) -> int:
    print(build_command_graph().as_markdown())
    return 0

def _setup_command_graph_parser(subparsers: argparse._SubParsersAction) -> None:
    parser = subparsers.add_parser('command-graph', help='show command graph segmentation')
    parser.set_defaults(func=handle_command_graph)

def handle_tool_pool(args: argparse.Namespace) -> int:
    print(assemble_tool_pool().as_markdown())
    return 0

def _setup_tool_pool_parser(subparsers: argparse._SubParsersAction) -> None:
    parser = subparsers.add_parser('tool-pool', help='show assembled tool pool with default settings')
    parser.set_defaults(func=handle_tool_pool)

def handle_bootstrap_graph(args: argparse.Namespace) -> int:
    print(build_bootstrap_graph().as_markdown())
    return 0

def _setup_bootstrap_graph_parser(subparsers: argparse._SubParsersAction) -> None:
    parser = subparsers.add_parser('bootstrap-graph', help='show the mirrored bootstrap/runtime graph stages')
    parser.set_defaults(func=handle_bootstrap_graph)

def handle_subsystems(args: argparse.Namespace) -> int:
    manifest = build_port_manifest()
    for subsystem in manifest.top_level_modules[: args.limit]:
        print(f'{subsystem.name}\t{subsystem.file_count}\t{subsystem.notes}')
    return 0

def _setup_subsystems_parser(subparsers: argparse._SubParsersAction) -> None:
    parser = subparsers.add_parser('subsystems', help='list the current Python modules in the workspace')
    parser.add_argument('--limit', type=int, default=32)
    parser.set_defaults(func=handle_subsystems)

def handle_commands(args: argparse.Namespace) -> int:
    if args.query:
        print(render_command_index(limit=args.limit, query=args.query))
    else:
        commands = get_commands(include_plugin_commands=not args.no_plugin_commands, include_skill_commands=not args.no_skill_commands)
        output_lines = [f'Command entries: {len(commands)}', '']
        output_lines.extend(f'- {module.name} — {module.source_hint}' for module in commands[: args.limit])
        print('\n'.join(output_lines))
    return 0

def _setup_commands_parser(subparsers: argparse._SubParsersAction) -> None:
    parser = subparsers.add_parser('commands', help='list mirrored command entries from the archived snapshot')
    parser.add_argument('--limit', type=int, default=20)
    parser.add_argument('--query')
    parser.add_argument('--no-plugin-commands', action='store_true')
    parser.add_argument('--no-skill-commands', action='store_true')
    parser.set_defaults(func=handle_commands)

def handle_tools(args: argparse.Namespace) -> int:
    if args.query:
        print(render_tool_index(limit=args.limit, query=args.query))
    else:
        permission_context = ToolPermissionContext.from_iterables(args.deny_tool, args.deny_prefix)
        tools = get_tools(simple_mode=args.simple_mode, include_mcp=not args.no_mcp, permission_context=permission_context)
        output_lines = [f'Tool entries: {len(tools)}', '']
        output_lines.extend(f'- {module.name} — {module.source_hint}' for module in tools[: args.limit])
        print('\n'.join(output_lines))
    return 0

def _setup_tools_parser(subparsers: argparse._SubParsersAction) -> None:
    parser = subparsers.add_parser('tools', help='list mirrored tool entries from the archived snapshot')
    parser.add_argument('--limit', type=int, default=20)
    parser.add_argument('--query')
    parser.add_argument('--simple-mode', action='store_true')
    parser.add_argument('--no-mcp', action='store_true')
    parser.add_argument('--deny-tool', action='append', default=[])
    parser.add_argument('--deny-prefix', action='append', default=[])
    parser.set_defaults(func=handle_tools)

def handle_route(args: argparse.Namespace) -> int:
    matches = PortRuntime().route_prompt(args.prompt, limit=args.limit)
    if not matches:
        print('No mirrored command/tool matches found.')
        return 0
    for match in matches:
        print(f'{match.kind}\t{match.name}\t{match.score}\t{match.source_hint}')
    return 0

def _setup_route_parser(subparsers: argparse._SubParsersAction) -> None:
    parser = subparsers.add_parser('route', help='route a prompt across mirrored command/tool inventories')
    parser.add_argument('prompt')
    parser.add_argument('--limit', type=int, default=5)
    parser.set_defaults(func=handle_route)

def handle_bootstrap(args: argparse.Namespace) -> int:
    print(PortRuntime().bootstrap_session(args.prompt, limit=args.limit).as_markdown())
    return 0

def _setup_bootstrap_parser(subparsers: argparse._SubParsersAction) -> None:
    parser = subparsers.add_parser('bootstrap', help='build a runtime-style session report from the mirrored inventories')
    parser.add_argument('prompt')
    parser.add_argument('--limit', type=int, default=5)
    parser.set_defaults(func=handle_bootstrap)

def handle_turn_loop(args: argparse.Namespace) -> int:
    results = PortRuntime().run_turn_loop(args.prompt, limit=args.limit, max_turns=args.max_turns, structured_output=args.structured_output)
    for idx, result in enumerate(results, start=1):
        print(f'## Turn {idx}')
        print(result.output)
        print(f'stop_reason={result.stop_reason}')
    return 0

def _setup_turn_loop_parser(subparsers: argparse._SubParsersAction) -> None:
    parser = subparsers.add_parser('turn-loop', help='run a small stateful turn loop for the mirrored runtime')
    parser.add_argument('prompt')
    parser.add_argument('--limit', type=int, default=5)
    parser.add_argument('--max-turns', type=int, default=3)
    parser.add_argument('--structured-output', action='store_true')
    parser.set_defaults(func=handle_turn_loop)

def handle_flush_transcript(args: argparse.Namespace) -> int:
    engine = QueryEnginePort.from_workspace()
    engine.submit_message(args.prompt)
    path = engine.persist_session()
    print(path)
    print(f'flushed={engine.transcript_store.flushed}')
    return 0

def _setup_flush_transcript_parser(subparsers: argparse._SubParsersAction) -> None:
    parser = subparsers.add_parser('flush-transcript', help='persist and flush a temporary session transcript')
    parser.add_argument('prompt')
    parser.set_defaults(func=handle_flush_transcript)

def handle_load_session(args: argparse.Namespace) -> int:
    session = load_session(args.session_id)
    print(f'{session.session_id}\n{len(session.messages)} messages\nin={session.input_tokens} out={session.output_tokens}')
    return 0

def _setup_load_session_parser(subparsers: argparse._SubParsersAction) -> None:
    parser = subparsers.add_parser('load-session', help='load a previously persisted session')
    parser.add_argument('session_id')
    parser.set_defaults(func=handle_load_session)

def handle_remote_mode(args: argparse.Namespace) -> int:
    print(run_remote_mode(args.target).as_text())
    return 0

def _setup_remote_mode_parser(subparsers: argparse._SubParsersAction) -> None:
    parser = subparsers.add_parser('remote-mode', help='simulate remote-control runtime branching')
    parser.add_argument('target')
    parser.set_defaults(func=handle_remote_mode)

def handle_ssh_mode(args: argparse.Namespace) -> int:
    print(run_ssh_mode(args.target).as_text())
    return 0

def _setup_ssh_mode_parser(subparsers: argparse._SubParsersAction) -> None:
    parser = subparsers.add_parser('ssh-mode', help='simulate SSH runtime branching')
    parser.add_argument('target')
    parser.set_defaults(func=handle_ssh_mode)

def handle_teleport_mode(args: argparse.Namespace) -> int:
    print(run_teleport_mode(args.target).as_text())
    return 0

def _setup_teleport_mode_parser(subparsers: argparse._SubParsersAction) -> None:
    parser = subparsers.add_parser('teleport-mode', help='simulate teleport runtime branching')
    parser.add_argument('target')
    parser.set_defaults(func=handle_teleport_mode)

def handle_direct_connect_mode(args: argparse.Namespace) -> int:
    print(run_direct_connect(args.target).as_text())
    return 0

def _setup_direct_connect_mode_parser(subparsers: argparse._SubParsersAction) -> None:
    parser = subparsers.add_parser('direct-connect-mode', help='simulate direct-connect runtime branching')
    parser.add_argument('target')
    parser.set_defaults(func=handle_direct_connect_mode)

def handle_deep_link_mode(args: argparse.Namespace) -> int:
    print(run_deep_link(args.target).as_text())
    return 0

def _setup_deep_link_mode_parser(subparsers: argparse._SubParsersAction) -> None:
    parser = subparsers.add_parser('deep-link-mode', help='simulate deep-link runtime branching')
    parser.add_argument('target')
    parser.set_defaults(func=handle_deep_link_mode)

def handle_show_command(args: argparse.Namespace) -> int:
    module = get_command(args.name)
    if module is None:
        print(f'Command not found: {args.name}')
        return 1
    print('\n'.join([module.name, module.source_hint, module.responsibility]))
    return 0

def _setup_show_command_parser(subparsers: argparse._SubParsersAction) -> None:
    parser = subparsers.add_parser('show-command', help='show one mirrored command entry by exact name')
    parser.add_argument('name')
    parser.set_defaults(func=handle_show_command)

def handle_show_tool(args: argparse.Namespace) -> int:
    module = get_tool(args.name)
    if module is None:
        print(f'Tool not found: {args.name}')
        return 1
    print('\n'.join([module.name, module.source_hint, module.responsibility]))
    return 0

def _setup_show_tool_parser(subparsers: argparse._SubParsersAction) -> None:
    parser = subparsers.add_parser('show-tool', help='show one mirrored tool entry by exact name')
    parser.add_argument('name')
    parser.set_defaults(func=handle_show_tool)

def handle_exec_command(args: argparse.Namespace) -> int:
    result = execute_command(args.name, args.prompt)
    print(result.message)
    return 0 if result.handled else 1

def _setup_exec_command_parser(subparsers: argparse._SubParsersAction) -> None:
    parser = subparsers.add_parser('exec-command', help='execute a mirrored command shim by exact name')
    parser.add_argument('name')
    parser.add_argument('prompt')
    parser.set_defaults(func=handle_exec_command)

def handle_exec_tool(args: argparse.Namespace) -> int:
    result = execute_tool(args.name, args.payload)
    print(result.message)
    return 0 if result.handled else 1

def _setup_exec_tool_parser(subparsers: argparse._SubParsersAction) -> None:
    parser = subparsers.add_parser('exec-tool', help='execute a mirrored tool shim by exact name')
    parser.add_argument('name')
    parser.add_argument('payload')
    parser.set_defaults(func=handle_exec_tool)

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description='Python porting workspace for the Claude Code rewrite effort')
    subparsers = parser.add_subparsers(dest='command', required=True)

    _setup_summary_parser(subparsers)
    _setup_manifest_parser(subparsers)
    _setup_parity_audit_parser(subparsers)
    _setup_setup_report_parser(subparsers)
    _setup_command_graph_parser(subparsers)
    _setup_tool_pool_parser(subparsers)
    _setup_bootstrap_graph_parser(subparsers)
    _setup_subsystems_parser(subparsers)
    _setup_commands_parser(subparsers)
    _setup_tools_parser(subparsers)
    _setup_route_parser(subparsers)
    _setup_bootstrap_parser(subparsers)
    _setup_turn_loop_parser(subparsers)
    _setup_flush_transcript_parser(subparsers)
    _setup_load_session_parser(subparsers)
    _setup_remote_mode_parser(subparsers)
    _setup_ssh_mode_parser(subparsers)
    _setup_teleport_mode_parser(subparsers)
    _setup_direct_connect_mode_parser(subparsers)
    _setup_deep_link_mode_parser(subparsers)
    _setup_show_command_parser(subparsers)
    _setup_show_tool_parser(subparsers)
    _setup_exec_command_parser(subparsers)
    _setup_exec_tool_parser(subparsers)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if hasattr(args, 'func'):
        return args.func(args)

    parser.error(f'unknown command: {args.command}')
    return 2


if __name__ == '__main__':
    raise SystemExit(main())
