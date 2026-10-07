(() => {
  "use strict";

  const payload = window.QMW_METRIC_DATA;
  if (!payload || payload.contract !== "qmw_metric.visualizer.v1") {
    throw new Error("Missing QMW visualizer payload");
  }
  const T = window.THREE;
  const stage = document.querySelector(".stage");
  const canvas = document.getElementById("fieldCanvas");
  if (!T) {
    stage.innerHTML = '<p class="fatal">three.js did not load. Serve this folder online or provide <code>window.THREE</code> locally.</p>';
    return;
  }

  const labels = {
    density: "Density",
    potential: "Potential",
    contours: "Potential contours",
    spatial_metric: "Spatial metric",
    lapse: "Lapse / time rate",
    curvature: "Scalar curvature",
    hessian_principal: "Hessian principal directions",
    probability_current: "Probability current + phase connection",
    vorticity: "Vorticity",
    eigenmodes: "Eigenmode shapes",
    trajectory: "Actual trajectory",
  };
  const ramps = {
    density: [[.025, .03, .065], [.95, .27, .13]],
    potential: [[.25, .055, .07], [.025, .035, .085], [.08, .14, .28]],
    lapse: [[.02, .07, .16], [.2, .8, .66]],
    curvature: [[.04, .25, .8], [.025, .035, .075], [1, .26, .12]],
    vorticity: [[.5, .1, .8], [.025, .035, .075], [.1, 1, .72]],
    eigenmodes: [[.05, .22, .9], [.025, .035, .075], [1, .7, .15]],
  };
  const scalarLayers = ["density", "potential", "lapse", "curvature", "vorticity", "eigenmodes"];
  const coherentScene = Math.max(0, payload.scenes.findIndex(s => s.name === "coherent_multi_well"));
  const state = {scene: coherentScene, mode: "analysis", modeIndex: 0, overlays: {}};
  payload.overlay_ids.forEach(id => state.overlays[id] = {enabled: false, opacity: .78});

  const renderer = new T.WebGLRenderer({canvas, antialias: true, powerPreference: "high-performance"});
  renderer.setPixelRatio(Math.min(devicePixelRatio || 1, 2));
  renderer.setClearColor(0x070910);
  renderer.outputColorSpace = T.SRGBColorSpace;
  const world = new T.Scene();
  world.fog = new T.FogExp2(0x070910, .075);
  const camera = new T.PerspectiveCamera(36, 1, .01, 100);
  camera.position.set(0, -2.75, 3.45);
  camera.lookAt(0, 0, -.08);
  const root = new T.Group();
  world.add(root);
  world.add(new T.HemisphereLight(0x8ca8ff, 0x08030d, 1.05));
  const key = new T.DirectionalLight(0xff927c, 1.3);
  key.position.set(-2, -3, 4);
  world.add(key);

  let surfaceObjects = [];
  let auxiliaryObjects = [];
  let orbitObjects = [];
  let coreObjects = [];
  let flowTracers = null;
  let trackedCenters = [];

  function disposeObject(object) {
    root.remove(object);
    object.geometry?.dispose();
    object.material?.map?.dispose();
    object.material?.dispose();
  }
  function disposeSurface() {
    surfaceObjects.forEach(disposeObject);
    surfaceObjects = [];
    flowTracers = null;
  }
  function disposeAuxiliary() {
    auxiliaryObjects.forEach(disposeObject);
    auxiliaryObjects = [];
    orbitObjects = [];
    coreObjects = [];
  }
  function addSurface(object) {
    root.add(object);
    surfaceObjects.push(object);
    return object;
  }
  function addAuxiliary(object) {
    root.add(object);
    auxiliaryObjects.push(object);
    return object;
  }

  const flatten = value => value.flat(Infinity);
  function range(value, symmetric = false) {
    let low = Infinity;
    let high = -Infinity;
    for (const item of flatten(value)) {
      low = Math.min(low, item);
      high = Math.max(high, item);
    }
    if (symmetric) {
      const maximum = Math.max(Math.abs(low), Math.abs(high), 1e-12);
      return [-maximum, maximum];
    }
    return [low, high === low ? low + 1 : high];
  }
  const mix = (a, b, t) => a.map((value, index) => value + (b[index] - value) * t);
  function ramp(t, palette) {
    t = Math.max(0, Math.min(1, t));
    return palette.length === 2
      ? mix(palette[0], palette[1], t)
      : t < .5 ? mix(palette[0], palette[1], t * 2) : mix(palette[1], palette[2], (t - .5) * 2);
  }
  const point = (x, y, z, nx, ny) => new T.Vector3(
    (x / (nx - 1) - .5) * 2.5,
    (.5 - y / (ny - 1)) * 2.5,
    z,
  );
  const height = (potential, maximum) => .66 * potential / maximum;
  const clamp = (value, low, high) => Math.max(low, Math.min(high, value));

  function scalarChoice(scene) {
    const id = scalarLayers.filter(name => state.overlays[name].enabled).at(-1) || "potential";
    const field = id === "eigenmodes"
      ? scene.mode_shapes[Math.min(state.modeIndex, scene.mode_shapes.length - 1)]
      : scene[id];
    return [id, field, state.overlays[id]?.opacity ?? .35];
  }
  function scalarField(scene, layer) {
    return layer === "eigenmodes"
      ? scene.mode_shapes[Math.min(state.modeIndex, scene.mode_shapes.length - 1)]
      : scene[layer];
  }
  function fieldMaximum(scene) {
    const [low, high] = range(scene.potential, true);
    return Math.max(Math.abs(low), Math.abs(high), 1e-12);
  }

  function createSurfaceMesh(scene, layer, opacity, additive = false) {
    const ny = scene.density.length;
    const nx = scene.density[0].length;
    const geometry = new T.PlaneGeometry(2.5, 2.5, nx - 1, ny - 1);
    geometry.setAttribute("color", new T.Float32BufferAttribute(new Float32Array(nx * ny * 3), 3));
    const material = additive
      ? new T.MeshBasicMaterial({vertexColors: true, transparent: true, opacity, depthWrite: false, blending: T.AdditiveBlending, side: T.DoubleSide})
      : new T.MeshStandardMaterial({vertexColors: true, roughness: .82, metalness: .03, transparent: true, opacity, side: T.DoubleSide});
    const mesh = addSurface(new T.Mesh(geometry, material));
    mesh.userData.fieldLayer = layer;
    mesh.userData.additive = additive;
    return mesh;
  }

  function rebuildSurface(scene) {
    disposeSurface();
    const [primary, , opacity] = scalarChoice(scene);
    createSurfaceMesh(scene, primary, Math.max(.22, opacity * .68));
    for (const layer of scalarLayers) {
      if (layer !== primary && state.overlays[layer].enabled) {
        createSurfaceMesh(scene, layer, state.overlays[layer].opacity * .24, true);
      }
    }
    if (state.overlays.probability_current.enabled) createFlowTracers(scene);
    updateSurface(scene, performance.now() / 1000);
  }

  function updateSurface(scene, clock) {
    const ny = scene.density.length;
    const nx = scene.density[0].length;
    const pmax = fieldMaximum(scene);
    let mode = null;
    let modeMaximum = 1;
    if (state.overlays.eigenmodes.enabled && scene.mode_shapes.length) {
      mode = scene.mode_shapes[Math.min(state.modeIndex, scene.mode_shapes.length - 1)];
      const [low, high] = range(mode, true);
      modeMaximum = Math.max(Math.abs(low), Math.abs(high), 1e-12);
    }
    for (const mesh of surfaceObjects) {
      if (!mesh.userData.fieldLayer) continue;
      const layer = mesh.userData.fieldLayer;
      const field = scalarField(scene, layer);
      const symmetric = ["potential", "curvature", "vorticity", "eigenmodes"].includes(layer);
      const [low, high] = range(field, symmetric);
      const positions = mesh.geometry.attributes.position;
      const colors = mesh.geometry.attributes.color;
      for (let y = 0; y < ny; y++) for (let x = 0; x < nx; x++) {
        const index = y * nx + x;
        const baseX = (x / (nx - 1) - .5) * 2.5;
        const baseY = (.5 - y / (ny - 1)) * 2.5;
        const gx = Math.sqrt(Math.max(scene.metric[0][0][y][x], 1e-12));
        const gy = Math.sqrt(Math.max(scene.metric[1][1][y][x], 1e-12));
        const metricX = state.overlays.spatial_metric.enabled ? 1 + .055 * clamp(gx - 1, -2, 2) : 1;
        const metricY = state.overlays.spatial_metric.enabled ? 1 + .055 * clamp(gy - 1, -2, 2) : 1;
        let z = state.overlays.potential.enabled || state.overlays.spatial_metric.enabled
          ? height(scene.potential[y][x], pmax) : 0;
        if (mode) {
          const localClock = clock * (1.35 + .9 * scene.lapse[y][x]);
          z += .065 * mode[y][x] / modeMaximum * Math.sin(localClock);
        }
        positions.setXYZ(index, baseX * metricX, baseY * metricY, z);
        const rgb = ramp((field[y][x] - low) / (high - low), ramps[layer]);
        const attenuation = mesh.userData.additive ? 1 : .72;
        colors.setXYZ(index, rgb[0] * attenuation, rgb[1] * attenuation, rgb[2] * attenuation);
      }
      positions.needsUpdate = true;
      colors.needsUpdate = true;
      if (!mesh.userData.additive) mesh.geometry.computeVertexNormals();
    }
  }

  function crossing(a, b, level, p, q) {
    if ((a < level) === (b < level) || a === b) return null;
    const t = (level - a) / (b - a);
    return [p[0] + (q[0] - p[0]) * t, p[1] + (q[1] - p[1]) * t];
  }
  function addContours(scene, nx, ny, pmax) {
    const vertices = [];
    const count = payload.presets[state.mode].contour_count || 10;
    const [low, high] = range(scene.potential);
    for (let levelIndex = 1; levelIndex < count; levelIndex++) {
      const level = low + (high - low) * levelIndex / count;
      for (let y = 0; y < ny - 1; y++) for (let x = 0; x < nx - 1; x++) {
        const field = scene.potential;
        const edges = [
          crossing(field[y][x], field[y][x + 1], level, [x, y], [x + 1, y]),
          crossing(field[y][x + 1], field[y + 1][x + 1], level, [x + 1, y], [x + 1, y + 1]),
          crossing(field[y + 1][x + 1], field[y + 1][x], level, [x + 1, y + 1], [x, y + 1]),
          crossing(field[y + 1][x], field[y][x], level, [x, y + 1], [x, y]),
        ].filter(Boolean);
        for (let edge = 0; edge + 1 < edges.length; edge += 2) {
          const a = point(edges[edge][0], edges[edge][1], height(level, pmax) + .008, nx, ny);
          const b = point(edges[edge + 1][0], edges[edge + 1][1], height(level, pmax) + .008, nx, ny);
          vertices.push(a.x, a.y, a.z, b.x, b.y, b.z);
        }
      }
    }
    const geometry = new T.BufferGeometry();
    geometry.setAttribute("position", new T.Float32BufferAttribute(vertices, 3));
    addAuxiliary(new T.LineSegments(geometry, new T.LineBasicMaterial({color: 0x44618f, transparent: true, opacity: state.overlays.contours.opacity * .68})));
  }

  function rawPeaks(field, count = 6, minimumDistance = 5) {
    const ny = field.length;
    const nx = field[0].length;
    const candidates = [];
    for (let y = 1; y < ny - 1; y++) for (let x = 1; x < nx - 1; x++) {
      const value = field[y][x];
      if (value >= field[y - 1][x] && value >= field[y + 1][x] && value >= field[y][x - 1] && value >= field[y][x + 1]) {
        candidates.push({x, y, value});
      }
    }
    candidates.sort((a, b) => b.value - a.value);
    const result = [];
    for (const candidate of candidates) {
      if (result.every(prior => Math.hypot(candidate.x - prior.x, candidate.y - prior.y) >= minimumDistance)) result.push(candidate);
      if (result.length === count) break;
    }
    return result;
  }
  function trackedPeaks(field) {
    const candidates = rawPeaks(field);
    if (!trackedCenters.length) {
      trackedCenters = candidates;
      return candidates;
    }
    const unused = candidates.slice();
    const ordered = [];
    for (const prior of trackedCenters) {
      if (!unused.length) break;
      let best = 0;
      for (let index = 1; index < unused.length; index++) {
        if (Math.hypot(unused[index].x - prior.x, unused[index].y - prior.y) < Math.hypot(unused[best].x - prior.x, unused[best].y - prior.y)) best = index;
      }
      ordered.push(unused.splice(best, 1)[0]);
    }
    trackedCenters = ordered.concat(unused).slice(0, 6);
    return trackedCenters;
  }
  function addLandscapeGrid(scene, nx, ny, pmax) {
    const vertices = [];
    const stride = 3;
    for (let y = 0; y < ny; y += stride) for (let x = 0; x < nx - 1; x++) {
      const a = point(x, y, height(scene.potential[y][x], pmax) + .004, nx, ny);
      const b = point(x + 1, y, height(scene.potential[y][x + 1], pmax) + .004, nx, ny);
      vertices.push(a.x, a.y, a.z, b.x, b.y, b.z);
    }
    for (let x = 0; x < nx; x += stride) for (let y = 0; y < ny - 1; y++) {
      const a = point(x, y, height(scene.potential[y][x], pmax) + .004, nx, ny);
      const b = point(x, y + 1, height(scene.potential[y + 1][x], pmax) + .004, nx, ny);
      vertices.push(a.x, a.y, a.z, b.x, b.y, b.z);
    }
    const geometry = new T.BufferGeometry();
    geometry.setAttribute("position", new T.Float32BufferAttribute(vertices, 3));
    addAuxiliary(new T.LineSegments(geometry, new T.LineBasicMaterial({color: 0x263b62, transparent: true, opacity: state.overlays.spatial_metric.opacity * .34})));
  }
  function criticalPoints(scene, count = 5, minimumDistance = 6) {
    const ny = scene.potential.length;
    const nx = scene.potential[0].length;
    const candidates = [];
    for (let y = 2; y < ny - 2; y++) for (let x = 2; x < nx - 2; x++) {
      candidates.push({x, y, value: Math.hypot(scene.grad_potential[0][y][x], scene.grad_potential[1][y][x])});
    }
    candidates.sort((a, b) => a.value - b.value);
    const result = [];
    for (const candidate of candidates) {
      if (result.every(prior => Math.hypot(candidate.x - prior.x, candidate.y - prior.y) >= minimumDistance)) result.push(candidate);
      if (result.length === count) break;
    }
    return result;
  }
  function textSprite(text) {
    const source = document.createElement("canvas");
    source.width = 128;
    source.height = 48;
    const context = source.getContext("2d");
    context.font = "26px ui-monospace, monospace";
    context.fillStyle = "#eef3ff";
    context.textAlign = "center";
    context.fillText(text, 64, 31);
    const sprite = new T.Sprite(new T.SpriteMaterial({map: new T.CanvasTexture(source), transparent: true, depthTest: false}));
    sprite.scale.set(.18, .068, 1);
    return sprite;
  }
  function addCriticalLabels(scene, nx, ny, pmax) {
    criticalPoints(scene).forEach((critical, index) => {
      const sprite = addAuxiliary(textSprite(`C${index + 1}`));
      sprite.position.copy(point(critical.x, critical.y, height(scene.potential[critical.y][critical.x], pmax) + .065, nx, ny));
    });
  }
  function addSourceCores(scene, nx, ny, pmax, centers) {
    for (const center of centers) {
      const location = point(center.x, center.y, height(scene.potential[center.y][center.x], pmax) + .035, nx, ny);
      const halo = addAuxiliary(new T.Mesh(new T.SphereGeometry(.075, 18, 12), new T.MeshBasicMaterial({color: 0xff715b, transparent: true, opacity: .18, blending: T.AdditiveBlending, depthWrite: false})));
      halo.position.copy(location);
      halo.userData.coreRate = scene.lapse[center.y][center.x];
      halo.userData.baseScale = 1;
      coreObjects.push(halo);
      const core = addAuxiliary(new T.Mesh(new T.SphereGeometry(.026, 18, 12), new T.MeshBasicMaterial({color: 0xffffff})));
      core.position.copy(location);
      const light = addAuxiliary(new T.PointLight(0xff6b57, .7, .55));
      light.position.copy(location);
    }
  }
  function addOrbitalRings(scene, nx, ny, pmax, centers) {
    for (const center of centers) {
      const origin = point(center.x, center.y, height(scene.potential[center.y][center.x], pmax), nx, ny);
      for (let ring = 0; ring < 6; ring++) {
        const radius = .075 + ring * .034;
        const points = [];
        for (let index = 0; index < 72; index++) {
          const angle = 2 * Math.PI * index / 72;
          const gx = center.x + Math.cos(angle) * radius / 2.5 * (nx - 1);
          const gy = center.y - Math.sin(angle) * radius * .72 / 2.5 * (ny - 1);
          const ix = clamp(Math.round(gx), 0, nx - 1);
          const iy = clamp(Math.round(gy), 0, ny - 1);
          points.push(new T.Vector3(
            Math.cos(angle) * radius,
            Math.sin(angle) * radius * .72,
            height(scene.potential[iy][ix], pmax) - origin.z + .018 + ring * .004,
          ));
        }
        const loop = addAuxiliary(new T.LineLoop(new T.BufferGeometry().setFromPoints(points), new T.LineBasicMaterial({color: 0xd9f4bd, transparent: true, opacity: state.overlays.contours.opacity * (.82 - ring * .075)})));
        loop.position.copy(origin);
        loop.userData.orbitRate = (.18 + ring * .035) * scene.lapse[center.y][center.x] * (ring % 2 ? -1 : 1);
        orbitObjects.push(loop);
      }
    }
  }

  function addVectors(field, scene, nx, ny, color, kind, scale = 1) {
    const vertices = [];
    const stride = payload.presets[state.mode].vector_stride || 4;
    let maximum = 1e-12;
    if (kind === "vector") {
      for (let y = 0; y < ny; y++) for (let x = 0; x < nx; x++) maximum = Math.max(maximum, Math.hypot(field[0][y][x], field[1][y][x]));
    }
    const pmax = fieldMaximum(scene);
    for (let y = 2; y < ny; y += stride) for (let x = 2; x < nx; x += stride) {
      let vx;
      let vy;
      if (kind === "hessian") {
        const angle = .5 * Math.atan2(2 * field[0][1][y][x], field[0][0][y][x] - field[1][1][y][x]);
        vx = Math.cos(angle);
        vy = -Math.sin(angle);
      } else {
        vx = field[0][y][x] / maximum;
        vy = -field[1][y][x] / maximum;
      }
      const p = point(x, y, height(scene.potential[y][x], pmax) + .035, nx, ny);
      const q = p.clone().add(new T.Vector3(vx * .075, vy * .075, .003));
      vertices.push(p.x, p.y, p.z, q.x, q.y, q.z);
    }
    const geometry = new T.BufferGeometry();
    geometry.setAttribute("position", new T.Float32BufferAttribute(vertices, 3));
    const alpha = (kind === "hessian" ? state.overlays.hessian_principal.opacity : state.overlays.probability_current.opacity) * scale;
    addAuxiliary(new T.LineSegments(geometry, new T.LineBasicMaterial({color, transparent: true, opacity: alpha})));
  }
  function addTrajectory(scene) {
    const [xmin, xmax, ymin, ymax] = payload.extent;
    const pmax = fieldMaximum(scene);
    const ny = scene.potential.length;
    const nx = scene.potential[0].length;
    const points = scene.trajectory_positions.map(position => {
      const gx = (position[0] - xmin) / (xmax - xmin) * (nx - 1);
      const gy = (position[1] - ymin) / (ymax - ymin) * (ny - 1);
      const ix = clamp(Math.round(gx), 0, nx - 1);
      const iy = clamp(Math.round(gy), 0, ny - 1);
      return new T.Vector3(
        (position[0] - xmin) / (xmax - xmin) * 2.5 - 1.25,
        1.25 - (position[1] - ymin) / (ymax - ymin) * 2.5,
        height(scene.potential[iy][ix], pmax) + .055,
      );
    });
    if (points.length < 2) return;
    const line = addAuxiliary(new T.Line(new T.BufferGeometry().setFromPoints(points), new T.LineDashedMaterial({color: 0xd65343, dashSize: .045, gapSize: .028, transparent: true, opacity: state.overlays.trajectory.opacity * .88})));
    line.computeLineDistances();
  }

  function rebuildAuxiliary(scene) {
    disposeAuxiliary();
    const ny = scene.density.length;
    const nx = scene.density[0].length;
    const pmax = fieldMaximum(scene);
    const centers = trackedPeaks(scene.density);
    if (state.overlays.spatial_metric.enabled) {
      addLandscapeGrid(scene, nx, ny, pmax);
      addCriticalLabels(scene, nx, ny, pmax);
    }
    if (state.overlays.contours.enabled) {
      addContours(scene, nx, ny, pmax);
      addOrbitalRings(scene, nx, ny, pmax, centers);
    }
    if (state.overlays.density.enabled) addSourceCores(scene, nx, ny, pmax, centers);
    if (state.overlays.hessian_principal.enabled) addVectors(scene.hessian, scene, nx, ny, 0xffd580, "hessian");
    if (state.overlays.probability_current.enabled) {
      addVectors(scene.phase_connection, scene, nx, ny, 0x79f0cf, "vector");
      addVectors(scene.probability_current, scene, nx, ny, 0xffffff, "vector", .55);
    }
    if (state.overlays.trajectory.enabled) addTrajectory(scene);
  }

  function createFlowTracers(scene) {
    const count = 180;
    const positions = new Float32Array(count * 3);
    for (let index = 0; index < count; index++) {
      positions[index * 3] = ((index * .61803398875) % 1 - .5) * 2.5;
      positions[index * 3 + 1] = ((index * .38196601125 + .23) % 1 - .5) * 2.5;
      positions[index * 3 + 2] = .04;
    }
    const geometry = new T.BufferGeometry();
    geometry.setAttribute("position", new T.BufferAttribute(positions, 3));
    flowTracers = addSurface(new T.Points(geometry, new T.PointsMaterial({color: 0xcfffdc, size: .018, transparent: true, opacity: state.overlays.probability_current.opacity * .72, blending: T.AdditiveBlending, depthWrite: false})));
    flowTracers.userData.flowTracer = true;
  }
  function sampleNearest(field, x, y) {
    const ny = field[0].length;
    const nx = field[0][0].length;
    const ix = clamp(Math.round((x / 2.5 + .5) * (nx - 1)), 0, nx - 1);
    const iy = clamp(Math.round((.5 - y / 2.5) * (ny - 1)), 0, ny - 1);
    return [field[0][iy][ix], field[1][iy][ix], ix, iy];
  }
  function updateFlowTracers(scene, dt) {
    if (!flowTracers || !state.overlays.probability_current.enabled) return;
    const field = scene.phase_connection;
    let maximum = 1e-12;
    for (let y = 0; y < field[0].length; y++) for (let x = 0; x < field[0][0].length; x++) maximum = Math.max(maximum, Math.hypot(field[0][y][x], field[1][y][x]));
    const positions = flowTracers.geometry.attributes.position;
    const pmax = fieldMaximum(scene);
    for (let index = 0; index < positions.count; index++) {
      let x = positions.getX(index);
      let y = positions.getY(index);
      const [vx, vy, ix, iy] = sampleNearest(field, x, y);
      x += vx / maximum * dt * .22;
      y -= vy / maximum * dt * .22;
      if (x > 1.25) x -= 2.5;
      if (x < -1.25) x += 2.5;
      if (y > 1.25) y -= 2.5;
      if (y < -1.25) y += 2.5;
      positions.setXYZ(index, x, y, height(scene.potential[iy][ix], pmax) + .045);
    }
    positions.needsUpdate = true;
  }

  function rebuildAll(scene) {
    trackedCenters = [];
    rebuildSurface(scene);
    rebuildAuxiliary(scene);
    document.getElementById("legend").textContent = payload.overlay_ids
      .filter(id => state.overlays[id].enabled).map(id => labels[id]).join(" · ");
  }

  const interpolatedFields = [
    "density", "potential", "lapse", "metric", "curvature", "hessian",
    "grad_potential", "probability_current", "phase_connection", "vorticity",
    "mode_shapes", "trajectory_positions",
  ];
  function blendArray(a, b, t) {
    if (typeof a === "number" && typeof b === "number") return a + (b - a) * t;
    if (!Array.isArray(a) || !Array.isArray(b) || a.length !== b.length) return b;
    return a.map((value, index) => blendArray(value, b[index], t));
  }
  function blendScene(from, to, t) {
    const scene = {...to};
    for (const name of interpolatedFields) scene[name] = blendArray(from[name], to[name], t);
    return scene;
  }
  const liveAnimation = {active: false, from: null, target: null, current: null, start: 0, duration: 100, lastAuxiliary: 0};
  function animatedLiveScene(now) {
    if (!liveAnimation.active || !liveAnimation.target) return null;
    const t = clamp((now - liveAnimation.start) / liveAnimation.duration, 0, 1);
    liveAnimation.current = blendScene(liveAnimation.from, liveAnimation.target, t * t * (3 - 2 * t));
    return liveAnimation.current;
  }
  function currentScene(now = performance.now()) {
    return animatedLiveScene(now) || payload.scenes[state.scene];
  }

  const controls = document.getElementById("overlayControls");
  payload.overlay_ids.forEach(id => {
    const row = document.createElement("div");
    row.className = "overlay";
    row.innerHTML = `<input type="checkbox" id="on-${id}"><label for="on-${id}">${labels[id]}</label><input aria-label="${labels[id]} opacity" id="alpha-${id}" type="range" min="0" max="1" value=".78" step=".02">`;
    controls.appendChild(row);
    row.children[0].onchange = event => {
      state.overlays[id].enabled = event.target.checked;
      rebuildAll(currentScene());
    };
    row.children[2].oninput = event => {
      state.overlays[id].opacity = +event.target.value;
      rebuildAll(currentScene());
    };
  });
  const sceneSelect = document.getElementById("sceneSelect");
  const modeSlider = document.getElementById("modeIndex");
  payload.scenes.forEach((scene, index) => {
    const option = document.createElement("option");
    option.value = index;
    option.textContent = scene.name.replaceAll("_", " ");
    sceneSelect.appendChild(option);
  });
  sceneSelect.onchange = event => {
    state.scene = +event.target.value;
    liveAnimation.active = payload.scenes[state.scene]?.name === "live_metric_frame";
    state.modeIndex = 0;
    sync();
    rebuildAll(currentScene());
  };
  modeSlider.oninput = event => {
    state.modeIndex = +event.target.value;
    document.getElementById("modeNumber").value = state.modeIndex + 1;
    rebuildAll(currentScene());
  };
  function preset(name) {
    state.mode = name;
    const presetData = payload.presets[name];
    const enabled = new Set(presetData.enabled);
    payload.overlay_ids.forEach(id => {
      state.overlays[id].enabled = enabled.has(id);
      state.overlays[id].opacity = presetData.opacity[id];
    });
    document.body.classList.toggle("performance", name === "performance");
    sync();
    rebuildAll(currentScene());
  }
  document.getElementById("analysisPreset").onclick = () => preset("analysis");
  document.getElementById("performancePreset").onclick = () => preset("performance");
  document.getElementById("clearAll").onclick = () => {
    payload.overlay_ids.forEach(id => state.overlays[id].enabled = false);
    sync();
    rebuildAll(currentScene());
  };
  function sync() {
    const scene = currentScene();
    payload.overlay_ids.forEach(id => {
      document.getElementById(`on-${id}`).checked = state.overlays[id].enabled;
      document.getElementById(`alpha-${id}`).value = state.overlays[id].opacity;
    });
    document.getElementById("analysisPreset").classList.toggle("active", state.mode === "analysis");
    document.getElementById("performancePreset").classList.toggle("active", state.mode === "performance");
    document.getElementById("sceneName").textContent = scene.name.replaceAll("_", " ");
    document.getElementById("revision").textContent = `source r${scene.source_revision} · frame r${scene.revision}`;
    document.getElementById("controlledChange").textContent = scene.controlled_change;
    document.getElementById("provenance").textContent = [scene.provenance, scene.projection_basis, scene.potential_model, scene.metric_model, scene.topography_mode].filter(Boolean).join(" · ");
    document.getElementById("diagnostics").innerHTML = `<div><small>coherence L1</small><b>${scene.coherence_l1.toFixed(4)}</b></div><div><small>purity</small><b>${scene.purity.toFixed(4)}</b></div><div><small>coupling κ</small><b>${scene.potential_coupling.toFixed(3)}</b></div><div><small>renderer</small><b>three.js / WebGL</b></div>`;
    modeSlider.max = Math.max(0, scene.mode_shapes.length - 1);
    modeSlider.value = Math.min(state.modeIndex, +modeSlider.max);
    document.getElementById("modeNumber").value = +modeSlider.value + 1;
  }

  function acceptLive(frame) {
    const arrays = frame.arrays;
    const scene = {
      name: "live_metric_frame",
      controlled_change: frame.model_label,
      revision: frame.revision,
      source_revision: frame.source_revision,
      time: frame.time,
      coherence_l1: 0,
      purity: 0,
      potential_coupling: 0,
      model_label: frame.model_label,
      density: arrays.density,
      potential: arrays.potential,
      lapse: arrays.lapse,
      metric: arrays.metric,
      curvature: arrays.curvature,
      hessian: arrays.hessian,
      grad_potential: arrays.grad_potential,
      probability_current: arrays.probability_current,
      phase_connection: arrays.phase_connection,
      vorticity: arrays.vorticity,
      mode_shapes: arrays.mode_shapes,
      trajectory_positions: arrays.trajectory_positions,
    };
    const now = performance.now();
    const prior = liveAnimation.current || liveAnimation.target;
    const changedShape = !prior || prior.density.length !== scene.density.length || prior.density[0].length !== scene.density[0].length;
    liveAnimation.from = changedShape ? scene : blendScene(liveAnimation.from || prior, liveAnimation.target || prior, clamp((now - liveAnimation.start) / liveAnimation.duration, 0, 1));
    liveAnimation.target = scene;
    liveAnimation.current = liveAnimation.from;
    liveAnimation.start = now;
    liveAnimation.duration = prior ? clamp((scene.time - prior.time) * 1000, 45, 240) : 100;
    liveAnimation.active = true;
    let index = payload.scenes.findIndex(candidate => candidate.name === "live_metric_frame");
    if (index < 0) {
      payload.scenes.push(scene);
      index = payload.scenes.length - 1;
      const option = document.createElement("option");
      option.value = index;
      option.textContent = "live metric frame";
      sceneSelect.appendChild(option);
    } else {
      payload.scenes[index] = scene;
    }
    state.scene = index;
    sceneSelect.value = index;
    if (changedShape) rebuildAll(scene);
    sync();
  }
  let live = null;
  document.getElementById("liveConnect").onclick = () => {
    if (live) {
      live.close();
      live = null;
      document.getElementById("liveConnect").textContent = "Connect";
      return;
    }
    const status = document.getElementById("liveStatus");
    live = new window.QMWLiveFrameClient(document.getElementById("liveUrl").value, acceptLive, text => status.textContent = text);
    live.connect();
    document.getElementById("liveConnect").textContent = "Disconnect";
  };

  let dragging = false;
  let pointerX = 0;
  let pointerY = 0;
  canvas.onpointerdown = event => {
    dragging = true;
    pointerX = event.clientX;
    pointerY = event.clientY;
    canvas.setPointerCapture(event.pointerId);
  };
  canvas.onpointerup = () => dragging = false;
  canvas.onpointermove = event => {
    if (!dragging) return;
    root.rotation.z += (event.clientX - pointerX) * .006;
    root.rotation.x = clamp(root.rotation.x + (event.clientY - pointerY) * .004, -.65, .65);
    pointerX = event.clientX;
    pointerY = event.clientY;
  };
  function resize() {
    const bounds = stage.getBoundingClientRect();
    renderer.setSize(bounds.width, bounds.height, false);
    camera.aspect = bounds.width / bounds.height;
    camera.updateProjectionMatrix();
  }
  new ResizeObserver(resize).observe(stage);
  let lastFrame = performance.now();
  function animate(now) {
    requestAnimationFrame(animate);
    const dt = Math.min(.05, Math.max(0, (now - lastFrame) / 1000));
    lastFrame = now;
    const scene = currentScene(now);
    if (liveAnimation.active) {
      updateSurface(scene, now / 1000);
      updateFlowTracers(scene, dt);
      if (now - liveAnimation.lastAuxiliary >= 100) {
        rebuildAuxiliary(scene);
        liveAnimation.lastAuxiliary = now;
      }
      document.getElementById("revision").textContent = `source r${scene.source_revision} · frame r${scene.revision}`;
    } else {
      updateSurface(scene, now / 1000);
      updateFlowTracers(scene, dt);
    }
    orbitObjects.forEach(orbit => orbit.rotation.z += orbit.userData.orbitRate * dt);
    coreObjects.forEach(core => {
      const pulse = core.userData.baseScale * (1 + .09 * Math.sin(now * .002 * core.userData.coreRate));
      core.scale.setScalar(pulse);
    });
    renderer.render(world, camera);
  }

  preset("analysis");
  sceneSelect.value = state.scene;
  resize();
  requestAnimationFrame(animate);
})();
