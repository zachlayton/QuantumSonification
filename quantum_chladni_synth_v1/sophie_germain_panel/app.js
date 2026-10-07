"use strict";

const ui = Object.fromEntries([
  "live-badge", "source-name", "revision-label", "profile-label", "mode-select",
  "probe-slider", "probe-output", "analyzer-slider", "analyzer-output",
  "analyzer-caption", "yaw-slider", "yaw-output", "pitch-slider", "pitch-output",
  "event-coordinate", "freeze-button", "purity", "coherence", "entropy",
  "qpe-result", "dominant-mode", "mode-caption", "event-caption", "live-state",
  "flow-status", "geodesic-status", "operator-status", "projection-status",
  "event-window-slider", "event-window-output", "rhythm-window-label",
  "rhythm-source", "coordinate-caption", "coordinate-note", "selected-event",
].map(id => [id, document.getElementById(id)]));

const canvases = Object.fromEntries([
  "field", "flow", "mode", "intensity", "quadrature", "trace", "histogram",
  "rhythm", "event-map", "event-trace", "interval", "interval-histogram",
].map(name => [name, document.getElementById(`${name}-canvas`)]));

const state = {
  geometry: null,
  frame: null,
  selectedMode: 0,
  probe: 0,
  yaw: 24,
  pitch: -18,
  analyzerAngle: -90,
  eventWindow: 12,
  frozen: false,
  lastRevision: 0,
  history: [],
  fieldReal: [],
  fieldImag: [],
};

function css(name) {
  return getComputedStyle(document.documentElement).getPropertyValue(name).trim();
}

function surface(canvas) {
  const rect = canvas.getBoundingClientRect();
  const ratio = Math.max(1, window.devicePixelRatio || 1);
  const width = Math.max(10, Math.round(rect.width));
  const height = Math.max(10, Math.round(rect.height));
  if (canvas.width !== Math.round(width * ratio) || canvas.height !== Math.round(height * ratio)) {
    canvas.width = Math.round(width * ratio);
    canvas.height = Math.round(height * ratio);
  }
  const context = canvas.getContext("2d");
  context.setTransform(ratio, 0, 0, ratio, 0, 0);
  context.clearRect(0, 0, width, height);
  return { context, width, height };
}

function grid(context, width, height) {
  context.strokeStyle = css("--line");
  context.globalAlpha = 0.26;
  context.lineWidth = 1;
  for (let i = 1; i < 6; i += 1) {
    const x = width * i / 6;
    const y = height * i / 6;
    context.beginPath(); context.moveTo(x, 0); context.lineTo(x, height); context.stroke();
    context.beginPath(); context.moveTo(0, y); context.lineTo(width, y); context.stroke();
  }
  context.globalAlpha = 1;
}

function line(context, x1, y1, x2, y2, color, width = 1) {
  context.strokeStyle = color;
  context.lineWidth = width;
  context.beginPath();
  context.moveTo(x1, y1);
  context.lineTo(x2, y2);
  context.stroke();
}

function marker(context, x, y) {
  context.strokeStyle = css("--ink");
  context.lineWidth = 1.4;
  context.beginPath();
  context.arc(x, y, 5, 0, Math.PI * 2);
  context.stroke();
  line(context, x - 8, y, x + 8, y, css("--ink"), 1.4);
  line(context, x, y - 8, x, y + 8, css("--ink"), 1.4);
}

function projectVertices(width, height) {
  const yaw = state.yaw * Math.PI / 180;
  const pitch = state.pitch * Math.PI / 180;
  const cy = Math.cos(yaw), sy = Math.sin(yaw);
  const cp = Math.cos(pitch), sp = Math.sin(pitch);
  const rotated = state.geometry.vertices.map(([x, y, z], index) => {
    const x1 = cy * x + sy * z;
    const z1 = -sy * x + cy * z;
    const y1 = cp * y - sp * z1;
    const depth = sp * y + cp * z1;
    return { x: x1, y: y1, depth, index };
  });
  const extent = Math.max(1e-9, ...rotated.flatMap(point => [Math.abs(point.x), Math.abs(point.y)]));
  const scale = 0.42 * Math.min(width, height) / extent;
  for (const point of rotated) {
    point.sx = width / 2 + point.x * scale;
    point.sy = height / 2 - point.y * scale;
  }
  return rotated.sort((a, b) => a.depth - b.depth);
}

function planarCoordinates(width, height, padding = 14) {
  const xs = state.geometry.vertices.map(vertex => vertex[0]);
  const ys = state.geometry.vertices.map(vertex => vertex[1]);
  const minX = Math.min(...xs), maxX = Math.max(...xs);
  const minY = Math.min(...ys), maxY = Math.max(...ys);
  const spanX = Math.max(1e-12, maxX - minX), spanY = Math.max(1e-12, maxY - minY);
  return state.geometry.vertices.map((vertex, index) => ({
    index,
    x: padding + (width - 2 * padding) * (vertex[0] - minX) / spanX,
    y: height - padding - (height - 2 * padding) * (vertex[1] - minY) / spanY,
  }));
}

