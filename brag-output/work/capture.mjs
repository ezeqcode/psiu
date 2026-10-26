// Drive headless Chrome over the DevTools protocol (Node 22 has fetch + WebSocket built in).
//   node capture.mjs stills 1.6 5.2 9.0     -> stills/t1.6.png …
//   node capture.mjs frames 22 30           -> frames/f00000.png … (duration s, fps)
import { spawn } from "node:child_process";
import { mkdirSync, mkdtempSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join, dirname } from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";

const WORK = dirname(fileURLToPath(import.meta.url));
const CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome";
const PORT = 9333;
const W = 1080, H = 1920;
const [mode, ...args] = process.argv.slice(2);

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

const chrome = spawn(CHROME, [
  "--headless=new", `--remote-debugging-port=${PORT}`, `--user-data-dir=${mkdtempSync(join(tmpdir(), "brag-chrome-"))}`,
  "--hide-scrollbars", "--force-device-scale-factor=1", "--no-first-run", "--mute-audio", "about:blank",
], { stdio: "ignore" });

let target;
for (let i = 0; i < 50 && !target; i++) {
  await sleep(200);
  try {
    const list = await (await fetch(`http://127.0.0.1:${PORT}/json/list`)).json();
    target = list.find((t) => t.type === "page");
  } catch { /* chrome still starting */ }
}
if (!target) throw new Error("Chrome did not start");

const ws = new WebSocket(target.webSocketDebuggerUrl);
await new Promise((r) => ws.addEventListener("open", r, { once: true }));
let nextId = 0;
const pending = new Map();
ws.addEventListener("message", (e) => {
  const msg = JSON.parse(e.data);
  if (msg.id && pending.has(msg.id)) {
    const { resolve, reject } = pending.get(msg.id);
    pending.delete(msg.id);
    msg.error ? reject(new Error(msg.error.message)) : resolve(msg.result);
  }
});
const send = (method, params = {}) => new Promise((resolve, reject) => {
  const id = ++nextId;
  pending.set(id, { resolve, reject });
  ws.send(JSON.stringify({ id, method, params }));
});
const evaluate = async (expression) => (await send("Runtime.evaluate", { expression, awaitPromise: true, returnByValue: true })).result.value;

await send("Page.enable");
await send("Emulation.setDeviceMetricsOverride", { width: W, height: H, deviceScaleFactor: 1, mobile: false });
await send("Emulation.setEmulatedMedia", { features: [{ name: "prefers-color-scheme", value: "dark" }] });
await send("Page.navigate", { url: pathToFileURL(join(WORK, "video.html")).href });
for (let i = 0; i < 100 && !(await evaluate("window.__ready === true").catch(() => false)); i++) await sleep(100);
await sleep(300);

async function shoot(t, file) {
  await evaluate(`renderAt(${t}); new Promise(r => requestAnimationFrame(() => requestAnimationFrame(r)))`);
  const { data } = await send("Page.captureScreenshot", { format: "png", clip: { x: 0, y: 0, width: W, height: H, scale: 1 } });
  writeFileSync(file, Buffer.from(data, "base64"));
}

if (mode === "stills") {
  mkdirSync(join(WORK, "stills"), { recursive: true });
  for (const t of args) {
    await shoot(Number(t), join(WORK, "stills", `t${t}.png`));
    const bad = await evaluate("window.__overflow()");
    if (bad.length) console.log(`t=${t}`, bad.join(" | "));
  }
} else if (mode === "frames") {
  const [duration, fps] = args.map(Number);
  mkdirSync(join(WORK, "frames"), { recursive: true });
  const total = Math.round(duration * fps);
  for (let f = 0; f < total; f++) {
    await shoot(f / fps, join(WORK, "frames", `f${String(f).padStart(5, "0")}.png`));
    if (f % 60 === 0) process.stdout.write(`${f}/${total}\n`);
  }
}

ws.close();
chrome.kill();
