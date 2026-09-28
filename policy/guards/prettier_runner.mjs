// Prettier만 포맷을 수행한다. 실제 파일 쓰기·동시 변경 검사는 Python 실행기가 맡는다.
import fs from "node:fs/promises";
import path from "node:path";
import { pathToFileURL } from "node:url";

const main = async () => {
  let input = "";
  for await (const chunk of process.stdin) input += chunk;
  const request = JSON.parse(input);
  const prettier = await import(
    pathToFileURL(path.join(request.package, "index.mjs")).href
  );
  if (prettier.version !== request.version)
    throw new Error("Prettier 버전이 정책과 다릅니다.");
  const results = [];
  for (const file of request.files) {
    const ignorePath = [".gitignore", ".prettierignore"].map((name) =>
      path.join(file.worktree, name),
    );
    const info = await prettier.getFileInfo(file.path, { ignorePath });
    if (info.ignored || !info.inferredParser) {
      results.push({ path: file.path, status: "ignored" });
      continue;
    }
    const configuration = await prettier.resolveConfigFile(file.path);
    if (!configuration)
      throw new Error(`Prettier 설정이 없습니다: ${file.path}`);
    const realConfig = await fs.realpath(configuration);
    const relative = path.relative(file.worktree, realConfig);
    if (relative.startsWith("..") || path.isAbsolute(relative))
      throw new Error(`프로젝트 밖의 Prettier 설정: ${configuration}`);
    const options = await prettier.resolveConfig(file.path, {
      editorconfig: true,
    });
    const content = await prettier.format(file.content, {
      ...options,
      filepath: file.path,
    });
    results.push({
      path: file.path,
      status: "formatted",
      content,
      config: realConfig,
    });
  }
  process.stdout.write(JSON.stringify({ files: results }));
};

main().catch((error) => {
  process.stderr.write(`Prettier 실행 실패: ${error.message}\n`);
  process.exitCode = 1;
});
