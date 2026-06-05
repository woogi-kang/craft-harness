#!/usr/bin/env node
import fs from 'node:fs';
import path from 'node:path';

const args = process.argv.slice(2);
const targets = args.length ? args : ['.'];
const root = process.cwd();

const SKIP_DIRS = new Set([
  '.git',
  '.agents',
  '.claude',
  '.codex',
  '.cursor',
  '.gemini',
  '.github',
  '.opencode',
  'node_modules',
  '.next',
  'dist',
  'build',
  'coverage',
  '.turbo',
  '.vercel',
  '__pycache__',
]);

const EXTENSIONS = new Set([
  '.html',
  '.css',
  '.scss',
  '.sass',
  '.js',
  '.jsx',
  '.ts',
  '.tsx',
  '.vue',
  '.svelte',
  '.astro',
  '.md',
  '.mdx',
]);

const RULES = [
  ['ai-gradient', /\b(from|to|via)-(purple|violet|indigo|blue)-\d{2,3}\b|linear-gradient\([^)]*(purple|violet|indigo|blue)/i, 'Purple/blue gradient reflex'],
  ['gradient-text', /background-clip:\s*text|bg-clip-text/i, 'Gradient text'],
  ['default-glass', /backdrop-blur|glassmorphism/i, 'Glassmorphism/default blur surface'],
  ['h-screen', /\bh-screen\b|height:\s*100vh/i, 'Use min-height: 100dvh for viewport sections'],
  ['transition-all', /\btransition-all\b|transition:\s*all\b/i, 'Over-broad transition'],
  ['giant-z', /z-\[(999|9999|99999)\]|z-index:\s*(999|9999|99999)/i, 'Arbitrary giant z-index'],
  ['side-stripe', /\bborder-[lr]-[2-9]\b|border-(left|right)-width:\s*[2-9]px/i, 'Decorative side stripe'],
  ['fake-name', /\b(John Doe|Jane Doe|Acme|Nexus|SmartFlow|Cloudly)\b/i, 'Generic placeholder name'],
  ['cliche-copy', /\b(elevate|seamless|unleash|revolutionize|next-gen|game-changer|cutting-edge)\b/i, 'Generic marketing copy'],
  ['placeholder-label', /placeholder=["'][^"']+["'][^>\n]*(aria-label)?/i, 'Check placeholder-only labels'],
  ['scroll-cue', />\s*(Scroll|↓\s*scroll|Scroll to explore)\s*</i, 'Decorative scroll cue'],
  ['lorem', /Lorem ipsum/i, 'Lorem ipsum placeholder'],
];

const findings = [];

function shouldRead(filePath) {
  return EXTENSIONS.has(path.extname(filePath));
}

function isSkippedPath(filePath) {
  return path.relative(root, filePath).split(path.sep).some(part => SKIP_DIRS.has(part));
}

function walk(target) {
  const absolute = path.resolve(root, target);
  if (!fs.existsSync(absolute)) return;
  if (isSkippedPath(absolute)) return;
  const stat = fs.statSync(absolute);

  if (stat.isDirectory()) {
    for (const entry of fs.readdirSync(absolute)) {
      if (SKIP_DIRS.has(entry)) continue;
      walk(path.join(absolute, entry));
    }
    return;
  }

  if (!stat.isFile() || !shouldRead(absolute)) return;

  const rel = path.relative(root, absolute);
  const text = fs.readFileSync(absolute, 'utf8');
  const lines = text.split(/\r?\n/);

  lines.forEach((line, index) => {
    for (const [id, regex, message] of RULES) {
      if (regex.test(line)) {
        findings.push({
          id,
          message,
          file: rel,
          line: index + 1,
          snippet: line.trim().slice(0, 180),
        });
      }
    }
  });
}

for (const target of targets) walk(target);

if (!findings.length) {
  console.log('No design-slop pattern hits found.');
  process.exit(0);
}

for (const finding of findings) {
  console.log(`${finding.file}:${finding.line} [${finding.id}] ${finding.message}`);
  console.log(`  ${finding.snippet}`);
}

console.log(`\n${findings.length} finding(s). Treat these as review prompts, not automatic failures.`);
process.exit(1);
