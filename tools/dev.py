"""One-command local development launcher. No third-party Python imports required."""
import argparse
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import json
import os
from pathlib import Path
import shutil
import signal
import socket
import subprocess
import sys
import tempfile
import threading
import time
from urllib.error import URLError
from urllib.request import ProxyHandler, build_opener

ROOT = Path(__file__).resolve().parents[1]


def port_number(value):
    number = int(value)
    if not 1024 <= number <= 65535:
        raise argparse.ArgumentTypeError("Choose a port between 1024 and 65535")
    return number


def reserve_port(preferred, *, explicit=False):
    """Keep the socket reserved so a port cannot be stolen between check and use."""
    for port in range(preferred, min(preferred + (1 if explicit else 30), 65536)):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            if sys.platform == "win32":
                # Windows SO_REUSEADDR allows a second bind to steal a live listener.
                # Exclusive use keeps an occupied port occupied. The listening socket
                # is closed before a restart, so the same port can be bound again.
                sock.setsockopt(socket.SOL_SOCKET, socket.SO_EXCLUSIVEADDRUSE, 1)
            else:
                # Permit immediate restart after an owned connection enters TIME_WAIT.
                # SO_REUSEPORT is deliberately not enabled: an active listener still wins.
                sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.bind(("127.0.0.1", port))
            sock.listen(128)
            return sock
        except OSError:
            sock.close()
    raise RuntimeError(f"Port {preferred} is unavailable" +
                       (". Choose another port; no existing process was stopped." if explicit
                        else " and no nearby free port was found. Use explicit port options."))


class LocalHandler(SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass

    def end_headers(self):
        self.send_header("Cache-Control", "no-store")
        super().end_headers()


def web_server(sock, directory):
    server = ThreadingHTTPServer(sock.getsockname(), partial(LocalHandler, directory=str(directory)),
                                 bind_and_activate=False)
    server.socket.close()
    server.socket = sock
    server.server_address = sock.getsockname()
    return server


def stop_child(process):
    if process.poll() is None:
        # Each child has its own group; never signal a process we did not launch.
        os.killpg(process.pid, signal.SIGTERM)
        try:
            process.wait(timeout=10)
        except subprocess.TimeoutExpired:
            os.killpg(process.pid, signal.SIGKILL)
            process.wait(timeout=5)


def wait_ready(base_url, process, timeout=180):
    opener = build_opener(ProxyHandler({}))
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if process.poll() is not None:
            raise RuntimeError("Backend exited before readiness. See backend.log.")
        try:
            with opener.open(base_url + "/rag/ready", timeout=2) as response:
                rag = json.load(response)
            with opener.open(base_url + "/storage/ready", timeout=2) as response:
                storage = json.load(response)
            if rag.get("status") == "ready" and storage.get("status") == "ready" and rag.get("development_only") is True:
                return rag
            raise RuntimeError("Backend readiness did not confirm development retrieval and storage.")
        except (URLError, TimeoutError):
            time.sleep(.5)
    raise RuntimeError("Backend readiness timed out. Check backend.log and the cached model; no mock fallback was used.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--api-port", type=port_number, help="Require this exact backend port")
    parser.add_argument("--web-port", type=port_number, help="Require this exact app port")
    args = parser.parse_args()
    children = []
    sockets = []
    server = None
    logs = []
    try:
        if os.name != "posix":
            raise RuntimeError("This launcher currently supports macOS/Linux. See README for manual startup.")
        python = ROOT / ".venv/bin/python"
        if not python.exists():
            raise RuntimeError("Missing .venv. From the repository root run: uv sync --locked --extra dev --extra rag")
        flutter = shutil.which("flutter")
        if not flutter:
            raise RuntimeError("Flutter is not on PATH. Add your installed Flutter SDK to this terminal's PATH.")
        api_socket = reserve_port(args.api_port or 8124, explicit=args.api_port is not None)
        sockets.append(api_socket)
        web_socket = reserve_port(args.web_port or 3001, explicit=args.web_port is not None)
        sockets.append(web_socket)
        api_url = f"http://127.0.0.1:{api_socket.getsockname()[1]}"
        web_url = f"http://127.0.0.1:{web_socket.getsockname()[1]}"
        sessions = ROOT / "var/dev"
        sessions.mkdir(parents=True, exist_ok=True)
        folder = Path(tempfile.mkdtemp(prefix="session-", dir=sessions))
        print(f"Logs and compiled app: {folder}\nBackend: {api_url}\nApp: {web_url}", flush=True)
        env = {**os.environ, "HF_HUB_OFFLINE": "1", "ALGAMASK_MODE": "development",
               "ALGAMASK_GENERATION_PROVIDER": "extractive"}
        # Retain documented dataset/index/database overrides, but anchor relative paths
        # to ROOT by launching from there. Do not download a model implicitly.
        backend_log = (folder / "backend.log").open("w")
        logs.append(backend_log)
        backend = subprocess.Popen([str(python), "-m", "uvicorn", "algamask.api:app",
                                    "--fd", str(api_socket.fileno())], cwd=ROOT, env=env,
                                   pass_fds=(api_socket.fileno(),), start_new_session=True,
                                   stdout=backend_log, stderr=subprocess.STDOUT)
        children.append(backend)
        api_socket.close()
        print("Checking local RAG and saved-run storage…", flush=True)
        ready = wait_ready(api_url, backend)
        print(f"Ready: {ready['dataset_version']} / {ready['index_version']}. Building Flutter…", flush=True)
        build_log = (folder / "flutter-build.log").open("w")
        logs.append(build_log)
        build_dir = folder / "web"
        build = subprocess.Popen([flutter, "build", "web", "--output", str(build_dir),
                                  f"--dart-define=API_BASE_URL={api_url}"], cwd=ROOT / "apps/flutter",
                                 stdout=build_log, stderr=subprocess.STDOUT, start_new_session=True)
        children.append(build)
        if build.wait() != 0:
            raise RuntimeError("Flutter build failed. See flutter-build.log.")
        if backend.poll() is not None:
            raise RuntimeError("Backend stopped during the build. See backend.log.")
        server = web_server(web_socket, build_dir)
        threading.Thread(target=server.serve_forever, daemon=True).start()
        print(f"\nAlgaMask is ready: {web_url}/\nAPI docs: {api_url}/docs\n"
              "Keep this terminal open. Ctrl+C stops only this launcher's services.\n"
              "After code changes, stop and rerun this command to rebuild.", flush=True)
        while backend.poll() is None:
            time.sleep(.5)
        raise RuntimeError("Backend stopped; shutting down this app server. See backend.log.")
    except KeyboardInterrupt:
        print("\nStopping this launcher's services. Saved runs and logs are retained.", flush=True)
        return 0
    except (OSError, RuntimeError, ValueError) as exc:
        print(f"Startup failed: {exc}", flush=True)
        return 1
    finally:
        if server:
            server.shutdown()
            server.server_close()
        for process in reversed(children):
            stop_child(process)
        for sock in sockets:
            sock.close()
        for handle in logs:
            handle.close()


if __name__ == "__main__":
    def terminate(signum, frame):
        raise KeyboardInterrupt
    signal.signal(signal.SIGTERM, terminate)
    raise SystemExit(main())
