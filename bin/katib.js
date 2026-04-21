#!/usr/bin/env node
/**
 * Katib npx entry point.
 *
 * Usage:
 *   npx @jasemal/katib                 # same as `install`
 *   npx @jasemal/katib install         # run the bash installer
 *   npx @jasemal/katib update          # git pull the installed skill
 *   npx @jasemal/katib uninstall       # run the bash uninstaller
 *   npx @jasemal/katib version         # print version
 *   npx @jasemal/katib help            # this message
 *
 * The actual install logic lives in install.sh — this is a thin wrapper that
 * fetches and runs it with the right env. Works on macOS, Linux, and WSL2.
 * Native Windows is unsupported (see README).
 */
"use strict";

const { spawnSync }   = require("child_process");
const { createWriteStream, existsSync, unlinkSync, mkdtempSync } = require("fs");
const { tmpdir, platform, homedir } = require("os");
const path            = require("path");
const https           = require("https");

const REPO      = process.env.KATIB_REPO_URL || "https://github.com/jneaimi/katib.git";
const RAW_BASE  = process.env.KATIB_RAW_BASE || "https://raw.githubusercontent.com/jneaimi/katib/main";
const SKILL_DIR = path.join(homedir(), ".claude", "skills", "katib");
const VERSION   = require("../package.json").version;

// ---------- tiny helpers ----------
function die(msg, code = 1) {
  process.stderr.write(`\x1b[31m✗\x1b[0m ${msg}\n`);
  process.exit(code);
}
function info(msg) { process.stdout.write(`\x1b[36m▶\x1b[0m ${msg}\n`); }
function ok(msg)   { process.stdout.write(`\x1b[32m✓\x1b[0m ${msg}\n`); }

function assertSupportedOS() {
  const p = platform();
  if (p === "win32") {
    die([
      "Native Windows is not supported in v0.1.",
      "",
      "Please install WSL2 (Ubuntu) and re-run from inside WSL:",
      "  https://learn.microsoft.com/en-us/windows/wsl/install",
      "",
      "From WSL, the command stays the same:",
      "  npx @jasemal/katib",
    ].join("\n"));
  }
  if (p !== "darwin" && p !== "linux") {
    die(`Unsupported platform: ${p}. Katib targets macOS, Linux, and WSL2.`);
  }
}

function requireCmd(cmd, hint) {
  const res = spawnSync("command", ["-v", cmd], { shell: true, stdio: "pipe" });
  if (res.status !== 0) {
    die(`${cmd} not found on PATH.${hint ? `\n  ${hint}` : ""}`);
  }
}

function download(url, dest) {
  return new Promise((resolve, reject) => {
    const file = createWriteStream(dest);
    https.get(url, (res) => {
      if (res.statusCode === 301 || res.statusCode === 302) {
        file.close(); unlinkSync(dest);
        return download(res.headers.location, dest).then(resolve, reject);
      }
      if (res.statusCode !== 200) {
        file.close(); unlinkSync(dest);
        return reject(new Error(`HTTP ${res.statusCode} fetching ${url}`));
      }
      res.pipe(file);
      file.on("finish", () => file.close(resolve));
    }).on("error", reject);
  });
}

function runBashScript(scriptPath, args = []) {
  const res = spawnSync("bash", [scriptPath, ...args], {
    stdio: "inherit",
    env: { ...process.env, KATIB_REPO_URL: REPO },
  });
  process.exit(res.status ?? 1);
}

// ---------- commands ----------
async function cmdInstall() {
  assertSupportedOS();
  // If the skill is already checked out, prefer its local install.sh —
  // guarantees the version we run matches what's on disk.
  const local = path.join(SKILL_DIR, "install.sh");
  if (existsSync(local)) {
    info(`Using local installer at ${local}`);
    return runBashScript(local);
  }
  // Otherwise fetch install.sh from the repo and run it.
  info(`Fetching installer from ${RAW_BASE}/install.sh`);
  const tmp = path.join(mkdtempSync(path.join(tmpdir(), "katib-")), "install.sh");
  try {
    await download(`${RAW_BASE}/install.sh`, tmp);
  } catch (e) {
    die(`Failed to download installer: ${e.message}`);
  }
  runBashScript(tmp);
}

function cmdUpdate() {
  assertSupportedOS();
  if (!existsSync(path.join(SKILL_DIR, ".git"))) {
    die(`Not installed at ${SKILL_DIR}. Run \`npx @jasemal/katib install\` first.`);
  }
  const res = spawnSync("git", ["-C", SKILL_DIR, "pull", "--ff-only"], { stdio: "inherit" });
  process.exit(res.status ?? 1);
}

function cmdUninstall(args) {
  assertSupportedOS();
  const script = path.join(SKILL_DIR, "uninstall.sh");
  if (!existsSync(script)) {
    die(`Uninstall script not found at ${script}. Is katib installed?`);
  }
  runBashScript(script, args);
}

function cmdVersion() {
  process.stdout.write(`katib v${VERSION}\n`);
}

function cmdHelp() {
  process.stdout.write([
    "",
    "  \x1b[1mkatib\x1b[0m — bilingual PDF document skill for Claude Code",
    "",
    "  Usage:",
    "    npx @jasemal/katib                 run the installer (same as `install`)",
    "    npx @jasemal/katib install         install or update the skill",
    "    npx @jasemal/katib update          git pull the installed skill",
    "    npx @jasemal/katib uninstall       remove the skill, keep user data",
    "    npx @jasemal/katib uninstall --purge   also wipe ~/.katib, config, memory",
    "    npx @jasemal/katib version         print the katib CLI version",
    "    npx @jasemal/katib help            this message",
    "",
    "  Installs to ~/.claude/skills/katib/",
    "  Docs: https://github.com/jneaimi/katib",
    "",
  ].join("\n"));
}

// ---------- main ----------
(async function main() {
  const [, , rawCmd = "install", ...rest] = process.argv;
  const cmd = rawCmd.toLowerCase();
  switch (cmd) {
    case "install":             await cmdInstall();       return;
    case "update":              cmdUpdate();              return;
    case "uninstall":           cmdUninstall(rest);       return;
    case "-v":
    case "--version":
    case "version":             cmdVersion();             return;
    case "-h":
    case "--help":
    case "help":                cmdHelp();                return;
    default:
      die(`Unknown command: ${rawCmd}\nRun \`npx @jasemal/katib help\` for usage.`);
  }
})().catch((e) => die(e.stack || e.message || String(e)));