function drawSpatialMap(canvas, values, transform = value => Math.abs(value)) {
  const { context, width, height } = surface(canvas);
  context.fillStyle = css("--panel");
  context.fillRect(0, 0, width, height);
  if (!state.geometry || !values.length) return;
  const points = planarCoordinates(width, height);
  const mapped = values.map(transform);
  const maximum = Math.max(1e-12, ...mapped.map(value => Math.abs(value)));
  const unique = axis => [...new Set(state.geometry.vertices.map(vertex => vertex[axis].toFixed(8)))].sort((a, b) => Number(a) - Number(b));
  const uniqueX = unique(0), uniqueY = unique(1);
  const regularEnough = uniqueX.length * uniqueY.length <= points.length * 1.15;
  if (regularEnough) {
    const xIndex = new Map(uniqueX.map((value, index) => [value, index]));
    const yIndex = new Map(uniqueY.map((value, index) => [value, index]));
    const raster = document.createElement("canvas");
    raster.width = uniqueX.length; raster.height = uniqueY.length;
    const rasterContext = raster.getContext("2d");
    state.geometry.vertices.forEach((vertex, index) => {
      const magnitude = Math.min(1, Math.max(0, mapped[index] / maximum));
      rasterContext.fillStyle = css("--teal");
      rasterContext.globalAlpha = 0.025 + 0.96 * magnitude;
      rasterContext.fillRect(xIndex.get(vertex[0].toFixed(8)), uniqueY.length - 1 - yIndex.get(vertex[1].toFixed(8)), 1, 1);
    });
    context.imageSmoothingEnabled = true;
    context.imageSmoothingQuality = "high";
    context.drawImage(raster, 14, 14, width - 28, height - 28);
  } else {
    const radius = Math.max(4, Math.min(width, height) / Math.sqrt(points.length) * 0.78);
    context.save();
    context.filter = `blur(${Math.max(2, radius * 0.3).toFixed(1)}px)`;
    for (const point of points) {
      const magnitude = Math.min(1, Math.max(0, mapped[point.index] / maximum));
      context.fillStyle = css("--teal");
      context.globalAlpha = 0.025 + 0.96 * magnitude;
      context.beginPath();
      context.arc(point.x, point.y, radius, 0, Math.PI * 2);
      context.fill();
    }
    context.restore();
  }
  context.globalAlpha = 1;
  const probe = points[state.probe];
  if (probe) marker(context, probe.x, probe.y);
}

function drawWave() {
  const { context, width, height } = surface(canvases.field);
  context.fillStyle = css("--panel");
  context.fillRect(0, 0, width, height);
  if (!state.geometry || !state.fieldReal.length) return;
  const vertices = state.geometry.vertices;
  const maximum = Math.max(1e-12, ...state.fieldReal.map(value => Math.abs(value)));
  const yaw = state.yaw * Math.PI / 180;
  const pitchScale = 0.10 + 0.16 * (Math.abs(state.pitch) / 80);
  const cx = Math.cos(yaw), sx = Math.sin(yaw);
  const xs = vertices.map(vertex => vertex[0]), ys = vertices.map(vertex => vertex[1]);
  const midX = (Math.min(...xs) + Math.max(...xs)) / 2;
  const midY = (Math.min(...ys) + Math.max(...ys)) / 2;
  const span = Math.max(1e-12, Math.max(...xs) - Math.min(...xs), Math.max(...ys) - Math.min(...ys));
  const points = vertices.map((vertex, index) => {
    const x = (vertex[0] - midX) / span * 2;
    const y = (vertex[1] - midY) / span * 2;
    const horizontal = cx * x - sx * y;
    const depth = sx * x + cx * y;
    const z = state.fieldReal[index] / maximum;
    return {
      index,
      x: width / 2 + horizontal * width * 0.31,
      y: height * 0.51 + depth * height * pitchScale - z * height * 0.22,
      sourceX: vertex[0],
      sourceY: vertex[1],
    };
  });
  const key = value => value.toFixed(8);
  const rows = new Map(), columns = new Map();
  points.forEach(point => {
    const row = key(point.sourceY), column = key(point.sourceX);
    if (!rows.has(row)) rows.set(row, []);
    if (!columns.has(column)) columns.set(column, []);
    rows.get(row).push(point); columns.get(column).push(point);
  });
  const drawFamily = (families, sortKey, color, alpha) => {
    context.strokeStyle = color; context.globalAlpha = alpha; context.lineWidth = 1;
    families.forEach(family => {
      if (family.length < 2) return;
      family.sort((a, b) => a[sortKey] - b[sortKey]);
      context.beginPath();
      family.forEach((point, index) => index ? context.lineTo(point.x, point.y) : context.moveTo(point.x, point.y));
      context.stroke();
    });
  };
  drawFamily(rows, "sourceX", css("--teal"), 0.92);
  drawFamily(columns, "sourceY", css("--line"), 0.8);
  if ([...rows.values()].every(row => row.length < 2)) {
    points.forEach(point => {
      context.fillStyle = css("--teal"); context.globalAlpha = 0.7;
      context.fillRect(point.x, point.y, 1.5, 1.5);
    });
  }
  context.globalAlpha = 1;
  const probe = points[state.probe];
  if (probe) marker(context, probe.x, probe.y);
}

