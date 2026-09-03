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

export const AgentPolicyPlugin = async ({ directory }) => {
  const startup = evaluate(directory, "session-start")
  if (startup.stdout?.trim()) process.stderr.write(`${startup.stdout.trim()}\n`)
  if (startup.stderr?.trim()) process.stderr.write(`${startup.stderr.trim()}\n`)

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

      const documentation = evaluate(directory, "documentation-stop", {
        session_id: sessionId(event),
      })
      const output = documentation.stdout?.trim()
      if (output) {
        try {
          const verdict = JSON.parse(output)
          if (verdict.decision === "block") {
            process.stderr.write(`산출물 확인 필요: ${verdict.reason}\n`)
            return
          }
        } catch {
          process.stderr.write(`산출물 판정 결과를 해석할 수 없습니다: ${output}\n`)
          return
        }
      }

      const result = collectLogs()
      if (result.status === 0) return
      const message = result.stderr?.trim() || result.error?.message || "알 수 없는 오류"
      process.stderr.write(`중앙 필수 산출물 로그 수집 실패: ${message}\n`)
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
