import select
import signal
import subprocess
import sys
import threading

ssh_process = None
should_exit = False
ssh_lock = threading.Lock()

ssh_path = "/usr/bin/ssh"


def start_ssh(cmd_args):
    global ssh_process
    print("[autossh] Starting SSH tunnel...")
    wrapped_args = [
        "-v",
        "-o",
        "ServerAliveInterval=5",
        "-o",
        "ServerAliveCountMax=3",
    ] + cmd_args
    with ssh_lock:
        ssh_process = subprocess.Popen(
            [ssh_path] + wrapped_args,
            stderr=subprocess.PIPE,
        )
    return ssh_process


def monitor_tunnel(cmd_args):
    """Monitor SSH process and restart whenever it exits unexpectedly."""
    global ssh_process, should_exit

    while not should_exit:
        with ssh_lock:
            process = ssh_process

        if process is None or process.poll() is not None:
            if not should_exit:
                print("[autossh] SSH process terminated, restarting...")
                start_ssh(cmd_args)

        try:
            select.select([], [], [], 1)
        except (OSError, ValueError):
            continue


def has_local_forward(args):
    """Detect whether command uses local forwarding (-L)."""
    for i, arg in enumerate(args):
        if arg == "-L" and i + 1 < len(args):
            return True
        if arg.startswith("-L") and len(arg) > 2:
            return True
    return False


def signal_handler(sig, frame):
    del sig, frame
    global should_exit
    print("\n[autossh] Caught interrupt. Exiting.")
    should_exit = True
    with ssh_lock:
        if ssh_process and ssh_process.poll() is None:
            ssh_process.terminate()


def main():
    global ssh_process
    args = sys.argv[1:]

    if not args:
        subprocess.run([ssh_path])
        return

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    if not has_local_forward(args):
        print("[autossh] Warning: No -L port detected. Running SSH without tunnel monitoring.")
        ssh_process = start_ssh(args)
        ssh_process.wait()
        return

    ssh_process = start_ssh(args)
    monitor_tunnel(args)


if __name__ == "__main__":
    main()