function drawFlow() {
  const { context, width, height } = surface(canvases.flow);
  context.fillStyle = css("--panel");
  context.fillRect(0, 0, width, height);
  const size = Math.min(width - 70, height - 32);
  const left = (width - size) / 2, top = (height - size) / 2;
  context.strokeStyle = css("--line");
  context.strokeRect(left, top, size, size);
  const vectors = state.frame?.flow?.vectors || [];
  const localPoints = state.geometry ? planarCoordinates(size, size, 0) : [];
  if (!vectors.length || vectors.length !== localPoints.length) {
    for (let y = 1; y < 10; y += 1) for (let x = 1; x < 10; x += 1) {
      context.fillStyle = css("--line");
      context.globalAlpha = 0.5;
      context.fillRect(left + x * size / 10, top + y * size / 10, 1, 1);
    }
    context.globalAlpha = 1;
    context.fillStyle = css("--muted");
    context.font = "11px system-ui";
    context.textAlign = "center";
    context.fillText("CURRENT FIELD NOT PUBLISHED", width / 2, height / 2 + 4);
    context.textAlign = "left";
  } else {
    const bins = new Map();
    vectors.forEach((vector, index) => {
      const point = localPoints[index];
      const binX = Math.min(10, Math.floor(point.x / Math.max(1, size) * 11));
      const binY = Math.min(10, Math.floor(point.y / Math.max(1, size) * 11));
      const magnitude = Math.hypot(vector[0], vector[1]);
      const key = `${binX}:${binY}`;
      if (!bins.has(key) || magnitude > bins.get(key).magnitude) {
        bins.set(key, { point, vector, magnitude });
      }
    });
    const maximum = Math.max(1e-12, ...[...bins.values()].map(item => item.magnitude));
    bins.forEach(({ point, vector, magnitude }) => {
      const x = left + point.x, y = top + point.y;
      if (magnitude <= maximum * 1e-5) {
        context.fillStyle = css("--line");
        context.fillRect(x, y, 1, 1);
        return;
      }
      const arrowLength = 2 + 13 * Math.sqrt(magnitude / maximum);
      const dx = vector[0] / magnitude * arrowLength;
      const dy = -vector[1] / magnitude * arrowLength;
      const startX = x - dx / 2, startY = y - dy / 2;
      const endX = x + dx / 2, endY = y + dy / 2;
      line(context, startX, startY, endX, endY, css("--teal"), 1.15);
      const angle = Math.atan2(dy, dx), head = Math.min(3.2, arrowLength * 0.42);
      line(context, endX, endY, endX - head * Math.cos(angle - 0.58), endY - head * Math.sin(angle - 0.58), css("--teal"), 1.15);
      line(context, endX, endY, endX - head * Math.cos(angle + 0.58), endY - head * Math.sin(angle + 0.58), css("--teal"), 1.15);
    });
  }
  const probe = localPoints[state.probe];
  if (probe) marker(context, left + probe.x, top + probe.y);
}

function reconstructField() {
  if (!state.geometry || !state.frame || !state.frame.modes) return;
  const amplitudes = state.frame.modes.map(mode => {
    const magnitude = Math.sqrt(Math.max(0, mode.probability));
    return [magnitude * Math.cos(mode.phase_radians), magnitude * Math.sin(mode.phase_radians)];
  });
  const real = new Array(state.geometry.sample_count).fill(0);
  const imag = new Array(state.geometry.sample_count).fill(0);
  for (let sample = 0; sample < state.geometry.sample_count; sample += 1) {
    const eigenrow = state.geometry.eigenvectors[sample];
    for (let mode = 0; mode < amplitudes.length; mode += 1) {
      real[sample] += eigenrow[mode] * amplitudes[mode][0];
      imag[sample] += eigenrow[mode] * amplitudes[mode][1];
    }
  }
  state.fieldReal = real;
  state.fieldImag = imag;
}

