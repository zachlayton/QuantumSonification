/* Authoritative-frame to named float32 jit.matrix adapter. No field math here. */
autowatch=1; inlets=1; outlets=2;
var lastRevision=-1,lastSourceRevision=-1;
var scalar=["density","potential","sigma","lapse","determinant","curvature","potential_laplacian","vorticity"];
function frame(){
  var text=arrayfromargs(arguments).join(" "),p;
  try{p=JSON.parse(text)}catch(e){outlet(1,"rejected","json");return}
  if(p.contract!=="qmw_metric.shader_frame.v1"){outlet(1,"rejected","contract");return}
  if(p.revision<=lastRevision||p.source_revision<lastSourceRevision){outlet(1,"stale",p.revision);return}
  lastRevision=p.revision;lastSourceRevision=p.source_revision;
  for(var i=0;i<scalar.length;i++)publishScalar(scalar[i],p.arrays[scalar[i]],p.revision);
  publishComponents("metric",p.arrays.metric,p.revision);
  publishComponents("inverse_metric",p.arrays.inverse_metric,p.revision);
  publishComponents("hessian",p.arrays.hessian,p.revision);
  publishVector("grad_potential",p.arrays.grad_potential,p.revision);
  publishVector("probability_current",p.arrays.probability_current,p.revision);
  publishVector("phase_connection",p.arrays.phase_connection,p.revision);
  for(var m=0;m<p.arrays.mode_shapes.length;m++)publishScalar("eigenmode_"+m,p.arrays.mode_shapes[m],p.revision);
  publishTrajectory(p.arrays.trajectory_positions,p.revision);
  outlet(0,"commit",p.revision);
  outlet(1,"accepted",p.revision,p.source_revision,p.time);
}
function publishScalar(name,a,revision){var ny=a.length,nx=a[0].length,m=new JitterMatrix("qmw_metric_"+name,1,"float32",nx,ny);for(var y=0;y<ny;y++)for(var x=0;x<nx;x++)m.setcell2d(x,y,a[y][x]);outlet(0,name,m.name,revision)}
function publishVector(name,a,revision){for(var i=0;i<2;i++)publishScalar(name+"_"+(i?"y":"x"),a[i],revision)}
function publishComponents(name,a,revision){for(var i=0;i<2;i++)for(var j=0;j<2;j++)publishScalar(name+"_"+i+j,a[i][j],revision)}
function publishTrajectory(a,revision){var m=new JitterMatrix("qmw_metric_trajectory",2,"float32",Math.max(1,a.length));for(var i=0;i<a.length;i++)m.setcell1d(i,a[i]);outlet(0,"trajectory",m.name,revision)}
