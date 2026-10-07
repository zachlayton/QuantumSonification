/* View-only state router. Never emits toward the quantum/field engine. */
autowatch=1;inlets=1;outlets=1;
var ids=["density","potential","contours","spatial_metric","lapse","curvature","hessian_principal","probability_current","vorticity","eigenmodes","trajectory"];
var enabled={},opacity={};for(var i=0;i<ids.length;i++){enabled[ids[i]]=0;opacity[ids[i]]=.78}
function overlay(name,on,alpha){if(ids.indexOf(name)<0){outlet(0,"rejected","unknown_overlay",name);return}enabled[name]=on?1:0;if(alpha!==undefined)opacity[name]=Math.max(0,Math.min(1,alpha));outlet(0,"overlay",name,enabled[name],opacity[name])}
function preset(name){var active=name==="analysis"?["density","potential","contours","spatial_metric","trajectory"]:["potential","contours","probability_current","eigenmodes","trajectory"];if(name!=="analysis"&&name!=="performance"){outlet(0,"rejected","unknown_preset",name);return}for(var i=0;i<ids.length;i++)overlay(ids[i],active.indexOf(ids[i])>=0,opacity[ids[i]]);outlet(0,"preset",name)}
function bang(){for(var i=0;i<ids.length;i++)outlet(0,"overlay",ids[i],enabled[ids[i]],opacity[ids[i]])}