function drawSpectrum() {
  const { context, width, height } = surface(canvases.spectrum);
  grid(context, width, height);
  if (!state.frame) return;
  const modes = state.frame.modes;
  const frequencies = modes.map(mode => Math.log(Math.max(mode.frequency_hz, 1e-9)));
  const low = Math.min(...frequencies), high = Math.max(...frequencies);
  const maxProbability = Math.max(1e-12, ...modes.map(mode => mode.probability));
  const teal = css("--teal"), amber = css("--amber"), muted = css("--muted");
  context.font = "10px ui-monospace, monospace";
  context.fillStyle = muted;
  context.fillText(`${modes[0].frequency_hz.toFixed(1)} Hz`, 10, height - 8);
  context.textAlign = "right";
  context.fillText(`${modes[modes.length - 1].frequency_hz.toFixed(1)} Hz`, width - 10, height - 8);
  context.textAlign = "left";
  modes.forEach((mode, index) => {
    const x = 14 + (width - 28) * (frequencies[index] - low) / Math.max(1e-12, high - low);
    const probability = mode.probability / maxProbability;
    const y = height - 28 - probability * (height - 54);
    context.strokeStyle = index === state.selectedMode ? amber : teal;
    context.globalAlpha = index === state.selectedMode ? 1 : 0.35 + 0.55 * probability;
    context.lineWidth = index === state.selectedMode ? 3 : 1.25 + 2 * Math.sqrt(Math.max(0, mode.material_weight));
    context.beginPath(); context.moveTo(x, height - 26); context.lineTo(x, y); context.stroke();
    context.fillStyle = context.strokeStyle;
    context.beginPath(); context.arc(x, y, index === state.selectedMode ? 5 : 2.5, 0, Math.PI * 2); context.fill();
  });
  context.globalAlpha = 1;
}

function drawBasis() {
  const { context, width, height } = surface(canvases.basis);
  if (!state.frame) return;
  const basis = state.frame.basis;
  const side = Math.ceil(Math.sqrt(basis.length));
  const gap = 7;
  const cell = Math.min((width - gap * (side + 1)) / side, (height - gap * (side + 1)) / side);
  const left = (width - (cell * side + gap * (side - 1))) / 2;
  const top = (height - (cell * side + gap * (side - 1))) / 2;
  const teal = css("--teal"), line = css("--line"), ink = css("--ink");
  const maximum = Math.max(1e-12, ...basis.map(item => item.population));
  basis.forEach((item, index) => {
    const row = Math.floor(index / side), column = index % side;
    const x = left + column * (cell + gap), y = top + row * (cell + gap);
    context.fillStyle = teal;
    context.globalAlpha = 0.1 + 0.9 * Math.sqrt(item.population / maximum);
    context.fillRect(x, y, cell, cell);
    context.globalAlpha = 1;
    context.strokeStyle = line; context.strokeRect(x, y, cell, cell);
    const radius = cell * 0.3;
    const cx = x + cell / 2, cy = y + cell / 2;
    context.strokeStyle = ink; context.lineWidth = 1.5;
    context.beginPath(); context.moveTo(cx, cy);
    context.lineTo(cx + radius * Math.cos(item.phase_radians), cy - radius * Math.sin(item.phase_radians));
    context.stroke();
    context.fillStyle = ink; context.font = "9px ui-monospace, monospace";
    context.fillText(index.toString(16).toUpperCase().padStart(2, "0"), x + 4, y + 11);
  });
  context.globalAlpha = 1;
}

function drawTrace() {
  const { context, width, height } = surface(canvases.trace);
  grid(context, width, height);
  if (state.history.length < 2) return;
  const max = Math.max(1e-9, ...state.history.flatMap(sample => [Math.abs(sample.real), Math.abs(sample.imag)]));
  const draw = (key, color) => {
    context.strokeStyle = color; context.lineWidth = 1.6; context.beginPath();
    state.history.forEach((sample, index) => {
      const x = 8 + (width - 16) * index / Math.max(1, state.history.length - 1);
      const y = height / 2 - sample[key] / max * (height * 0.42);
      if (index === 0) context.moveTo(x, y); else context.lineTo(x, y);
    });
    context.stroke();
  };
  context.strokeStyle = css("--line"); context.beginPath(); context.moveTo(0, height / 2); context.lineTo(width, height / 2); context.stroke();
  draw("real", css("--teal"));
  draw("imag", css("--amber"));
  context.fillStyle = css("--muted"); context.font = "10px system-ui";
  context.fillText("real", 9, 14); context.fillText("quadrature", 42, 14);
}

function drawHistogram() {
  const { context, width, height } = surface(canvases.histogram);
  grid(context, width, height);
  if (!state.history.length) return;
  const samples = state.history.map(sample => sample.real);
  const extent = Math.max(1e-9, ...samples.map(Math.abs));
  const bins = new Array(20).fill(0);
  samples.forEach(value => {
    const index = Math.min(bins.length - 1, Math.floor((value / extent + 1) * 0.5 * bins.length));
    bins[Math.max(0, index)] += 1;
  });
  const maximum = Math.max(...bins, 1);
  bins.forEach((count, index) => {
    const x = index * width / bins.length;
    const barWidth = Math.max(1, width / bins.length - 1);
    const barHeight = (height - 25) * count / maximum;
    context.fillStyle = index < bins.length / 2 ? css("--amber") : css("--teal");
    context.globalAlpha = 0.75;
    context.fillRect(x, height - barHeight - 14, barWidth, barHeight);
  });
  context.globalAlpha = 1;
  context.fillStyle = css("--muted"); context.font = "10px ui-monospace, monospace";
  context.fillText("−", 5, height - 3); context.fillText("0", width / 2 - 3, height - 3); context.fillText("+", width - 12, height - 3);
}

