# src/core/hermes.py
"""
Hermes Agent IPC client for Hermes Toolkit.
"""

import json
import subprocess
import socket
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass


@dataclass
class HermesStatus:
    """Hermes system status."""
    running: bool
    version: str
    uptime: str
    connected_platforms: List[str]
    mcp_services: List[Dict[str, str]]


class HermesClient:
    """
    Client for communicating with Hermes Agent.

    Supports both CLI and socket-based IPC.
    """

    def __init__(self, hermes_dir: Optional[str] = None):
        if hermes_dir:
            self._hermes_dir = Path(hermes_dir)
        else:
            self._hermes_dir = Path.home() / '.hermes'

        self._socket_path = self._hermes_dir / 'hermes.sock'
        self._cli_path = self._find_hermes_cli()

    def _find_hermes_cli(self) -> Optional[str]:
        """Try to find hermes CLI executable."""
        possible_paths = [
            'hermes',
            '/usr/local/bin/hermes',
            str(Path.home() / '.local' / 'bin' / 'hermes'),
        ]

        for path in possible_paths:
            try:
                result = subprocess.run(
                    ['which', path] if path != 'hermes' else ['hermes'],
                    capture_output=True,
                    text=True,
                    timeout=5,
                )
                if result.returncode == 0:
                    return result.stdout.strip()
            except (subprocess.SubprocessError, FileNotFoundError):
                pass

        return None

    def is_running(self) -> bool:
        """Check if Hermes is running."""
        if self._socket_path.exists():
            try:
                sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
                sock.settimeout(1)
                sock.connect(str(self._socket_path))
                sock.close()
                return True
            except (socket.error, OSError):
                pass

        # Try CLI check
        if self._cli_path:
            try:
                result = subprocess.run(
                    [self._cli_path, 'status'],
                    capture_output=True,
                    text=True,
                    timeout=5,
                )
                return result.returncode == 0
            except subprocess.SubprocessError:
                pass

        return False

    def get_status(self) -> HermesStatus:
        """Get Hermes system status."""
        status = HermesStatus(
            running=False,
            version='unknown',
            uptime='unknown',
            connected_platforms=[],
            mcp_services=[],
        )

        # Try to get status from CLI
        if self._cli_path:
            try:
                result = subprocess.run(
                    [self._cli_path, 'status', '--json'],
                    capture_output=True,
                    text=True,
                    timeout=5,
                )
                if result.returncode == 0:
                    data = json.loads(result.stdout)
                    status.running = data.get('running', False)
                    status.version = data.get('version', 'unknown')
                    status.uptime = data.get('uptime', 'unknown')
                    status.connected_platforms = data.get('platforms', [])
                    status.mcp_services = data.get('mcp_services', [])
            except (subprocess.SubprocessError, json.JSONDecodeError):
                pass

        return status

    def reload_config(self) -> bool:
        """Reload Hermes configuration."""
        if self._cli_path:
            try:
                result = subprocess.run(
                    [self._cli_path, 'reload'],
                    capture_output=True,
                    text=True,
                    timeout=10,
                )
                return result.returncode == 0
            except subprocess.SubprocessError:
                pass
        return False

    def restart(self) -> bool:
        """Restart Hermes."""
        if self._cli_path:
            try:
                result = subprocess.run(
                    [self._cli_path, 'restart'],
                    capture_output=True,
                    text=True,
                    timeout=30,
                )
                return result.returncode == 0
            except subprocess.SubprocessError:
                pass
        return False

    def sync_data(self) -> bool:
        """Sync Hermes data."""
        if self._cli_path:
            try:
                result = subprocess.run(
                    [self._cli_path, 'sync'],
                    capture_output=True,
                    text=True,
                    timeout=30,
                )
                return result.returncode == 0
            except subprocess.SubprocessError:
                pass
        return False

    def execute_skill(self, skill_name: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Execute a skill with given parameters."""
        if self._cli_path:
            try:
                cmd = [self._cli_path, 'skill', 'run', skill_name]
                if params:
                    cmd.extend(['--params', json.dumps(params)])

                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=60,
                )

                return {
                    'success': result.returncode == 0,
                    'output': result.stdout,
                    'error': result.stderr,
                }
            except subprocess.SubprocessError as e:
                return {
                    'success': False,
                    'output': '',
                    'error': str(e),
                }

        return {
            'success': False,
            'output': '',
            'error': 'Hermes CLI not found',
        }

    def list_mcp_services(self) -> List[Dict[str, str]]:
        """List available MCP services."""
        status = self.get_status()
        return status.mcp_services

    def list_platforms(self) -> List[str]:
        """List connected platforms."""
        status = self.get_status()
        return status.connected_platforms
