import { execFile } from "node:child_process"
import { join } from "node:path"

const CENTRAL_ROOT = "{{CENTRAL_ROOT}}"
const PROJECT_ID = "{{PROJECT_ID}}"
const POLICY_TOOLS = new Set([
  "apply_patch",
  "bash",
  "edit",
  "multiedit",
  "notebookedit",
  "patch",
  "shell",
  "write",
])
const HARNESS_EVIDENCE_TOOLS = new Set([
  "bash",
  "glob",
  "grep",
  "read",
  "search",
  "shell",
  "skill",
])

const sessionId = (value) =>
  value?.sessionID ??
  value?.sessionId ??
  value?.session_id ??
  value?.properties?.sessionID ??
  value?.properties?.sessionId ??
  value?.properties?.session_id

const runPython = (args, input, timeout) =>
  new Promise((resolve) => {
    const child = execFile("python3", args, {encoding: "utf-8", timeout, maxBuffer: 1024 * 1024}, (error, stdout, stderr) => {
      resolve({status: error ? (typeof error.code === "number" ? error.code : null) : 0, error, stdout, stderr})
    })
    child.stdin.on?.("error", () => {})
    child.stdin.end(input || "")
  })

const evaluate = (directory, mode, payload = {}) =>
  runPython(["-I", join(directory, ".agent-policy/runtime/managed_policy_guard.py"), mode, "opencode"],
    JSON.stringify({cwd: directory, ...payload}), 10000)

const collectLogs = () =>
  runPython([join(CENTRAL_ROOT, "bin/agent-policy"), "collect-logs", "--project", PROJECT_ID,
    "--channel", "opencode", "--quiet"], "", 30000)

const logDiagnostic = (client, directory, level, message) =>
  client.app
    .log({
      body: {
        service: "agent-policy",
        level,
        message,
      },
      query: { directory },
    })
    .catch(() => undefined)

const showNotification = async (client, directory, title, message, variant = "warning") => {
  await logDiagnostic(client, directory, variant === "error" ? "error" : "warn", message)
  try {
    await client.tui.showToast({
      body: {
        title,
        message,
        variant,
      },
      query: { directory },
    })
  } catch {
    // The structured server log above remains available when no TUI is attached.
  }
}

export const AgentPolicyPlugin = async ({ client, directory }) => {
  const startup = await evaluate(directory, "session-start")
  if (startup.stdout?.trim()) {
    void logDiagnostic(client, directory, "warn", startup.stdout.trim())
  }
  if (startup.stderr?.trim()) {
    void logDiagnostic(client, directory, "error", startup.stderr.trim())
  }

  return {
    "chat.message": async (input, output) => {
      const prompt = output.parts
        .filter((part) => part?.type === "text" && !part.synthetic)
        .map((part) => part.text)
        .join("\n")
      if (!prompt.trim()) return
      const result = await evaluate(directory, "user-prompt", {
        session_id: input.sessionID,
        prompt,
      })
      if (result.status !== 0) throw new Error(result.stderr || "승인 상태 기록 실패")
    },
    "experimental.session.compacting": async (input, output) => {
      const result = await evaluate(directory, "branch-context", {session_id: sessionId(input)})
      const context = result.stdout?.trim()
      if (context) output.context.push(context)
    },
    event: async ({ event }) => {
      if (event.type !== "session.idle") return

      const result = await collectLogs()
      if (result.status === 0) return
      const message = result.stderr?.trim() || result.error?.message || "알 수 없는 오류"
      await showNotification(
        client,
        directory,
        "중앙 필수 산출물 로그 수집 실패",
        message,
        "error",
      )
    },
    "tool.execute.before": async (input, output) => {
      if (!POLICY_TOOLS.has(String(input.tool).toLowerCase())) return

      const verdict = await evaluate(directory, "pre-tool", {
        session_id: sessionId(input),
        tool_use_id: input.callID,
        tool_name: input.tool,
        tool_input: output.args ?? {},
      })
      if (verdict.status === 0 && verdict.stdout?.trim()) {
        let decision
        try { decision = JSON.parse(verdict.stdout) } catch { throw new Error("중앙 guard의 판정 형식이 올바르지 않습니다.") }
        if (decision?.decision !== "allow") throw new Error("중앙 guard가 허용 판정을 반환하지 않았습니다.")
      }
      if (verdict.status !== 0 || verdict.error) {
        throw new Error(verdict.stderr?.trim() || "중앙 관리 파일 수정이 차단되었습니다.")
      }
    },
    "tool.execute.after": async (input, output) => {
      if (!HARNESS_EVIDENCE_TOOLS.has(String(input.tool).toLowerCase()) && !POLICY_TOOLS.has(String(input.tool).toLowerCase())) return
      const result = await evaluate(directory, "post-tool", {
        session_id: input.sessionID,
        tool_name: input.tool,
        tool_input: input.args ?? {},
        tool_output: output.output ?? "",
        tool_use_id: input.callID,
        tool_response: {
          success: output.error ? false : typeof output.metadata?.exit === "number"
            ? output.metadata.exit === 0
            : !["bash", "shell"].includes(String(input.tool).toLowerCase()) && output.output?.length > 0 ? true : undefined,
          exit_code: output.metadata?.exit,
          error: output.error,
        },
      })
      if (result.status !== 0) await showNotification(client, directory, "도구 실행 기록 실패", result.stderr || "상태 확인 필요", "error")
    },
  }
}