function drawRhythm() {
  if (!state.frame) return;
  const geodesic = state.frame.geodesic_events || [];
  const isGeodesic = geodesic.length > 0;
  const sourceEvents = isGeodesic ? geodesic : (state.frame.qpe_events || []);
  const events = sourceEvents.slice(-state.eventWindow);
  const useDistance = ui["event-coordinate"].value === "distance" && isGeodesic;
  const eventStrength = event => Math.max(0, isGeodesic
    ? Math.abs(event.weighted_increment || 0)
    : (event.confidence === undefined ? 0 : event.confidence));
  const coordinate = event => useDistance ? event.intrinsic_length : event.observer_elapsed_seconds;
  const eventId = event => isGeodesic
    ? `site ${event.site} · record ${event.record_index}`
    : `QPE revision ${event.revision}`;
  ui["event-window-output"].textContent = String(state.eventWindow);
  ui["rhythm-window-label"].textContent = `Latest ${events.length} of ${sourceEvents.length} admitted records`;
  ui["rhythm-source"].textContent = isGeodesic
    ? "AUTHORITATIVE GEODESIC PULSES · source timing and intrinsic coordinate"
    : "QPE FRAME SAMPLES · observer receipt times · not geodesic rhythm";
  ui["coordinate-caption"].textContent = isGeodesic
    ? "Intrinsic path coordinate by observer receipt time"
    : "QPE phase by observer receipt time · not a spatial trajectory";
  ui["coordinate-note"].textContent = isGeodesic
    ? "Path distance is source-owned; the panel does not reconstruct a trajectory."
    : "No geodesic path is inferred from QPE frame samples.";

  const empty = canvas => {
    const { context, width, height } = surface(canvas);
    context.fillStyle = css("--muted"); context.font = "12px system-ui"; context.textAlign = "center";
    context.fillText("Waiting for admitted source records", width / 2, height / 2);
    context.textAlign = "left";
  };
  if (!events.length) {
    [canvases.rhythm, canvases["event-map"], canvases["event-trace"], canvases.interval, canvases["interval-histogram"]].forEach(empty);
    ui["selected-event"].textContent = "No admitted event records are available.";
    return;
  }

  const times = events.map(event => event.observer_elapsed_seconds);
  const values = events.map(coordinate);
  const strengths = events.map(eventStrength);
  const timeIntervals = times.slice(1).map((value, index) => value - times[index]);
  const coordinateIntervals = values.slice(1).map((value, index) => value - values[index]);
  const median = samples => {
    if (!samples.length) return 1;
    const sorted = [...samples].sort((a, b) => a - b);
    return sorted[Math.floor(sorted.length / 2)];
  };

  {
    const { context, width, height } = surface(canvases.rhythm);
    const cx = width / 2, cy = height / 2, radius = Math.min(width, height) * 0.35;
    context.strokeStyle = css("--line"); context.lineWidth = 1.1;
    context.beginPath(); context.arc(cx, cy, radius, 0, Math.PI * 2); context.stroke();
    for (let tick = 0; tick < 32; tick += 1) {
      const angle = -Math.PI / 2 + tick / 32 * Math.PI * 2;
      line(context,
        cx + Math.cos(angle) * (radius + 7), cy + Math.sin(angle) * (radius + 7),
        cx + Math.cos(angle) * (radius + 10), cy + Math.sin(angle) * (radius + 10),
        css("--line"));
    }
    const low = values[0], span = Math.max(1e-12, values[values.length - 1] - low + Math.abs(median(coordinateIntervals)));
    const points = values.map((value, index) => {
      const angle = -Math.PI / 2 + (value - low) / span * Math.PI * 2;
      return { x: cx + radius * Math.cos(angle), y: cy + radius * Math.sin(angle), index };
    });
    context.strokeStyle = css("--teal"); context.globalAlpha = 0.55; context.beginPath();
    points.forEach((point, index) => index ? context.lineTo(point.x, point.y) : context.moveTo(point.x, point.y));
    context.stroke(); context.globalAlpha = 1;
    if (points.length > 1) line(context, points[points.length - 1].x, points[points.length - 1].y, points[0].x, points[0].y, css("--amber"), 2.2);
    const maxStrength = Math.max(1e-12, ...strengths);
    points.forEach((point, index) => {
      context.fillStyle = index === points.length - 1 ? css("--amber") : css("--teal");
      context.beginPath();
      context.arc(point.x, point.y, 3.5 + 5 * Math.sqrt(strengths[index] / maxStrength), 0, Math.PI * 2);
      context.fill();
      context.fillStyle = css("--muted"); context.font = "10px system-ui"; context.textAlign = "center";
      context.fillText(String(index + 1), cx + (radius - 20) * Math.cos(Math.atan2(point.y - cy, point.x - cx)), cy + (radius - 20) * Math.sin(Math.atan2(point.y - cy, point.x - cx)) + 3);
    });
    context.fillStyle = css("--muted"); context.font = "11px system-ui"; context.textAlign = "center";
    context.fillText(`${events.length} events`, cx, cy - 8);
    context.fillText(useDistance ? "intrinsic distance" : `${(times[times.length - 1] - times[0]).toFixed(2)} s window`, cx, cy + 12);
    context.textAlign = "left";
  }

  {
    const { context, width, height } = surface(canvases["event-map"]);
    const left = 42, right = width - 14, top = 18, bottom = height - 32;
    const xSpan = Math.max(1e-12, times[times.length - 1] - times[0]);
    const vertical = isGeodesic ? events.map(event => event.intrinsic_length) : events.map(event => event.qpe_phase);
    const low = isGeodesic ? Math.min(...vertical) : 0;
    const high = isGeodesic ? Math.max(...vertical) : 1;
    const x = value => left + (value - times[0]) / xSpan * (right - left);
    const y = value => bottom - (value - low) / Math.max(1e-12, high - low) * (bottom - top);
    [0, 0.5, 1].forEach(fraction => {
      const yy = bottom - fraction * (bottom - top);
      line(context, left, yy, right, yy, css("--line"));
    });
    context.strokeStyle = css("--teal"); context.lineWidth = 1.3; context.beginPath();
    vertical.forEach((value, index) => index ? context.lineTo(x(times[index]), y(value)) : context.moveTo(x(times[index]), y(value)));
    context.stroke();
    vertical.forEach((value, index) => {
      context.fillStyle = index === vertical.length - 1 ? css("--amber") : css("--teal");
      context.beginPath(); context.arc(x(times[index]), y(value), 3.5, 0, Math.PI * 2); context.fill();
    });
    context.fillStyle = css("--muted"); context.font = "10px system-ui";
    context.fillText(isGeodesic ? "Intrinsic length" : "QPE phase", left, 11);
    context.fillText("0 s", left, height - 9); context.textAlign = "right";
    context.fillText(`${xSpan.toFixed(2)} s`, right, height - 9); context.textAlign = "left";
  }

  {
    const { context, width, height } = surface(canvases["event-trace"]);
    const left = 38, right = width - 12, top = 18, bottom = height - 28;
    const xSpan = Math.max(1e-12, times[times.length - 1] - times[0]);
    const maxStrength = Math.max(1e-12, ...strengths);
    line(context, left, bottom, right, bottom, css("--line"));
    events.forEach((event, index) => {
      const x = left + (times[index] - times[0]) / xSpan * (right - left);
      const y = bottom - strengths[index] / maxStrength * (bottom - top);
      line(context, x, bottom, x, y, index === events.length - 1 ? css("--amber") : css("--teal"), index === events.length - 1 ? 2 : 1.2);
      context.fillStyle = index === events.length - 1 ? css("--amber") : css("--teal");
      context.beginPath(); context.arc(x, y, 3.2, 0, Math.PI * 2); context.fill();
    });
    context.fillStyle = css("--muted"); context.font = "10px system-ui";
    context.fillText("Source strength", left, 11); context.fillText("0 s", left, height - 8); context.textAlign = "right";
    context.fillText(`${xSpan.toFixed(2)} s`, right, height - 8); context.textAlign = "left";
  }

  {
    const { context, width, height } = surface(canvases.interval);
    const left = 34, right = width - 10, top = 17, bottom = height - 30;
    const minimum = timeIntervals.length ? Math.min(...timeIntervals) : 0;
    const maximum = timeIntervals.length ? Math.max(...timeIntervals) : 0;
    const range = Math.max(1e-12, maximum - minimum);
    const barWidth = (right - left) / Math.max(1, timeIntervals.length);
    [0, 0.5, 1].forEach(fraction => line(context, left, bottom - fraction * (bottom - top), right, bottom - fraction * (bottom - top), css("--line")));
    timeIntervals.forEach((interval, index) => {
      const heightValue = 8 + (interval - minimum) / range * (bottom - top - 8);
      context.fillStyle = index === timeIntervals.length - 1 ? css("--amber") : css("--teal");
      context.fillRect(left + index * barWidth + 2, bottom - heightValue, Math.max(2, barWidth - 4), heightValue);
    });
    context.fillStyle = css("--muted"); context.font = "10px system-ui";
    context.fillText(`${maximum.toFixed(3)} s`, 1, top + 4);
    context.fillText(`${minimum.toFixed(3)} s`, 1, bottom + 3);
    context.fillText("Event interval · local scale", left + 54, height - 8);
  }

  {
    const { context, width, height } = surface(canvases["interval-histogram"]);
    const left = 34, right = width - 10, top = 17, bottom = height - 30, count = 7;
    const minimumInterval = timeIntervals.length ? Math.min(...timeIntervals) : 0;
    const maximumInterval = timeIntervals.length ? Math.max(...timeIntervals) : 0;
    const intervalRange = Math.max(1e-12, maximumInterval - minimumInterval);
    const bins = new Array(count).fill(0);
    timeIntervals.forEach(interval => { bins[Math.min(count - 1, Math.floor((interval - minimumInterval) / intervalRange * count))] += 1; });
    const maximumCount = Math.max(1, ...bins), barWidth = (right - left) / count;
    [0, 0.5, 1].forEach(fraction => line(context, left, bottom - fraction * (bottom - top), right, bottom - fraction * (bottom - top), css("--line")));
    bins.forEach((countValue, index) => {
      const heightValue = countValue / maximumCount * (bottom - top);
      context.fillStyle = css("--teal");
      context.fillRect(left + index * barWidth + 2, bottom - heightValue, Math.max(2, barWidth - 4), heightValue);
    });
    context.fillStyle = css("--muted"); context.font = "10px system-ui";
    context.fillText(`${minimumInterval.toFixed(3)} s`, left, height - 8); context.textAlign = "right";
    context.fillText(`${maximumInterval.toFixed(3)} s`, right, height - 8); context.textAlign = "left";
  }

  const latest = events[events.length - 1];
  const lastInterval = timeIntervals.length ? timeIntervals[timeIntervals.length - 1] : 0;
  ui["selected-event"].textContent = `${eventId(latest)} · observer time ${latest.observer_elapsed_seconds.toFixed(3)} s · source strength ${eventStrength(latest).toFixed(3)} · preceding interval ${lastInterval.toFixed(3)} s`;
}

