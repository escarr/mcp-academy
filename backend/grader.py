"""Grader: spawns the student's MCP server as a subprocess, talks JSON-RPC
over stdio, captures every message for the Protocol Inspector, then checks
whether the responses match each lesson's expectations.

We talk raw JSON-RPC (no SDK client) on purpose — it gives us perfect
visibility into the protocol, which is the whole point of the visualizer.

Supported `GraderStep.kind` values:
  initialize        Handshake.
  list_tools        Verifies tools/list output (tool name, annotations).
  call_tool         Calls a tool; verifies result text / structured / isError.
  list_resources    Verifies resources/list output.
  read_resource     Reads a resource; verifies content text / mimeType.
  list_resource_templates  Verifies resources/templates/list output.
  list_prompts      Verifies prompts/list output.
  get_prompt        Fetches a prompt; verifies messages.
  source_assert     Static check on the student's source code (regex / contains).
"""
from __future__ import annotations

import asyncio
import json
import os
import re
import shutil
import sys
import tempfile
from pathlib import Path
from typing import Any

from mcp.types import LATEST_PROTOCOL_VERSION

from lessons import LESSONS, GraderStep, Lesson

# Spawn student code with the same interpreter as the grader so the venv's
# `mcp` package is automatically available.
PYTHON_CMD = os.environ.get("MCP_TEACHER_PYTHON", sys.executable)
# Track whatever the SDK ships as latest — avoids drift as the SDK updates.
PROTOCOL_VERSION = LATEST_PROTOCOL_VERSION
TIMEOUT_PER_CALL = 8.0
TIMEOUT_TOTAL = 25.0


class GraderError(Exception):
    pass


class StdioMCPClient:
    """Minimal JSON-RPC 2.0 client over a subprocess's stdio."""

    def __init__(self):
        self.proc: asyncio.subprocess.Process | None = None
        self.trace: list[dict[str, Any]] = []
        self.stderr_buf: list[str] = []
        self._next_id = 0
        self._stderr_task: asyncio.Task | None = None
        self.source: str = ""
        self.workdir: Path | None = None

    async def spawn(self, code: str, workdir: Path) -> None:
        self.source = code
        self.workdir = workdir
        script = workdir / "server.py"
        script.write_text(code)
        self.proc = await asyncio.create_subprocess_exec(
            PYTHON_CMD, "-u", str(script),
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=str(workdir),
            env={**os.environ, "PYTHONUNBUFFERED": "1"},
        )
        self._stderr_task = asyncio.create_task(self._drain_stderr())

    async def _drain_stderr(self) -> None:
        assert self.proc and self.proc.stderr
        while True:
            line = await self.proc.stderr.readline()
            if not line:
                return
            try:
                self.stderr_buf.append(line.decode("utf-8", errors="replace").rstrip())
            except Exception:
                pass

    def _alloc_id(self) -> int:
        self._next_id += 1
        return self._next_id

    async def send(self, method: str, params: dict | None = None,
                   is_notification: bool = False) -> dict | None:
        assert self.proc and self.proc.stdin and self.proc.stdout
        msg: dict[str, Any] = {"jsonrpc": "2.0", "method": method}
        if params is not None:
            msg["params"] = params
        if not is_notification:
            msg["id"] = self._alloc_id()
        self.trace.append({"direction": "out", "message": msg})
        self.proc.stdin.write((json.dumps(msg) + "\n").encode())
        await self.proc.stdin.drain()
        if is_notification:
            return None
        return await self._await_response(msg["id"])

    async def _await_response(self, request_id: int) -> dict:
        assert self.proc and self.proc.stdout
        while True:
            try:
                raw = await asyncio.wait_for(
                    self.proc.stdout.readline(), timeout=TIMEOUT_PER_CALL
                )
            except asyncio.TimeoutError:
                raise GraderError(
                    f"Timed out waiting for a response to request #{request_id}. "
                    "Did your server crash? Check the stderr panel."
                )
            if not raw:
                raise GraderError(
                    "Server closed its stdout before responding. "
                    "Did it crash or exit early?"
                )
            line = raw.decode("utf-8", errors="replace").strip()
            if not line:
                continue
            try:
                resp = json.loads(line)
            except json.JSONDecodeError:
                self.trace.append({"direction": "log", "message": {"raw": line}})
                continue
            self.trace.append({"direction": "in", "message": resp})
            # Server-initiated request (has both `method` and `id` and no
            # `result`/`error`)? Respond on the client's behalf so tools that
            # use sampling/elicitation can run end-to-end.
            if (
                "method" in resp
                and "id" in resp
                and "result" not in resp
                and "error" not in resp
            ):
                await self._respond_to_server_request(resp)
                continue
            if resp.get("id") == request_id:
                return resp

    async def _respond_to_server_request(self, req: dict) -> None:
        """Mock client responses for server-initiated requests.

        Currently handles `sampling/createMessage` and `elicitation/create`,
        which lets W5.1 and W5.2 actually exercise their bidirectional
        features in the academy instead of being graded purely on source.
        """
        assert self.proc and self.proc.stdin
        method = req.get("method")
        req_id = req.get("id")
        if method == "sampling/createMessage":
            result: dict[str, Any] = {
                "model": "mcp-teacher-mock",
                "role": "assistant",
                "content": {
                    "type": "text",
                    "text": "Mock LLM reflection: keep eating those pellets!",
                },
                "stopReason": "endTurn",
            }
            msg = {"jsonrpc": "2.0", "id": req_id, "result": result}
        elif method == "elicitation/create":
            params = req.get("params") or {}
            schema = params.get("requestedSchema") or {}
            content = _stub_content_for_schema(schema)
            result = {"action": "accept", "content": content}
            msg = {"jsonrpc": "2.0", "id": req_id, "result": result}
        else:
            msg = {
                "jsonrpc": "2.0",
                "id": req_id,
                "error": {"code": -32601, "message": f"unknown method: {method}"},
            }
        self.trace.append({"direction": "out", "message": msg})
        self.proc.stdin.write((json.dumps(msg) + "\n").encode())
        await self.proc.stdin.drain()

    async def close(self) -> None:
        if not self.proc:
            return
        if self.proc.returncode is None:
            try:
                self.proc.terminate()
                await asyncio.wait_for(self.proc.wait(), timeout=2)
            except asyncio.TimeoutError:
                self.proc.kill()
                await self.proc.wait()
        if self._stderr_task:
            try:
                await asyncio.wait_for(self._stderr_task, timeout=0.5)
            except asyncio.TimeoutError:
                self._stderr_task.cancel()


