/* Four audition modes for the v4 dual-rail complex laboratory. */
autowatch = 1; inlets = 1; outlets = 3;
function feedback(message, value){ outlet(0, message, value); }
function matrix(message, value){
    if(arguments.length > 1) outlet(1, message, value);
    else outlet(1, message);
}
function mode1(){
    matrix("identity"); matrix("imagdepth",0);
    feedback("hilbertdepth",1); feedback("phasedepth",1);
    feedback("complexmemory",0); feedback("mode",2);
    outlet(2,["mode",1,"analytic_rotation"]);
}
function mode2(){
    matrix("fundamental_fifth"); matrix("imagdepth",1);
    feedback("hilbertdepth",1); feedback("phasedepth",1);
    feedback("complexmemory",0.5); feedback("mode",2);
    outlet(2,["mode",2,"coherence_pair"]);
}
function mode3(){
    matrix("external"); matrix("imagdepth",1);
    feedback("hilbertdepth",1); feedback("phasedepth",1);
    feedback("complexmemory",0.5); feedback("mode",2);
    outlet(2,["mode",3,"full_density_operator"]);
}
function mode4(){
    feedback("hilbertdepth",1); feedback("phasedepth",1);
    feedback("complexmemory",1); feedback("mode",2);
    outlet(2,["mode",4,"dual_rail_complex_memory"]);
}
function anything(){ outlet(2,["error","unknown_mode",messagename]); }
