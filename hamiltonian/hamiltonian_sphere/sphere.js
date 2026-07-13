let ham = {
  x: 0.56,
  y: 0.37,
  z: 0.07
};

let smoothHam = {
  x: 0.56,
  y: 0.37,
  z: 0.07
};

const sphereRadius = 190;

function setup() {
  createCanvas(windowWidth, windowHeight, WEBGL);
  textFont("Arial");
}

function draw() {
  background(9, 11, 16);

  orbitControl(1.0, 1.0, 0.1);

  // Smooth incoming values so the Hamiltonian field has visible continuity.
  smoothHam.x = lerp(smoothHam.x, ham.x, 0.12);
  smoothHam.y = lerp(smoothHam.y, ham.y, 0.12);
  smoothHam.z = lerp(smoothHam.z, ham.z, 0.12);

  drawAxes();
  drawBlochSphere();
  drawHamiltonianVector();
  drawLabels();
}

function drawAxes() {
  strokeWeight(1.4);

  // X axis
  stroke(215, 95, 95);
  line(-sphereRadius * 1.25, 0, 0, sphereRadius * 1.25, 0, 0);

  // Y axis
  stroke(95, 210, 135);
  line(0, -sphereRadius * 1.25, 0, 0, sphereRadius * 1.25, 0);

  // Z axis
  stroke(95, 145, 235);
  line(0, 0, -sphereRadius * 1.25, 0, 0, sphereRadius * 1.25);
}

function drawBlochSphere() {
  push();

  noFill();
  stroke(88, 102, 128, 85);
  strokeWeight(1);
  sphere(sphereRadius, 36, 24);

  // Equator
  rotateX(HALF_PI);
  ellipse(0, 0, sphereRadius * 2, sphereRadius * 2);

  pop();
}

function drawHamiltonianVector() {
  const x = smoothHam.x;
  const y = smoothHam.y;
  const z = smoothHam.z;

  const magnitude = sqrt(x * x + y * y + z * z);
  const safeMagnitude = max(magnitude, 0.00001);

  // Normalized direction.
  const nx = x / safeMagnitude;
  const ny = y / safeMagnitude;
  const nz = z / safeMagnitude;

  // The arrow is limited to the sphere radius.
  const visualLength = constrain(magnitude * sphereRadius * 1.35, 22, sphereRadius);

  const vx = nx * visualLength;
  const vy = -ny * visualLength;
  const vz = nz * visualLength;

  // Glow line behind the vector.
  stroke(255, 205, 90, 60);
  strokeWeight(10);
  line(0, 0, 0, vx, vy, vz);

  // Primary field vector.
  stroke(255, 222, 122);
  strokeWeight(3);
  line(0, 0, 0, vx, vy, vz);

  // Arrowhead / active field point.
  push();
  translate(vx, vy, vz);

  noStroke();
  fill(255, 234, 150);
  sphere(11);

  pop();

  // Projection point on the sphere:
  // direction is legible even when the Hamiltonian magnitude is small.
  push();
  translate(
    nx * sphereRadius,
    -ny * sphereRadius,
    nz * sphereRadius
  );

  noStroke();
  fill(255, 185, 55, 120);
  sphere(5);

  pop();
}

function drawLabels() {
  resetMatrix();

  const magnitude = sqrt(
    smoothHam.x * smoothHam.x +
    smoothHam.y * smoothHam.y +
    smoothHam.z * smoothHam.z
  );

  const xScreen = 24;
  const yScreen = 52;

  noStroke();
  fill(232, 237, 245);
  textSize(19);
  text("HAMILTONIAN FIELD", xScreen, yScreen);

  textSize(13);
  fill(158, 174, 196);

  text(
    "H = Xσx + Yσy + Zσz",
    xScreen,
    yScreen + 24
  );

  text(
    `Pauli-X drive: ${smoothHam.x.toFixed(3)}`,
    xScreen,
    yScreen + 56
  );

  text(
    `Pauli-Y drive: ${smoothHam.y.toFixed(3)}`,
    xScreen,
    yScreen + 78
  );

  text(
    `Pauli-Z drive: ${smoothHam.z.toFixed(3)}`,
    xScreen,
    yScreen + 100
  );

  fill(255, 222, 122);
  text(
    `Field strength: ${magnitude.toFixed(3)}`,
    xScreen,
    yScreen + 132
  );

  fill(145, 157, 177);
  textSize(12);
  text(
    "Drag to rotate • scroll to zoom",
    xScreen,
    height - 28
  );
}

function windowResized() {
  resizeCanvas(windowWidth, windowHeight);
}

/*
  Temporary keyboard controls for testing before OSC/WebSocket wiring:

  Q / A = Pauli-X up/down
  W / S = Pauli-Y up/down
  E / D = Pauli-Z up/down
*/
function keyPressed() {
  const step = 0.05;

  if (key === "q") ham.x += step;
  if (key === "a") ham.x -= step;

  if (key === "w") ham.y += step;
  if (key === "s") ham.y -= step;

  if (key === "e") ham.z += step;
  if (key === "d") ham.z -= step;

  ham.x = constrain(ham.x, -1.0, 1.0);
  ham.y = constrain(ham.y, -1.0, 1.0);
  ham.z = constrain(ham.z, -1.0, 1.0);
}

/*
  This is the function the OSC/WebSocket bridge will call later.

  Example:
  updateHamiltonian({
    x: 0.562,
    y: 0.372,
    z: 0.066
  });
*/
function updateHamiltonian(data) {
  if (typeof data.x === "number") ham.x = data.x;
  if (typeof data.y === "number") ham.y = data.y;
  if (typeof data.z === "number") ham.z = data.z;
}