# ---------- helpers ----------

def _stub_content_for_schema(schema: dict) -> dict:
    """Generate placeholder values matching a JSON Schema's required fields.

    Used by the mock elicitation responder so tools that call `ctx.elicit`
    receive a sensible canned answer instead of hanging.
    """
    props = (schema.get("properties") or {}) if isinstance(schema, dict) else {}
    required = schema.get("required") if isinstance(schema, dict) else None
    if not required:
        required = list(props.keys())
    out: dict[str, Any] = {}
    for name in required:
        p = props.get(name) or {}
        t = p.get("type")
        if t == "string":
            out[name] = f"stub-{name}"
        elif t in ("integer", "number"):
            out[name] = 1
        elif t == "boolean":
            out[name] = True
        elif t == "array":
            out[name] = []
        else:
            out[name] = None
    return out


def _text_blocks(content: list[dict]) -> str:
    parts = []
    for block in content or []:
        if block.get("type") == "text":
            parts.append(block.get("text", ""))
    return "\n".join(parts)


def _check_text(text: str, expect: dict) -> tuple[bool, str]:
    if "text_equals" in expect:
        want = expect["text_equals"]
        if text != want:
            return False, f"expected text `{want!r}`, got `{text!r}`"
    if "text_contains" in expect:
        want = expect["text_contains"]
        wants = want if isinstance(want, list) else [want]
        for w in wants:
            if w not in text:
                return False, f"expected text to contain `{w!r}`, got `{text!r}`"
    if "text_matches" in expect:
        pattern = expect["text_matches"]
        if not re.search(pattern, text, re.S):
            return False, f"expected text to match /{pattern}/, got `{text!r}`"
    return True, f"text OK ({text[:60]!r})"


