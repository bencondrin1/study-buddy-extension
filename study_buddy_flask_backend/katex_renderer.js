// katex_renderer.js

const katex = require("katex");
const readline = require("readline");

const rl = readline.createInterface({
  input: process.stdin,
  output: process.stdout,
  terminal: false,
});

let input = "";

rl.on("line", (line) => {
  input += line + "\n";
});

rl.on("close", () => {
  try {
    const latex = input.trim();

    // Detect \displaystyle passed from Python to enable block rendering
    const isDisplay = latex.startsWith("\\displaystyle ");
    const cleanLatex = isDisplay ? latex.replace("\\displaystyle ", "") : latex;

    const html = katex.renderToString(cleanLatex, {
      throwOnError: false,
      displayMode: isDisplay,
      strict: "warn",
    });

    console.log(html);
  } catch (err) {
    console.error("KaTeX render error:", err.message);
    process.exit(1);
  }
});
