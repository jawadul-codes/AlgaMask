import importlib.util
from pathlib import Path
import socket

import pytest

spec = importlib.util.spec_from_file_location("dev_launcher", Path(__file__).resolve().parents[2] / "tools/dev.py")
dev = importlib.util.module_from_spec(spec)
spec.loader.exec_module(dev)


def test_busy_explicit_port_does_not_stop_owner():
    with socket.socket() as owner:
        owner.bind(("127.0.0.1", 0))
        owner.listen()
        port = owner.getsockname()[1]
        with pytest.raises(RuntimeError, match="no existing process was stopped"):
            dev.reserve_port(port, explicit=True)
        assert owner.fileno() >= 0


def test_automatic_selection_skips_busy_port():
    with socket.socket() as owner:
        owner.bind(("127.0.0.1", 0))
        owner.listen()
        port = owner.getsockname()[1]
        if port > 65505:
            pytest.skip("No nearby range available")
        with dev.reserve_port(port) as selected:
            assert selected.getsockname()[1] > port
            with pytest.raises(RuntimeError):
                dev.reserve_port(selected.getsockname()[1], explicit=True)


def test_web_server_keeps_reserved_socket_and_directory(tmp_path):
    sock = dev.reserve_port(31000)
    server = dev.web_server(sock, tmp_path)
    try:
        assert server.socket is sock
        assert server.RequestHandlerClass.keywords["directory"] == str(tmp_path)
    finally:
        server.server_close()


@pytest.mark.parametrize("port", ["0", "80", "65536"])
def test_invalid_ports(port):
    with pytest.raises(dev.argparse.ArgumentTypeError):
        dev.port_number(port)


def test_backend_exit_fails_fast():
    class Exited:
        def poll(self): return 1
    with pytest.raises(RuntimeError, match="Backend exited"):
        dev.wait_ready("http://127.0.0.1:1", Exited(), timeout=1)