def _check_tool(tool: dict, expect: dict) -> tuple[bool, str]:
    """Check a single tool entry from tools/list against expectations."""
    if "schema_property" in expect:
        prop = expect["schema_property"]
        schema = tool.get("inputSchema") or {}
        props = schema.get("properties") or {}
        if prop not in props:
            return False, f"expected `{tool['name']}` to declare input property `{prop}`"
    if "schema_property_description_contains" in expect:
        prop, want = expect["schema_property_description_contains"]
        props = (tool.get("inputSchema") or {}).get("properties") or {}
        desc = (props.get(prop) or {}).get("description") or ""
        if want.lower() not in desc.lower():
            return False, (
                f"expected `{tool['name']}.{prop}` description to mention `{want!r}`, "
                f"got `{desc!r}`"
            )
    if "annotation_equals" in expect:
        key, want = expect["annotation_equals"]
        annotations = tool.get("annotations") or {}
        got = annotations.get(key)
        if got != want:
            return False, f"expected `{tool['name']}.annotations.{key} == {want!r}`, got `{got!r}`"
    if "has_output_schema" in expect and expect["has_output_schema"]:
        if not tool.get("outputSchema"):
            return False, f"expected `{tool['name']}` to declare an outputSchema"
    return True, "tool shape OK"


# ---------- step runner ----------