function render() {
  if (!state.geometry) return;
  drawWave();
  drawFlow();
  const selectedMode = state.geometry.eigenvectors.map(row => row[state.selectedMode]);
  const modeMaximum = Math.max(1e-12, ...selectedMode.map(value => Math.abs(value)));
  const nodalBrightness = selectedMode.map(value => Math.exp(-Math.pow(value / modeMaximum, 2) / 0.055));
  const intensity = state.fieldReal.map((value, index) => value * value + state.fieldImag[index] * state.fieldImag[index]);
  const angle = state.analyzerAngle * Math.PI / 180;
  const analyzer = state.fieldReal.map((value, index) => Math.abs(value * Math.cos(angle) - state.fieldImag[index] * Math.sin(angle)));
  drawSpatialMap(canvases.mode, nodalBrightness, value => value);
  drawSpatialMap(canvases.intensity, intensity, value => value);
  drawSpatialMap(canvases.quadrature, analyzer, value => value);
  drawTrace(); drawHistogram(); drawRhythm();
}

function availability(element, item) {
  element.textContent = item.available ? `Available · ${item.source || item.reason}` : `Unavailable · ${item.reason}`;
  element.className = item.available ? "available" : "unavailable";
}

function updateLabels() {
  const frame = state.frame;
  if (!frame || frame.status !== "live") return;
  const sourceLabels = {
    quantum_chladni_synth_v1: "Quantum Chladni",
    qmw_v4_2_authoritative_density: "QMW V4.2 authoritative density",
  };
  ui["live-badge"].textContent = "LIVE"; ui["live-badge"].className = "badge live";
  ui["source-name"].textContent = sourceLabels[frame.source] || frame.source;
  ui["live-state"].textContent = "live";
  ui["revision-label"].textContent = `revision ${frame.source_revision}`;
  ui["profile-label"].textContent = `profile ${frame.profile}`;
  ui.purity.textContent = frame.diagnostics.purity.toFixed(4);
  ui.coherence.textContent = frame.diagnostics.coherence_normalized.toFixed(4);
  ui.entropy.textContent = frame.diagnostics.entropy_normalized.toFixed(4);
  ui["qpe-result"].textContent = `|${frame.qpe.bitstring}⟩ · φ ${frame.qpe.phase.toFixed(4)}`;
  const dominant = frame.modes[frame.qpe.dominant_mode];
  ui["dominant-mode"].textContent = `${frame.qpe.dominant_mode + 1} · ${dominant.frequency_hz.toFixed(2)} Hz`;
  const selected = frame.modes[state.selectedMode];
  ui["mode-caption"].textContent = `Mode ${state.selectedMode + 1} · ${selected.frequency_hz.toFixed(2)} Hz · decay ${selected.decay_seconds.toFixed(2)} s`;
  availability(ui["flow-status"], frame.availability.probability_or_energy_flow);
  availability(ui["geodesic-status"], frame.availability.geodesic_rhythm);
  ui["operator-status"].textContent = state.geometry.operator;
  ui["projection-status"].textContent = frame.projection.mapping_status;
  const hasGeodesic = frame.geodesic_events && frame.geodesic_events.length > 0;
  ui["event-coordinate"].options[1].disabled = !hasGeodesic;
  if (!hasGeodesic && ui["event-coordinate"].value === "distance") ui["event-coordinate"].value = "time";
  ui["event-caption"].textContent = hasGeodesic
    ? "Authoritative geodesic pulses · no panel-side scheduling"
    : "QPE samples at the frame-publication cadence · not geodesic rhythm";
}

