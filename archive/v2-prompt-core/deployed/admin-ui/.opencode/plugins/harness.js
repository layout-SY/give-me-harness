import { spawnSync } from "node:child_process"
import { statSync } from "node:fs"
import { dirname, join, resolve } from "node:path"
import { fileURLToPath } from "node:url"

const EDIT_TOOLS = new Set(["write", "edit", "multiedit", "patch", "apply_patch", "bash", "shell"])
const PLUGIN_DIRECTORY = dirname(fileURLToPath(import.meta.url))

const executionDirectory = (sessionDirectory, workdir) => {
  if (typeof workdir !== "string" || workdir.trim() === "") return sessionDirectory
  const candidate = resolve(sessionDirectory, workdir)
  try {
    return statSync(candidate).isDirectory() ? candidate : sessionDirectory
  } catch {
    return sessionDirectory
  }
}

const evaluate = (directory, eventName, payload) => {
  const entry = join(PLUGIN_DIRECTORY, "harness_hook.py")
  const result = spawnSync("python3", ["-I", entry, eventName], {
    input: JSON.stringify(payload),
    encoding: "utf-8",
    timeout: 10000,
    cwd: directory,
  })
  return {
    blocked: result.status === 2,
    reason: (result.stderr || "").trim(),
    context: (result.stdout || "").trim(),
  }
}

export const HarnessPlugin = async ({ directory }) => ({
  "tool.execute.before": async (input, output) => {
    const toolName = String(input.tool).toLowerCase()
    if (!EDIT_TOOLS.has(toolName)) return
    const toolInput = output.args ?? {}
    const directoryToInspect = toolName === "bash" || toolName === "shell"
      ? executionDirectory(directory, toolInput.workdir)
      : directory
    const verdict = evaluate(directoryToInspect, "PreToolUse", {
      tool_name: toolName === "bash" ? "Bash" : input.tool,
      tool_input: toolInput,
    })
    if (verdict.blocked) throw new Error(verdict.reason)
  },
  "experimental.session.compacting": async (_input, output) => {
    const verdict = evaluate(directory, "BranchContext", {})
    if (verdict.context) output.context.push(verdict.context)
  },
})