async def _run_step(client: StdioMCPClient, step: GraderStep) -> tuple[bool, str]:
    """Execute one grader step. Returns (passed, message)."""
    kind = step.kind

    if kind == "initialize":
        resp = await client.send("initialize", {
            "protocolVersion": PROTOCOL_VERSION,
            "capabilities": {},
            "clientInfo": {"name": "mcp-teacher-grader", "version": "0.1.0"},
        })
        if resp is None or "error" in resp:
            return False, f"Initialize failed: {resp.get('error') if resp else 'no response'}"
        await client.send("notifications/initialized", is_notification=True)
        return True, "Handshake OK"

    if kind == "list_tools":
        resp = await client.send("tools/list")
        if resp is None or "error" in resp:
            return False, f"tools/list failed: {resp.get('error') if resp else 'no response'}"
        tools = (resp.get("result") or {}).get("tools") or []
        names = [t.get("name") for t in tools]

        wanted_name = step.expect.get("tool_name")
        wanted_all = step.expect.get("tools_include")
        if wanted_name and wanted_name not in names:
            return False, f"expected a tool named `{wanted_name}`, got: {names or 'no tools'}"
        if wanted_all:
            missing = [n for n in wanted_all if n not in names]
            if missing:
                return False, f"missing tool(s): {missing}. Found: {names}"
        # Per-tool shape checks
        if "tool_check" in step.expect:
            name, checks = step.expect["tool_check"]
            tool = next((t for t in tools if t.get("name") == name), None)
            if tool is None:
                return False, f"expected tool `{name}` to exist; got {names}"
            ok, msg = _check_tool(tool, checks)
            if not ok:
                return False, msg
        return True, f"tools OK: {names}"

    if kind == "call_tool":
        resp = await client.send("tools/call", step.params)
        if resp is None:
            return False, "tools/call got no response"
        if "error" in resp:
            return False, f"tools/call returned a protocol error: {resp['error']}"
        result = resp.get("result") or {}
        # isError check
        if "is_error" in step.expect:
            want_err = step.expect["is_error"]
            got_err = bool(result.get("isError"))
            if got_err != want_err:
                return False, f"expected isError={want_err}, got {got_err}"
        text = _text_blocks(result.get("content") or [])
        if any(k in step.expect for k in ("text_equals", "text_contains", "text_matches")):
            ok, msg = _check_text(text, step.expect)
            if not ok:
                return False, msg
        if "structured_has" in step.expect:
            structured = result.get("structuredContent") or {}
            for key in step.expect["structured_has"]:
                if key not in structured:
                    return False, f"expected structuredContent.{key}, got keys {list(structured)}"
        return True, f"call OK: {(text or json.dumps(result.get('structuredContent') or {}))[:80]}"

    if kind == "list_resources":
        resp = await client.send("resources/list")
        if resp is None or "error" in resp:
            return False, f"resources/list failed: {resp.get('error') if resp else 'no response'}"
        resources = (resp.get("result") or {}).get("resources") or []
        uris = [r.get("uri") for r in resources]
        if "uri" in step.expect:
            want = step.expect["uri"]
            if want not in uris:
                return False, f"expected resource URI `{want}`, got: {uris or 'none'}"
        return True, f"resources OK: {uris}"

    if kind == "list_resource_templates":
        resp = await client.send("resources/templates/list")
        if resp is None or "error" in resp:
            return False, f"resources/templates/list failed: {resp.get('error') if resp else 'no response'}"
        templates = (resp.get("result") or {}).get("resourceTemplates") or []
        uri_templates = [t.get("uriTemplate") for t in templates]
        if "uri_template_contains" in step.expect:
            want = step.expect["uri_template_contains"]
            if not any(want in (u or "") for u in uri_templates):
                return False, f"expected a resource template containing `{want}`, got: {uri_templates}"
        return True, f"resource templates OK: {uri_templates}"

    if kind == "read_resource":
        resp = await client.send("resources/read", step.params)
        if resp is None or "error" in resp:
            return False, f"resources/read failed: {resp.get('error') if resp else 'no response'}"
        contents = (resp.get("result") or {}).get("contents") or []
        text = "\n".join(c.get("text", "") for c in contents if c.get("text"))
        if any(k in step.expect for k in ("text_equals", "text_contains", "text_matches")):
            ok, msg = _check_text(text, step.expect)
            if not ok:
                return False, msg
        if "mime_equals" in step.expect:
            mimes = [c.get("mimeType") for c in contents]
            want = step.expect["mime_equals"]
            if want not in mimes:
                return False, f"expected mimeType `{want}`, got: {mimes}"
        return True, f"resource OK ({text[:60]!r})"

    if kind == "list_prompts":
        resp = await client.send("prompts/list")
        if resp is None or "error" in resp:
            return False, f"prompts/list failed: {resp.get('error') if resp else 'no response'}"
        prompts = (resp.get("result") or {}).get("prompts") or []
        names = [p.get("name") for p in prompts]
        if "prompt_name" in step.expect:
            want = step.expect["prompt_name"]
            if want not in names:
                return False, f"expected prompt named `{want}`, got: {names or 'none'}"
        return True, f"prompts OK: {names}"

    if kind == "get_prompt":
        resp = await client.send("prompts/get", step.params)
        if resp is None or "error" in resp:
            return False, f"prompts/get failed: {resp.get('error') if resp else 'no response'}"
        messages = (resp.get("result") or {}).get("messages") or []
        # Concatenate all text content across all messages for the text check
        concat = []
        for m in messages:
            content = m.get("content") or {}
            if isinstance(content, dict) and content.get("type") == "text":
                concat.append(content.get("text", ""))
            elif isinstance(content, list):
                for c in content:
                    if c.get("type") == "text":
                        concat.append(c.get("text", ""))
        text = "\n".join(concat)
        if any(k in step.expect for k in ("text_equals", "text_contains", "text_matches")):
            ok, msg = _check_text(text, step.expect)
            if not ok:
                return False, msg
        return True, f"prompt OK ({len(messages)} message(s))"

    if kind == "source_assert":
        # Static check on the student's source. Useful for concept levels.
        src = client.source
        if "contains" in step.expect:
            wants = step.expect["contains"]
            if isinstance(wants, str):
                wants = [wants]
            for w in wants:
                if w not in src:
                    return False, f"expected source to contain `{w}`"
        if "matches" in step.expect:
            pattern = step.expect["matches"]
            if not re.search(pattern, src, re.S):
                return False, f"expected source to match /{pattern}/"
        return True, "source check passed"

    if kind == "persistence_check":
        # Initialize, log a pellet, terminate, re-spawn in the SAME workdir,
        # initialize again, list_pellets, verify the pellet survived.
        # This exercises the real persistence layer end-to-end.
        if client.workdir is None:
            return False, "persistence_check: no workdir on client"
        test_habit = step.params.get("habit", "persistence-test-habit")

        # --- spawn #1 was done by grade(); finish init then log ---
        init_resp = await client.send("initialize", {
            "protocolVersion": PROTOCOL_VERSION,
            "capabilities": {},
            "clientInfo": {"name": "mcp-teacher-grader", "version": "0.1.0"},
        })
        if init_resp is None or "error" in init_resp:
            return False, f"first initialize failed: {init_resp}"
        await client.send("notifications/initialized", is_notification=True)
        log_resp = await client.send(
            "tools/call",
            {"name": "log_pellet", "arguments": {"habit": test_habit}},
        )
        if log_resp is None or "error" in log_resp:
            return False, f"first log_pellet failed: {log_resp}"
        log_result = log_resp.get("result") or {}
        if log_result.get("isError"):
            text = _text_blocks(log_result.get("content") or [])
            return False, f"first log_pellet returned an error: {text}"

        # --- kill #1, spawn #2 in the same workdir ---
        source = client.source
        workdir = client.workdir
        await client.close()

        client.proc = None
        client._stderr_task = None
        # Re-use the same client object so .trace stays unified for the
        # Protocol Inspector — easier than splicing two traces together.
        await client.spawn(source, workdir)

        init_resp2 = await client.send("initialize", {
            "protocolVersion": PROTOCOL_VERSION,
            "capabilities": {},
            "clientInfo": {"name": "mcp-teacher-grader", "version": "0.1.0"},
        })
        if init_resp2 is None or "error" in init_resp2:
            return False, f"second initialize failed: {init_resp2}"
        await client.send("notifications/initialized", is_notification=True)

        list_resp = await client.send("tools/call", {"name": "list_pellets", "arguments": {}})
        if list_resp is None or "error" in list_resp:
            return False, f"after restart, list_pellets failed: {list_resp}"
        text = _text_blocks((list_resp.get("result") or {}).get("content") or [])
        if test_habit not in text:
            return False, (
                f"after restart, list_pellets did not contain `{test_habit}`. "
                f"Got: {text!r}. Did you call _save(PELLETS) on write and _load() on startup?"
            )
        return True, f"`{test_habit}` survived the restart"

    return False, f"Unknown grader step kind: {kind}"


