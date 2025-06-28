#!/usr/bin/env node
import { spawn } from "child_process";
import { Command } from "commander";
import path from "path";

const program = new Command();

program
  .requiredOption("--input <path>", "Path to the input video file")
  .option("--output <path>", "Path to output video", "output.mp4");

program.parse(process.argv);
const options = program.opts();

const scriptPath = path.resolve(__dirname, "../python_backend/karaoke_gen.py");

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
