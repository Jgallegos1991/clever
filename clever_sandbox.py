#!/usr/bin/env python3
"""
clever_sandbox.py — local, sandboxed Python executor for Clever.
Captures stdout/stderr and returns JSON-friendly results.
"""

import contextlib
import io
import traceback

SAFE_BUILTINS = {
    "print": print,
    "range": range,
    "len": len,
    "min": min,
    "max": max,
    "sum": sum,
    "enumerate": enumerate,
    "list": list,
    "dict": dict,
    "set": set,
    "tuple": tuple,
    "sorted": sorted,
    "zip": zip,
    "any": any,
    "all": all,
}


def run_snippet(code: str) -> dict:
    """
    Execute an arbitrary Python snippet in a restricted environment.

    Args:
        code (str): The Python code to execute.

    Returns:
        dict: A dictionary containing:
            - ok (bool): True if execution succeeded, False otherwise.
            - stdout (str): Captured standard output.
            - stderr (str): Captured standard error or traceback.
    """
    out, err = io.StringIO(), io.StringIO()
    sandbox_globals = {"__builtins__": SAFE_BUILTINS}
    try:
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            exec(compile(code, "<clever-sandbox>", "exec"), sandbox_globals, None)
        return {"ok": True, "stdout": out.getvalue(), "stderr": err.getvalue()}
    except Exception:
        return {"ok": False, "stdout": out.getvalue(), "stderr": traceback.format_exc()}
    finally:
        out.close()
        err.close()


if __name__ == "__main__":
    print("=== Clever Sandbox Interactive ===")
    print("Type Python code, or 'exit()' to quit.")
    while True:
        try:
            code = input(">>> ")
            if code.strip().lower() in ("exit()", "quit", "bye"):
                break
            res = run_snippet(code)
            if res["ok"]:
                print(res["stdout"].strip() or "[no output]")
            else:
                print("⚠️ Error:\n", res["stderr"])
        except KeyboardInterrupt:
            break