async def grade(world: int, level: int, code: str) -> dict:
    lesson = LESSONS.get((world, level))
    if not lesson:
        return {
            "passed": False,
            "trace": [],
            "stderr": "",
            "steps": [],
            "errors": [f"No lesson for world {world}, level {level}"],
        }

    client = StdioMCPClient()
    workdir = Path(tempfile.mkdtemp(prefix="mcp_student_"))
    step_results: list[dict] = []
    errors: list[str] = []
    passed_overall = True

    try:
        try:
            await client.spawn(code, workdir)
        except FileNotFoundError as e:
            return {
                "passed": False,
                "trace": [],
                "stderr": f"Python not found: {e}. Set MCP_TEACHER_PYTHON env var.",
                "steps": [],
                "errors": [str(e)],
            }

        async def _run_all():
            nonlocal passed_overall
            need_spawn = any(
                s.kind != "source_assert" for s in lesson.grader_steps
            )
            # If the lesson is pure source_assert (concept level), the server
            # never gets a chance to start cleanly — we still rely on
            # client.source which was captured during spawn().
            for step in lesson.grader_steps:
                try:
                    ok, msg = await _run_step(client, step)
                except GraderError as e:
                    ok, msg = False, str(e)
                step_results.append({
                    "kind": step.kind,
                    "description": step.description,
                    "passed": ok,
                    "message": msg,
                })
                if not ok:
                    passed_overall = False
                    errors.append(f"{step.description or step.kind}: {msg}")
                    break  # stop on first failure
            _ = need_spawn  # currently informational only

        try:
            await asyncio.wait_for(_run_all(), timeout=TIMEOUT_TOTAL)
        except asyncio.TimeoutError:
            passed_overall = False
            errors.append("Overall grader timed out (server too slow or stuck).")
    except Exception as e:
        passed_overall = False
        errors.append(f"{type(e).__name__}: {e}")
    finally:
        await client.close()
        shutil.rmtree(workdir, ignore_errors=True)

    return {
        "passed": passed_overall,
        "trace": client.trace,
        "stderr": "\n".join(client.stderr_buf),
        "steps": step_results,
        "errors": errors,
        "pellet_reward": lesson.pellet_reward if passed_overall else 0,
    }
