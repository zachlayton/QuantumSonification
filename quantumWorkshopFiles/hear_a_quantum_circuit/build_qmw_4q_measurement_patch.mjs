// Build the self-contained measurement patch from the verified exact-state
// patch plus the small participant-facing measurement overlay.
//
// Keeping the exact patch as the source avoids a fragile bpatcher search-path
// dependency while preventing the two instrument implementations from
// drifting apart.

import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const directory = path.dirname(fileURLToPath(import.meta.url));
const exactPath = path.join(
  directory,
  "QMW_Four_Qubit_16_Overtone_Workshop.maxpat",
);
const overlayPath = path.join(
  directory,
  "qmw_4q_measurement_overlay_template.json",
);
const outputPath = path.join(
  directory,
  "QMW_Four_Qubit_16_Overtone_Measurement_Workshop.maxpat",
);

const exact = JSON.parse(fs.readFileSync(exactPath, "utf8"));
const overlay = JSON.parse(fs.readFileSync(overlayPath, "utf8"));

const overlayBoxes = overlay.patcher.boxes.filter(
  (entry) => entry.box.id !== "exact-patch",
);
const exactIds = new Set(exact.patcher.boxes.map((entry) => entry.box.id));
for (const entry of overlayBoxes) {
  if (exactIds.has(entry.box.id)) {
    throw new Error(`Duplicate Max object id: ${entry.box.id}`);
  }
}

exact.patcher.rect = [30.0, 45.0, 1400.0, 816.0];
exact.patcher.openinpresentation = 1;
exact.patcher.boxes.push(...overlayBoxes);
exact.patcher.lines.push(...overlay.patcher.lines);

exact.patcher.dependency_cache ??= [];
if (
  !exact.patcher.dependency_cache.some(
    (entry) => entry.name === "qmw_4q_measurement_workshop.js",
  )
) {
  exact.patcher.dependency_cache.push({
    name: "qmw_4q_measurement_workshop.js",
    patcherrelativepath: ".",
    type: "TEXT",
    implicit: 1,
  });
}

const allIds = new Set(exact.patcher.boxes.map((entry) => entry.box.id));
for (const entry of exact.patcher.lines) {
  const line = entry.patchline;
  if (!allIds.has(line.source[0]) || !allIds.has(line.destination[0])) {
    throw new Error(
      `Unresolved patch cord: ${line.source[0]} -> ${line.destination[0]}`,
    );
  }
}

fs.writeFileSync(outputPath, `${JSON.stringify(exact, null, 2)}\n`);
console.log(`Built ${path.basename(outputPath)}`);
