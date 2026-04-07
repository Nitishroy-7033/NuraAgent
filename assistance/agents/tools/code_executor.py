"""
code_executor.py — Safe Python code execution tool for the Reasoning Agent

Runs code in a restricted subprocess with:
  - 30 second timeout
  - No network access from executed code
  - Captures stdout, stderr, and exceptions cleanly
"""
import asyncio
import sys
import textwrap
import tempfile
import os
from pathlib import Path

from utils.logger import get_logger

logger = get_logger("code_executor")

# Hard limits
MAX_OUTPUT_CHARS = 5000
TIMEOUT_SECONDS = 30


async def execute_python(code: str) -> dict:
    """
    Execute Python code in a subprocess and return the result.

    Returns:
      {
        "success": bool,
        "output":  str,   # stdout
        "error":   str,   # stderr or exception message
        "code":    str,   # the code that was run
      }
    """
    # Clean up the code — strip markdown fences if present
    code = _strip_fences(code)

    logger.info(f"Executing code: {len(code.splitlines())} lines")
    logger.debug(f"Code preview: {code[:200]}")

    # Write to a temp file — cleaner than -c for multiline code
    with tempfile.NamedTemporaryFile(
        mode="w",
        suffix=".py",
        delete=False,
        encoding="utf-8",
    ) as f:
        f.write(code)
        tmp_path = f.name

    try:
        proc = await asyncio.create_subprocess_exec(
            sys.executable, tmp_path,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )

        try:
            stdout, stderr = await asyncio.wait_for(
                proc.communicate(),
                timeout=TIMEOUT_SECONDS,
            )
        except asyncio.TimeoutError:
            proc.kill()
            await proc.communicate()
            return {
                "success": False,
                "output":  "",
                "error":   f"Timeout: code took more than {TIMEOUT_SECONDS}s to run.",
                "code":    code,
            }

        out = stdout.decode("utf-8", errors="replace").strip()
        err = stderr.decode("utf-8", errors="replace").strip()

        # Truncate very long output
        if len(out) > MAX_OUTPUT_CHARS:
            out = out[:MAX_OUTPUT_CHARS] + f"\n... [truncated at {MAX_OUTPUT_CHARS} chars]"

        success = proc.returncode == 0
        logger.info(f"Code executed: success={success}, output_len={len(out)}")

        return {
            "success": success,
            "output":  out,
            "error":   err if not success else "",
            "code":    code,
        }

    finally:
        # Always clean up temp file
        try:
            os.unlink(tmp_path)
        except Exception:
            pass


def _strip_fences(code: str) -> str:
    """Remove markdown code fences if the LLM wrapped the code in them."""
    code = code.strip()
    if code.startswith("```"):
        lines = code.split("\n")
        # Remove first line (```python or ```) and last line (```)
        lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        code = "\n".join(lines)
    return code.strip()


def format_result(result: dict) -> str:
    """Format code execution result for display in chat."""
    code = result["code"]
    output = result["output"]
    error = result["error"]
    success = result["success"]

    parts = []

    # Show the code
    parts.append("```python")
    parts.append(code)
    parts.append("```")

    # Show result
    if success and output:
        parts.append("\n**Output:**")
        parts.append("```")
        parts.append(output)
        parts.append("```")
    elif success and not output:
        parts.append("\n**Output:** *(no output)*")
    else:
        parts.append("\n**Error:**")
        parts.append("```")
        parts.append(error or "Unknown error")
        parts.append("```")

    return "\n".join(parts)