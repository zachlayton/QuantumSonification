autowatch=1; inlets=1; outlets=1;
function bang(){ seed(); }
function seed(){
    var a=[];
    for(var i=0;i<4096;i++){
        var p=2*Math.PI*i/4096;
        a.push(0.65*Math.sin(p)+0.22*Math.sin(3*p+0.3)+0.1*Math.sin(7*p-0.4));
    }
    new Buffer("qmw_fdg_source").poke(1,0,a);
    outlet(0,"seeded",4096);
}
