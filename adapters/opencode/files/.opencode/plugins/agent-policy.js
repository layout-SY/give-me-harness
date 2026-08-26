import { spawnSync } from "node:child_process"
import { join } from "node:path"

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

export const AgentPolicyPlugin = async ({ directory }) => {
  const startup = evaluate(directory, "session-start")
  if (startup.stdout?.trim()) process.stderr.write(`${startup.stdout.trim()}\n`)
  if (startup.stderr?.trim()) process.stderr.write(`${startup.stderr.trim()}\n`)

  return {
    "tool.execute.before": async (input, output) => {
      if (!POLICY_TOOLS.has(String(input.tool).toLowerCase())) return

      const verdict = evaluate(directory, "pre-tool", {
        tool_name: input.tool,
        tool_input: output.args ?? {},
      })
      if (verdict.status === 2) {
        throw new Error(verdict.stderr?.trim() || "중앙 관리 파일 수정이 차단되었습니다.")
      }
    },
  }
}
