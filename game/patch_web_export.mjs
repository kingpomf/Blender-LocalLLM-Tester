// Post-export patch so the Godot Web build runs on the plain-HTTP AidenGames
// LAN site. Run after exporting, e.g.:
//   godot --headless --path game --export-release "Web" build/web/index.html
//   node patch_web_export.mjs build/web
//
// Godot Web requires a secure context (HTTPS/localhost). The LAN profile is
// plain HTTP, so this bypasses the startup gate. Audio is disabled separately
// via project.godot (audio/driver/driver="Dummy") because AudioWorklet is also
// secure-context-gated. This demo uses no audio and no secure-only APIs.
import { readFileSync, writeFileSync } from 'node:fs';
import path from 'node:path';

const dir = process.argv[2];
if (!dir) {
	console.error('usage: node patch_web_export.mjs <export-dir>');
	process.exit(1);
}
const file = path.join(dir, 'index.js');
let src = readFileSync(file, 'utf8');
const needle = "return window['isSecureContext'] === true;";

if (src.includes('LAN test patch')) {
	console.log('already patched:', file);
} else if (src.includes(needle)) {
	src = src.replace(needle, 'return true; /* LAN test patch: HTTP is not a secure context */');
	writeFileSync(file, src);
	console.log('patched secure-context gate:', file);
} else {
	console.error('secure-context needle not found; the Godot template may have changed.');
	process.exit(2);
}