function appendProbeSample() {
  if (!state.fieldReal.length || state.probe >= state.fieldReal.length) return;
  state.history.push({
    revision: state.frame.source_revision,
    time: state.frame.observer_elapsed_seconds,
    real: state.fieldReal[state.probe],
    imag: state.fieldImag[state.probe],
  });
  if (state.history.length > 240) state.history.splice(0, state.history.length - 240);
}

async function loadGeometry() {
  const response = await fetch("/api/geometry", { cache: "no-store" });
  if (!response.ok) throw new Error(`geometry ${response.status}`);
  state.geometry = await response.json();
  ui["probe-slider"].max = Math.max(0, state.geometry.sample_count - 1);
  state.probe = state.geometry.eigenvectors.reduce((best, row, index, rows) => {
    const energy = row.reduce((total, value) => total + value * value, 0);
    const bestEnergy = rows[best].reduce((total, value) => total + value * value, 0);
    return energy > bestEnergy ? index : best;
  }, 0);
  ui["probe-slider"].value = state.probe;
  ui["probe-output"].textContent = String(state.probe + 1);
  ui["mode-select"].replaceChildren(...state.geometry.frequencies_hz.map((frequency, index) => {
    const option = document.createElement("option");
    option.value = index; option.textContent = `${String(index + 1).padStart(2, "0")} · ${frequency.toFixed(2)} Hz`;
    return option;
  }));
  ui["operator-status"].textContent = state.geometry.operator;
}

