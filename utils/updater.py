import subprocess
import os

_update_status = {"up_to_date": True, "local": None, "remote": None, "updated": False, "error": None}

def is_git_repo():
    return os.path.isdir(".git")

def _run_git(args):
    return subprocess.run(["git"] + args, capture_output=True, text=True, check=False)

def check_for_updates(branch="dev"):
    global _update_status
    if not is_git_repo():
        _update_status["error"] = "Not a git repository"
        return _update_status

    _run_git(["fetch", "origin", branch])

    local = _run_git(["rev-parse", "HEAD"]).stdout.strip()
    remote = _run_git(["rev-parse", f"origin/{branch}"]).stdout.strip()

    _update_status.update({
        "local": local,
        "remote": remote,
        "up_to_date": (local == remote),
        "updated": False,
        "error": None
    })
    return _update_status

def do_update(branch="dev"):
    global _update_status
    res = _run_git(["pull", "origin", branch])
    if res.returncode == 0:
        _update_status["updated"] = True
    else:
        _update_status["error"] = res.stderr
    return _update_status

def auto_update(cfg):
    """Main entrypoint for startup. Respects config flags."""
    status = check_for_updates()
    if cfg.get("auto_update", False) and not status["up_to_date"]:
        do_update()
    return status

def get_status():
    return _update_status
