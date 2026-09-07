import { spawnSync } from "node:child_process"
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

const evaluate = (directory, mode, payload = {}) =>
  spawnSync(
    "python3",
    ["-I", join(directory, ".agent-policy/runtime/managed_policy_guard.py"), mode, "opencode"],
    {
      input: JSON.stringify({ cwd: directory, ...payload }),
      encoding: "utf-8",
      timeout: 10000,
    },
  )

const collectLogs = () =>
  spawnSync(
    "python3",
    [
      join(CENTRAL_ROOT, "bin/agent-policy"),
      "collect-logs",
      "--project",
      PROJECT_ID,
      "--channel",
      "opencode",
      "--quiet",
    ],
    {
      encoding: "utf-8",
      timeout: 30000,
    },
  )

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
  const startup = evaluate(directory, "session-start")
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
      evaluate(directory, "user-prompt", {
        session_id: input.sessionID,
        prompt,
      })
    },
    "experimental.session.compacting": async (_input, output) => {
      const result = evaluate(directory, "branch-context")
      const context = result.stdout?.trim()
      if (context) output.context.push(context)
    },
    event: async ({ event }) => {
      if (event.type !== "session.idle") return

      const result = collectLogs()
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

      const verdict = evaluate(directory, "pre-tool", {
        session_id: sessionId(input),
        tool_name: input.tool,
        tool_input: output.args ?? {},
      })
      if (verdict.status === 2) {
        throw new Error(verdict.stderr?.trim() || "중앙 관리 파일 수정이 차단되었습니다.")
      }
    },
    "tool.execute.after": async (input, output) => {
      if (!HARNESS_EVIDENCE_TOOLS.has(String(input.tool).toLowerCase())) return
      evaluate(directory, "post-tool", {
        session_id: input.sessionID,
        tool_name: input.tool,
        tool_input: input.args ?? {},
        tool_output: output.output ?? "",
      })
    },
  }
}