async function poll() {
  try {
    const response = await fetch("/api/frame", { cache: "no-store" });
    if (!response.ok) throw new Error(`frame ${response.status}`);
    const frame = await response.json();
    if (frame.status !== "live") return;
    if (!state.frozen && frame.source_revision > state.lastRevision) {
      if (state.lastRevision === 0) {
        state.selectedMode = frame.qpe.dominant_mode;
        ui["mode-select"].value = String(state.selectedMode);
      }
      state.frame = frame;
      state.lastRevision = frame.source_revision;
      state.selectedMode = Math.min(state.selectedMode, frame.modes.length - 1);
      reconstructField(); appendProbeSample(); updateLabels(); render();
    }
  } catch (error) {
    ui["live-badge"].textContent = "OFFLINE"; ui["live-badge"].className = "badge error";
    ui["revision-label"].textContent = error.message;
  }
}

ui["mode-select"].addEventListener("change", event => { state.selectedMode = Number(event.target.value); updateLabels(); render(); });
ui["analyzer-slider"].addEventListener("input", event => {
  state.analyzerAngle = Number(event.target.value);
  const label = `${state.analyzerAngle < 0 ? "−" : ""}${Math.abs(state.analyzerAngle)}°`;
  ui["analyzer-output"].textContent = label;
  ui["analyzer-caption"].textContent = label;
  render();
});
ui["probe-slider"].addEventListener("input", event => {
  state.probe = Number(event.target.value); state.history = [];
  ui["probe-output"].textContent = String(state.probe + 1); render();
});
ui["yaw-slider"].addEventListener("input", event => { state.yaw = Number(event.target.value); ui["yaw-output"].textContent = `${state.yaw}°`; render(); });
ui["pitch-slider"].addEventListener("input", event => { state.pitch = Number(event.target.value); ui["pitch-output"].textContent = `${state.pitch < 0 ? "−" : ""}${Math.abs(state.pitch)}°`; render(); });
ui["event-coordinate"].addEventListener("change", render);
ui["event-window-slider"].addEventListener("input", event => {
  state.eventWindow = Number(event.target.value);
  render();
});
ui["freeze-button"].addEventListener("click", () => {
  state.frozen = !state.frozen;
  ui["freeze-button"].setAttribute("aria-pressed", String(state.frozen));
  ui["freeze-button"].textContent = state.frozen ? "Resume display" : "Freeze display";
});
window.addEventListener("resize", render);

(async () => {
  try {
    await loadGeometry();
    await poll();
    setInterval(poll, 125);
  } catch (error) {
    ui["live-badge"].textContent = "ERROR"; ui["live-badge"].className = "badge error";
    ui["revision-label"].textContent = error.message;
  }
})();
