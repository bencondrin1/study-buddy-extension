// katex_renderer.js

const katex = require("katex");

// Read input from stdin
let input = "";
process.stdin.on("data", chunk => {
  input += chunk;
});

process.stdin.on("end", () => {
  try {
    const latex = input.trim();
    const displayMode = process.argv.includes("--display-mode");
    const html = katex.renderToString(latex, {
      displayMode: displayMode,
      throwOnError: false,
      errorColor: "#cc0000"
    });
    process.stdout.write(html);
  } catch (error) {
    console.error("KaTeX rendering error:", error.message);
    process.exit(1);
  }
});
