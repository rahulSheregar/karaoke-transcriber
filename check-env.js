const { execSync } = require("child_process");

function check(command, name, installHint = "") {
  try {
    execSync(command, { stdio: "ignore" });
    console.log("Found:", name);
  } catch {
    console.warn("Missing:", name);
    if (installHint) console.warn("  Hint:", installHint);
  }
}

console.log("\nChecking required system dependencies...\n");

check(
  "ffmpeg -version",
  "FFmpeg",
  "Install from https://ffmpeg.org or use 'brew install ffmpeg'"
);
check("python3 --version", "Python 3", "Install from https://www.python.org/");
check(
  "pip3 show openai-whisper",
  "Whisper (Python)",
  "Run: pip3 install openai-whisper"
);
check("pip3 show srt", "srt (Python)", "Run: pip3 install srt");

console.log(
  "\nIf any tools are missing, please install them before using this CLI.\n"
);
