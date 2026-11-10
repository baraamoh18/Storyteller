// node compare.js a.json b.json : are two dumps the same (numbers within 0.002)?
const fs = require("fs");
const [a, b] = process.argv.slice(2).map((f) => JSON.parse(fs.readFileSync(f)));
const norm = (v) => (v || "").replace(/translate\(0px, 0px\)/g, "").replace(/translate3d\(0px, 0px, 0px\)/g, "").replace(/\s+/g, " ");
const nums = (v) => (norm(v).match(/-?\d+\.?\d*(e-?\d+)?/g) || []).map(Number);
const words = (v) => norm(v).replace(/-?\d+\.?\d*(e-?\d+)?/g, "#");
let bad = 0, checked = 0; const stateA = {}, stateB = {};
for (let k = 0; k < Math.max(a.length, b.length); k++) {
  Object.assign(stateA, a[k].d); Object.assign(stateB, b[k].d);
  for (const id of new Set([...Object.keys(a[k].d), ...Object.keys(b[k].d)])) {
    checked++;
    const x = stateA[id], y = stateB[id], nx = nums(x), ny = nums(y);
    const same = words(x) === words(y) && nx.length === ny.length && nx.every((v, i) => Math.abs(v - ny[i]) <= 0.002 + 0.0005 * Math.abs(v));
    if (!same && bad++ < 8) console.log(`DIFF at t=${a[k].t} ${id}\n  A ${x}\n  B ${y}`);
  }
}
console.log(bad ? `${bad} differences in ${checked} checks` : `identical: ${checked} element states over ${a.length} places`);
