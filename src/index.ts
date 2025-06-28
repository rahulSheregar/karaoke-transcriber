#!/usr/bin/env node
import { spawn } from "child_process";
import { Command } from "commander";
import path from "path";
import fs from "fs";

const pkgPath = path.resolve(__dirname, "../package.json");
const version = JSON.parse(fs.readFileSync(pkgPath, "utf8")).version;

const program = new Command();

program
  .name("karaoke-transcriber")
  .description("CLI to generate karaoke-style subtitles using Whisper + FFmpeg")
  .version(version)
  .option("--check", "Check system dependencies")
  .option("--input <path>", "Path to the input video file")
  .option("--output <path>", "Path to the output video file", "output.mp4");

program.parse(process.argv);
const options = program.opts();

if (options.check) {
  const checkScript = path.resolve(__dirname, "../check-env.js");
  const checkProcess = spawn("node", [checkScript], { stdio: "inherit" });

  checkProcess.on("close", (code) => {
    process.exit(code ?? 0);
  });
} else {
  if (!options.input) {
    console.error("Error: --input <path> is required unless using --check");
    process.exit(1);
  }

  const scriptPath = path.resolve(
    __dirname,
    "../python_backend/karaoke_gen.py"
  );

  const subprocess = spawn(
    "python3",
    [scriptPath, "--input", options.input, "--output", options.output],
    { stdio: "inherit" }
  );

  subprocess.on("close", (code) => {
    if (code === 0) {
      console.log(`Done! Output saved to ${options.output}`);
    } else {
      console.error(`Error: Python exited with code ${code}`);
    }
  });
}
