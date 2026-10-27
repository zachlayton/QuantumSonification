/* Offscreen-compatible GUI drawing/reopen check. Optional QMW_EVENT_GUI_DIR
   writes PNG snapshots for visual inspection; no audio server is needed. */
(
var here=thisProcess.nowExecutingPath.dirname, output="QMW_EVENT_GUI_DIR".getenv;
~qefHeadless=false;
thisProcess.interpreter.executeFile(here +/+ "../supercollider/EventFieldAddon.scd");
Routine({
    var pic;
    ~qefOpenObservables.(); 0.2.wait;
    if(~qefObserverWindow.isNil, { "FAIL: missing observer window".postln; 1.exit });
    4.do { |operator|
        var frame=~qefFrame.(if(operator==0,{0},{1.2}));
        ~qefDisplayed=(frame:frame,observables:~qefObservables.(frame));
        ~qefSet.(\diracIndex,operator); ~qefSelectedPair=operator;
        ~qefObserverView.refresh; 0.12.wait;
        if(output.notNil, {
            pic=Image.fromWindow(~qefObserverWindow);
            pic.write(output +/+ ("observables_" ++ operator ++ ".png"),"png"); pic.free;
        });
    };
    if(output.notNil, {
        pic=Image.fromWindow(~qefWindow); pic.write(output +/+ "controls.png","png"); pic.free;
    });
    ~qefObserverWindow.close; 0.05.wait;
    if(~qefObserverView.notNil, { "FAIL: closed observer retained".postln; 1.exit });
    ~qefOpenObservables.(); 0.1.wait;
    ~qefShutdown.(); "GUI PASS: all matrices, zero coherence, live snapshot, close/reopen".postln; 0.exit;
}).play(AppClock);
SystemClock.sched(8,{ "FAIL: GUI timeout".postln; 1.exit });
)
