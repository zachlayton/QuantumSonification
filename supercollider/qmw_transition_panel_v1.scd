/* Opt-in stereo note/body junction. No rho reconstruction or quantum controls.
   Shared SIMPLE fuzz and main FX sends. Solo preserves existing FX returns.
   Ringz decaytime is T60 = amplitude tau * ln(1000). */
(
var generation, finite, validPacket, install, adapterFile, priorQMWRender, wrappedQMWRender, initial, previousControls, previousRevision;
adapterFile = "QMW_NOTE_TIMBRE_SC_FILE".getenv ? thisProcess.nowExecutingPath;
previousControls=~qtpControls !? _.copy;
previousRevision=(~qtpAppliedRevision ? -1).max(~qtpConfigRevision ? 0);
~qtpDetachNavigation !? { ~qtpDetachNavigation.value };
~qtpRemove !? { ~qtpRemove.value };
generation = Object.new;
~qtpGeneration = generation;
~qtpArmed = false;
~qtpSolo = ~qtpSolo ? false;
~qtpHold = false;
~qtpControls = [0,0,0,2,0.0,1e-8,1e-8,0,0,0,1,10.0,220.0,0,0.25,4,0,1,1];
initial="QMW_TRANSITION_INITIAL_CONTROLS".getenv;
if(initial.notNil, {
    initial=initial.split($,).collect(_.asFloat);
    if(initial.size == 19, {
        [0,1,2,3,7,8,9,10,13,15,16,17,18].do { |i| initial[i]=initial[i].asInteger };
        initial[0]=0; ~qtpControls=initial;
    });
});
if(previousControls.notNil,{~qtpControls=previousControls});
~qtpCandidates=[]; ~qtpFollowCycle=0; ~qtpQMWTriggers=0; ~qtpFollowOnsets=0; ~qtpLastQMWAt = -1e9;
~qtpOnsetLog=nil;
~qtpPacket = nil; ~qtpCells = nil; ~qtpView = 0; ~qtpLastNoteLabel = "No musical event yet";
~qtpDrawCount = 0; ~qtpSourceHash = ""; ~qtpSaveLabel = "Save exports exact H, rho, A and observation to the session folder.";
~qtpConfigRevision = previousRevision.max(0); ~qtpAppliedRevision = -1;
~qtpSession = nil; ~qtpRetired = Set.new; ~qtpAllowNewSession = false;
~qtpSequence = -1; ~qtpObservedRevision = -1; ~qtpSourceRevision = -1;
~qtpLastValidAt = -1e9; ~qtpLastEventAt = -1e9;
~qtpNodes = List.new; ~qtpLevel = ~qtpLevel ? 1.0;
~qtpInstalled = false; ~qtpSourceLabel = "Waiting for actual runtime H/rho";
~qtpConfigTarget = NetAddr("127.0.0.1", 17935);
~qtpSoundChoice=~qtpSoundChoice ? 2;
~qtpChordMode=~qtpSoundChoice>0; ~qtpChordAuto=~qtpChordAuto ? true; ~qtpChordSelected=~qtpChordSelected ? 0; ~qtpChordCurrent=nil;
~qtpHarmony=nil; ~qtpChordCells=nil; ~qtpHarmonyWindow=nil; ~qtpHarmonyView=nil;
~qtpPositionDepth=~qtpPositionDepth ? 0.0; ~qtpSizeDepth=~qtpSizeDepth ? 0.0; ~qtpCVSmooth=~qtpCVSmooth ? 0.5;
~qtpPositionOwned=false; ~qtpSizeOwned=false; ~qtpPositionCV=0.5; ~qtpSizeCV=0.0;
~qtpEveryQMW=~qtpEveryQMW ? false;
~qtpGrainMs=~qtpGrainMs ? 45.0; ~qtpGrainRate=~qtpGrainRate ? 32.0;
~qtpGrainTexture=~qtpGrainTexture ? 0.7; ~qtpGrainSpread=~qtpGrainSpread ? 0.7;
~qtpGrainSizeDepth=~qtpGrainSizeDepth ? 0.0;
~qtpGrainWindow=nil;
~qtpGrainSettings={
    var cv=if(~qtpHarmony.notNil,{~qtpHarmony[2]},{0.5});
    // The coherence observation changes grain size in octaves around the knob.
    // Read exactly once per QMW onset; HOLD therefore holds this mapping too.
    var size=(~qtpGrainMs*(2**(~qtpGrainSizeDepth*(2*cv-1)))).clip(6,250);
    [size,~qtpGrainRate.clip(2,120),~qtpGrainTexture.clip(0,4),~qtpGrainSpread.clip(0,1)]
};
~qtpOpenGrains={
    if(~qtpGrainWindow.notNil,{~qtpGrainWindow.front},{
        var w,text;
        w=Window("QMW GRANULAR CHORD VOICE",Rect(170,150,580,410)).background_(Color.fromHexString("111a24")).front;
        ~qtpGrainWindow=w;
        text={|rect,string,size=12|StaticText(w,rect).string_(string).font_(Font("Helvetica Neue",size)).stringColor_(Color.fromHexString("dde6ec"))};
        text.(Rect(20,12,540,30),"GRANULAR CHORD VOICE",21);
        text.(Rect(20,50,540,48),"A short grain cloud starts on each admitted QMW attack.\nIts four carrier pitches come from the current chord cell.");
        EZSlider(w,Rect(20,110,540,30),"Grain size ms",ControlSpec(6,250,\exp),{|v|~qtpGrainMs=v.value},~qtpGrainMs,labelWidth:150);
        EZSlider(w,Rect(20,152,540,30),"Grains/sec per note",ControlSpec(2,120,\exp),{|v|~qtpGrainRate=v.value},~qtpGrainRate,labelWidth:150);
        EZSlider(w,Rect(20,194,540,30),"Texture / FM",ControlSpec(0,4,\lin),{|v|~qtpGrainTexture=v.value},~qtpGrainTexture,labelWidth:150);
        EZSlider(w,Rect(20,236,540,30),"Stereo spread",ControlSpec(0,1,\lin),{|v|~qtpGrainSpread=v.value},~qtpGrainSpread,labelWidth:150);
        EZSlider(w,Rect(20,278,540,30),"Density → size oct",ControlSpec(-2,2,\lin),{|v|~qtpGrainSizeDepth=v.value},~qtpGrainSizeDepth,labelWidth:150);
        text.(Rect(20,322,540,70),"Depth 0 keeps grain size fixed. Positive/negative depth follows/inverts coherence.\nNote duration sets the cloud's duration; grain size sets each particle's length.\nGrain rhythm and FM texture are sound design. No sample file is required.\nThe same SIMPLE fuzz, FX send, Solo and sound gates apply.",11);
        w.view.children.do {|view|if(view.isKindOf(CompositeView),{view.children.do {|child|
            if(child.isKindOf(StaticText),{child.stringColor_(Color.fromHexString("dde6ec"))});
        }})};
        w.onClose_({~qtpGrainWindow=nil});
    });
};

~qtpRestoreClouds={
    ~qriCloudsNode !? { |node|
        if(~qtpPositionOwned,{node.set(\pos,~qriCloudsPosition ? 0.5)});
        if(~qtpSizeOwned,{node.set(\size,~qriCloudsSize ? 0.45)});
    };
    ~qtpPositionOwned=false; ~qtpSizeOwned=false;
};
~qtpUpdateClouds={
    var fresh=~qtpHarmony.notNil and: {Main.elapsedTime-~qtpLastValidAt<1.5};
    var alpha=1-exp(-0.1/(~qtpCVSmooth.max(0.02))), pos, size;
    if(fresh, {
        ~qtpPositionCV=~qtpPositionCV+(alpha*(~qtpHarmony[1]-~qtpPositionCV));
        ~qtpSizeCV=~qtpSizeCV+(alpha*(~qtpHarmony[2]-~qtpSizeCV));
    });
    pos=((~qriCloudsPosition ? 0.5)+(~qtpPositionDepth*(2*~qtpPositionCV-1))).clip(0,1);
    size=((~qriCloudsSize ? 0.45)+(~qtpSizeDepth*(2*~qtpSizeCV-1))).clip(0,1);
    if(fresh, {
        ~qriCloudsNode !? { |node|
            if(~qtpPositionDepth != 0, {node.set(\pos,pos);~qtpPositionOwned=true}, {
                if(~qtpPositionOwned,{node.set(\pos,~qriCloudsPosition ? 0.5);~qtpPositionOwned=false});
            });
            if(~qtpSizeDepth != 0, {node.set(\size,size);~qtpSizeOwned=true}, {
                if(~qtpSizeOwned,{node.set(\size,~qriCloudsSize ? 0.45);~qtpSizeOwned=false});
            });
        };
    }, {~qtpRestoreClouds.value});
    ~qtpCVReadout !? { |view|
        view.string_("Population position CV " ++ ~qtpPositionCV.round(0.001)
            ++ " / coherence size CV " ++ ~qtpSizeCV.round(0.001)
            ++ "\nClouds position " ++ pos.round(0.001) ++ " / size " ++ size.round(0.001)
            ++ if(fresh,{""},{" / stale: base values restored"}));
    };
};
~qtpOpenHarmony={
    if(~qtpHarmonyWindow.notNil,{~qtpHarmonyWindow.front},{
        var w, text;
        w=Window("QMW CHORD MATRIX / FX",Rect(100,90,990,675)).background_(Color.fromHexString("111a24")).front;
        ~qtpHarmonyWindow=w;
        text={|rect,string,size=12|StaticText(w,rect).string_(string).font_(Font("Helvetica Neue",size)).stringColor_(Color.fromHexString("dde6ec"))};
        text.(Rect(20,12,940,32),"FOUR-NOTE CHORD MATRIX",22);
        text.(Rect(20,50,940,42),"Rows: chord quality. Columns: inversion. Brightness: density + transition weight.\nThis is an explicit musical lookup; these ratios are not quantum energy gaps.");
        PopUpMenu(w,Rect(20,100,225,30)).items_(["Single transition","Four-note chords","Granular chords"])
            .value_(~qtpSoundChoice).action_({|v|~qtpSoundChoice=v.value;~qtpChordMode=v.value>0});
        ~qtpChordFollowButton=Button(w,Rect(255,100,225,30)).states_([["SELECT CELL"],["FOLLOW MATRIX",Color.black,Color.fromHexString("75b9ed")]])
            .value_(~qtpChordAuto.asInteger).action_({|v|~qtpChordAuto=v.value==1});
        ~qtpHarmonyView=UserView(w,Rect(20,145,465,330)).background_(Color.fromHexString("18232e"));
        ~qtpHarmonyView.drawFunc_({
            var rows=~qtpChordCells, qualities=["MAJ 7","MIN 7","DOM 7","HALF DIM"], chosen;
            chosen=if(~qtpChordAuto,{~qtpChordCurrent ? 0},{~qtpChordSelected});
            Pen.font=Font("Helvetica Neue",11);
            16.do { |i|
                var x=i%4,y=(i/4).floor.asInteger, rect=Rect(5+(x*114),5+(y*80),109,74);
                var weight=if(rows.notNil,{rows[i][3]},{0});
                Pen.color=Color.hsv(0.52,0.6,0.18+(weight.sqrt*0.7));Pen.fillRect(rect);
                Pen.color=Color.white;
                Pen.stringAtPoint(qualities[y] ++ " / inv " ++ x,Point(rect.left+5,rect.top+7));
                if(rows.notNil,{
                    Pen.stringAtPoint(rows[i][0].round(0.1).asString ++ " Hz root",Point(rect.left+5,rect.top+26));
                    Pen.stringAtPoint((100*weight).round(0.1).asString ++ "% weight",Point(rect.left+5,rect.top+45));
                });
                if(i==chosen,{Pen.width=2;Pen.color=Color.fromHexString("f4ce80");Pen.strokeRect(rect.insetBy(1,1))});
            };
        });
        ~qtpHarmonyView.mouseDownAction_({|view,x,y|
            var column=((x-5)/114).floor.asInteger,row=((y-5)/80).floor.asInteger;
            if(column.inclusivelyBetween(0,3) and: {row.inclusivelyBetween(0,3)}, {
                ~qtpChordSelected=(row*4)+column;~qtpChordAuto=false;
                ~qtpChordFollowButton.value_(0); view.refresh;
            });
        });
        text.(Rect(20,490,465,110),"Key: population centroid shifts the base pitch by up to one octave.\nNote balance: four qubit populations.\nActivity changes cell weights; density changes key and cell preference.\nAutomatic selection uses 10% hysteresis to avoid rapid switching.\nBase pitch and duration remain in the transition panel.",11);
        text.(Rect(515,100,450,30),"DENSITY CV → CLOUDS",18);
        EZSlider(w,Rect(515,145,450,30),"Position depth",ControlSpec(-1,1,\lin),{|v|~qtpPositionDepth=v.value},~qtpPositionDepth,labelWidth:125);
        EZSlider(w,Rect(515,187,450,30),"Grain size depth",ControlSpec(-1,1,\lin),{|v|~qtpSizeDepth=v.value},~qtpSizeDepth,labelWidth:125);
        EZSlider(w,Rect(515,229,450,30),"Smoothing sec",ControlSpec(0.02,5,\exp),{|v|~qtpCVSmooth=v.value},~qtpCVSmooth,labelWidth:125);
        ~qtpCVReadout=text.(Rect(515,270,450,65),"Waiting for density CV");
        text.(Rect(515,338,450,70),"Depth 0 switches modulation off. Negative depth inverts it.\nClouds knobs remain the base values; final values stay within 0–1.\nStale data or closing TRANSITIONS restores the base values.",11);
        Button(w,Rect(515,420,220,30)).states_([["MAIN CLOUDS / VST FX"]]).action_({~qriOpenFXControls !? _.value});
        Button(w,Rect(745,420,220,30)).states_([["SIMPLE FUZZ / FX SENDS"]]).action_({~qriOpenPanel !? _.value});
        text.(Rect(515,462,450,74),"Routing: transition → SIMPLE fuzz → dry + main FX send.\nRaise SIMPLE's FX send, then Clouds or VST return.\nSolo transitions keeps the existing effect returns audible.",11);
        Button(w,Rect(515,548,450,30)).states_([["RHYTHM: RESPECT RATE / VOICE CAPS"],["RHYTHM: EVERY QMW EVENT (steal oldest tail)"]])
            .value_(~qtpEveryQMW.asInteger).action_({|v|~qtpEveryQMW=v.value==1});
        text.(Rect(515,588,450,50),"Every event bypasses the transition rate cap and replaces the oldest\ntail at the voice limit. Observable filters and sound gates still apply.",11);
        Button(w,Rect(20,610,220,30)).states_([["SAVE EXACT FRAME"]]).action_({~qtpConfigTarget.sendMsg("/qmw/transitions/v1/save")});
        Button(w,Rect(250,610,230,30)).states_([["GRANULAR VOICE CONTROLS"]]).action_({~qtpOpenGrains.value});
        w.view.children.do { |view|
            if(view.isKindOf(CompositeView), {view.children.do { |child|
                if(child.isKindOf(StaticText),{child.stringColor_(Color.fromHexString("dde6ec"))});
            }});
        };
        w.onClose_({~qtpHarmonyWindow=nil;~qtpHarmonyView=nil;~qtpCVReadout=nil});
    });
};



finite = { |value| value.isNumber and: { value.abs < 1e12 } };
validPacket = { |a|
    var good = true, strings = [1,8,22], require, modes, changedSession, seen;
    ~qtpRejectReason = nil;
    require = { |condition, reason|
        if(good and: { condition.not }, { good=false; ~qtpRejectReason=reason }); good
    };
    require.(a.size >= 1822, "incomplete v3 frame");
    if(good, {
        require.([0,1].includes(a[1624]), "timing mode");
        require.(finite.(a[1625]) and: { a[1625] >= 0 and: { a[1625] <= 240 and: { a[1625].asInteger == a[1625] } } }, "candidate count");
        require.(a.size == (1822+(a[1625]*5)), "incomplete candidate list");
    });
    if(good, {
        strings.do { |i|
            if(a[i].isKindOf(Symbol), { a[i]=a[i].asString });
            require.(a[i].isKindOf(String) and: { a[i].size > 0 }, "text field");
        };
        a.do { |value,i| if(strings.includes(i).not, { require.(finite.(value), "nonfinite field") }) };
    });
    if(good, {
        require.(a[0] == 3 and: { a[23] == 1 }, "schema/hbar");
        [2,3,4,6,9].do { |i| require.(a[i] >= 0 and: { a[i].asInteger == a[i] }, "revision/count") };
        require.([0,1].includes(a[7]) and: { [0,1].includes(a[15]) }, "hold/excitation flags");
        require.(a[16] >= 1 and: { a[16] <= 8 and: { a[16].asInteger == a[16] } }, "voice limit");
        require.(a[17] >= 0.25 and: { a[17] <= 10 }, "musical rate cap");
        require.(a[9] <= 240 and: { a[22].size == 64 and: { a[4] <= a[3] } }, "source metadata");
        require.(~qtpRetired.includes(a[1]).not, "retired session");
        changedSession = ~qtpSession.notNil and: { ~qtpSession != a[1] };
        require.(changedSession.not or: { ~qtpAllowNewSession }, "new session: refresh connection first");
        if(changedSession.not, {
            require.(a[2] > ~qtpSequence, "old sequence");
            require.(a[6] >= ~qtpAppliedRevision, "old configuration");
            require.(a[3] > ~qtpObservedRevision, "old source observation");
            require.(a[7] == 1 or: { a[4] >= ~qtpSourceRevision }, "source revision moved backward");
        });
        if(a[10] == -1, {
            require.(a[11] == -1 and: { a[12] == 0 and: { a[13] == 0 and: { a[14] == 0 } } }, "no-note fields");
        }, {
            [10,11].do { |i| require.(a[i] >= 0 and: { a[i] < 16 and: { a[i].asInteger == a[i] } }, "note endpoint") };
            require.(a[10] != a[11], "diagonal note");
            require.(a[12] > 0 and: { a[12] < (s.sampleRate * 0.45) }, "note frequency");
            require.(a[13] > 0 and: { a[13] <= 1.000001 }, "note diagnostic strength");
            require.(a[14] >= 0.000999 and: { a[14] <= 2 }, "note duration");
        });
        require.(if(a[1624] == 1,{a[10] == -1},{a[1625] == 0}), "competing onset clocks");
        seen=Set.new;
        if(a[1625] > 0, {
            a.copyRange(1626,1625+(a[1625]*5)).clump(5).do { |candidate|
                [0,1].do { |i| require.(candidate[i] >= 0 and: { candidate[i] < 16 and: { candidate[i].asInteger == candidate[i] } }, "candidate endpoint") };
                require.(candidate[0] != candidate[1], "diagonal candidate");
                require.(candidate[2] > 0 and: { candidate[2] < (s.sampleRate*0.45) }, "candidate pitch");
                require.(candidate[3] > 0 and: { candidate[3] <= 1.000001 }, "candidate strength");
                require.(candidate[4] >= 0.000999 and: { candidate[4] <= 2 }, "candidate duration");
                if(good, {
                    var key=(candidate[1]*16)+candidate[0];
                    require.(seen.includes(key).not, "duplicate candidate"); seen.add(key);
                    require.((candidate[3]-a[88+(key*6)+5]).abs < 1e-5, "candidate activity mismatch");
                });
            };
        });
        {
            var h=a.copyRange(1626+(a[1625]*5),a.size-1), chords=h.copyRange(4,195).clump(12);
            require.(h[0]==1 and: {h[1].inclusivelyBetween(0,1)} and: {h[2].inclusivelyBetween(0,1)}
                and: {h[3].asInteger==h[3] and: {h[3].inclusivelyBetween(0,15)}}, "harmony metadata");
            require.((chords.collect {|r|r[3]}.sum-1).abs<1e-5,"chord weights");
            chords.do { |r,i|
                require.(r[0]>0 and: {r[1]==(i/4).floor} and: {r[2]==(i%4)} and: {r[3]>=0},"chord identity");
                require.(r.copyRange(4,7).every {|hz|hz>0 and: {hz<(s.sampleRate*0.45)}},"chord frequencies");
                require.(r.copyRange(8,11).every {|gain|gain>0} and: {(r.copyRange(8,11).sum-1).abs<1e-5},"chord amplitudes");
            };
        }.value;
        modes = a.copyRange(24,87).clump(4);
        modes.do { |row|
            require.(row[0] > 0 and: { row[0] < (s.sampleRate*0.45) }, "body frequency");
            require.(row[1] >= 0 and: { row[1] <= 1.000001 }, "body amplitude");
            require.(row[2] > 0 and: { row[2] <= 2 and: { row[3] == 0 } }, "body damping/phase");
        };
        a.copyRange(88,1623).clump(6).do { |cell| require.(cell[5] >= 0, "negative activity") };
    });
    good
};
~qtpValidatePacket = validPacket;
~qtpLastRejectAt = -1e9;
~qtpSendConfig = {
    ~qtpConfigRevision = (~qtpConfigRevision.max(~qtpAppliedRevision)) + 1;
    ~qtpControls[0] = ~qtpConfigRevision;
    ~qtpConfigTarget.sendMsg("/qmw/transitions/v2/config", *~qtpControls);
};

// Refresh keeps accepting newer frames from the current source. Retire its
// identity only when a different, validated source actually replaces it.
~qtpReconnect = {
    ~qtpAllowNewSession = true;
    ~qtpArmed = false; ~qtpArmButton !? { |v| v.value_(0) };
    ~qtpVoiceGroup !? _.freeAll;
    ~qtpNodes.clear;
    ~qtpSendConfig.value;
    ~qtpSourceLabel = "Refreshing connection: waiting for the next source frame";
};
~qtpCanSound = {
    ~qtpInstalled and: { ~qtpArmed and: { ~qrmSonify ? false } }
        and: { ~qriEnabled ? false } and: { ~qriPlucksEnabled.notNil and: { ~qriPlucksEnabled.value } }
        and: { Main.elapsedTime - ~qtpLastValidAt < 1.5 }
        and: { ~qtpAppliedRevision >= ~qtpConfigRevision }
};

// The native render callback owns onsets. Analysis packets provide candidates.
~qtpChooseFollow = { |event, level=1.0, now|
    var a=~qtpPacket, answer=nil, candidates=~qtpCandidates;
    now=now ? Main.elapsedTime;
    ~qtpNodes=~qtpNodes.select { |node| node.isPlaying };
    if(a.notNil and: { a[1624] == 1 } and: { ~qtpControls[18] == 1 }
        and: { ~qtpCanSound.value } and: { a[6] == ~qtpConfigRevision }
        and: { candidates.notEmpty } and: { (event[\energy] ? 0) > 0 }
        and: { level > 0 } and: { (~qriEffectiveVoiceGains.value[0] ? 0) > 0 }
        and: { ~qtpEveryQMW or: {~qtpNodes.size < a[16]} }
        and: { ~qtpEveryQMW or: {(now-~qtpLastEventAt) >= (1/a[17])} }, {
        answer=candidates[if(~qtpControls[8] == 1, {~qtpFollowCycle % candidates.size}, {0})];
    });
    answer
};

~qtpEmit = { |candidate, clockName, event=nil|
    var a=~qtpPacket, rows, node, now=Main.elapsedTime, emitted=false, fields, chord=nil, chordIndex= -1, grainSettings=nil, synthName;
    ~qtpNodes=~qtpNodes.select { |active| active.isPlaying };
    if(a.notNil and: { ~qtpCanSound.value }
        and: { (~qriEffectiveVoiceGains.value[0] ? 0) > 0 }
        and: { (~qtpEveryQMW and: {clockName=="QMW"}) or: {~qtpNodes.size < a[16]} }, {
        if(~qtpNodes.size>=a[16],{~qtpNodes.removeAt(0).free});
        rows=a.copyRange(24,87).clump(4);
        // Inherit any native bundle; do not add another clock or latency.
        if(~qtpChordMode and: {~qtpChordCells.notNil}, {
            chordIndex=if(~qtpChordAuto,{~qtpChordCurrent ? 0},{~qtpChordSelected});
            chord=~qtpChordCells[chordIndex];
            synthName=if(~qtpSoundChoice==2,{\qtpGranularChordV1},{\qtpChordEventV1});
            grainSettings=~qtpGrainSettings.value;
            node=Synth.tail(~qtpVoiceGroup,synthName,[
                \outBus,~qtpPrivateBus.index,\strength,candidate[3],\duration,~qtpControls[14],
                \chordHz,chord.copyRange(4,7),\chordGains,chord.copyRange(8,11),
                \gains,rows.collect {|r|r[1]}] ++ if(~qtpSoundChoice==2,{[
                \grainMs,grainSettings[0],\grainRate,grainSettings[1],
                \texture,grainSettings[2],\spread,grainSettings[3]]},{[]})).register;
        }, {
        node=Synth.tail(~qtpVoiceGroup,\qtpEventV1,[
            \outBus,~qtpPrivateBus.index,\noteHz,candidate[2],\strength,candidate[3],
            \excitationMode,a[15],\duration,candidate[4],
            \frequencies,rows.collect { |r| r[0] },
            \gains,rows.collect { |r| r[1] },\tau,rows.collect { |r| r[2] }]).register;
        });
        ~qtpNodes.add(node); ~qtpLastEventAt=now;
        ~qtpLastNoteLabel=(candidate[0]+1).asString ++ " > " ++ (candidate[1]+1)
            ++ "   " ++ if(chord.notNil,{["maj7","min7","dom7","half dim"][chord[1].asInteger] ++ " inv " ++ chord[2].asInteger ++ " / " ++ chord.copyRange(4,7).round(0.1)},{candidate[2].round(0.01).asString ++ " Hz"}) ++ " / " ++ clockName ++ if(~qtpSoundChoice==2,{" / GRAINS"},{""});
        fields=[clockName,now,a[1],a[2],a[4],a[6],~qtpQMWTriggers,
            if(event.notNil,{event[\channel] ? "-"},{"-"}),
            if(event.notNil,{event[\kind] ? "-"},{"-"}),
            candidate[0],candidate[1],candidate[2],candidate[3],chordIndex,
            if(chord.notNil,{chord.copyRange(4,7).join(",")},{"-"}),
            ~qtpSoundChoice,if(grainSettings.notNil and: {~qtpSoundChoice==2},{grainSettings.join(",")},{"-"})];
        ~qtpOnsetLog !? { |file|
            file.write(fields.collect { |value| value.asString.replace("\t"," ").replace("\n"," ") }.join("\t") ++ "\n");
            file.flush;
        };
        emitted=true;
    });
    emitted
};

~qtpOnQMW = { |event, level=1.0|
    var candidate;
    if(~qtpGeneration === generation and: { ~qtpInstalled }, {
        ~qtpQMWTriggers=~qtpQMWTriggers+1;
        if(~qtpQMWTriggers == 1,{"QMW_TRANSITION_QMW_TRIGGER_RECEIVED".postln});
        ~qtpLastQMWAt=Main.elapsedTime;
        candidate=~qtpChooseFollow.(event,level);
        if(candidate.notNil, {
            if(~qtpEmit.(candidate,"QMW",event), {
                ~qtpFollowCycle=~qtpFollowCycle+1;
                ~qtpFollowOnsets=~qtpFollowOnsets+1;
                if(~qtpFollowOnsets == 1,{"QMW_TRANSITION_FOLLOW_ONSET_RENDERED".postln});
            });
        });
    });
};

~qtpInstallFollow = {
    if(~qriRenderEventUnsafe.isKindOf(Function), {
        priorQMWRender=~qriRenderEventUnsafe;
        wrappedQMWRender={ |event,level=1.0|
            var result=priorQMWRender.value(event,level);
            // Local V3 clock closures all dispatch through this seam. Preserve
            // the existing renderer, its arguments, and its return value.
            if(~qtpGeneration === generation, {
                try { ~qtpOnQMW.(event,level) } { |error| error.reportError };
            });
            result
        };
        ~qriRenderEventUnsafe=wrappedQMWRender;
        ~qtpDetachFollow={
            if(~qriRenderEventUnsafe === wrappedQMWRender, {~qriRenderEventUnsafe=priorQMWRender});
        };
        "QMW_TRANSITION_FOLLOW_CONNECTED: native render seam".postln;
    }, { "QMW TRANSITIONS: QMW render trigger unavailable; FOLLOW stays silent.".warn });
};

~qtpRemove = {
    ~qtpArmed = false; ~qtpInstalled = false; ~qtpGeneration = nil;
    ~qtpDetachFollow !? {~qtpDetachFollow.value}; ~qtpDetachFollow=nil;
    ~qtpOnsetLog !? _.close; ~qtpOnsetLog=nil;
    OSCdef(\qtpCompleteFrame).free;
    // Removing the final selector restores the original stereo mix. Free only
    // this adapter's groups/buses; never stop server, old sources, or authority.
    ~qtpRouterGroup !? _.free; ~qtpRouterGroup = nil;
    ~qtpVoiceGroup !? _.free; ~qtpVoiceGroup = nil;
    OSCdef(\qtpSaved).free;
    ~qtpFeedGroup !? _.free; ~qtpFeedGroup=nil;
    ~qtpCaptureGroup !? _.free; ~qtpCaptureGroup=nil;
    ~qtpSelectedBus !? _.free; ~qtpSelectedBus=nil;
    ~qtpBeforeBus !? _.free; ~qtpBeforeBus=nil;
    ~qtpWetBus !? _.free; ~qtpWetBus=nil;
    ~qtpRestoreClouds !? _.value;
    ~qtpGrainWindow !? _.close; ~qtpGrainWindow=nil;
    ~qtpHarmonyWindow !? _.close; ~qtpHarmonyWindow=nil;
    ~qtpPrivateBus !? _.free; ~qtpPrivateBus = nil;
    ~qtpGateBus !? _.free; ~qtpGateBus = nil;
    ~qtpNodes !? _.clear;
    ~qtpWindow !? { |v| v.onClose_(nil); v.close }; ~qtpWindow = nil;
};

// Keep a navigation-only recovery entry after the opt-in layer is removed.
// Bringing an existing panel forward changes no audio controls. Reopening a
// removed layer evaluates this addon again and therefore starts DISARMED.
~qtpOpenPanel = {
    if(~qtpWindow.notNil, { ~qtpWindow.front }, {
        if(adapterFile.notNil and: { File.exists(adapterFile) }, {
            thisProcess.interpreter.executeFile(adapterFile);
        }, { "QMW TRANSITIONS: recovery requires its original addon path.".warn });
    });
};
~qtpEnsureWorkspaceEntry = {
    if(~qmwuWorkspaceWindow.notNil and: { ~qtpWorkspaceParent !== ~qmwuWorkspaceWindow }, {
        ~qtpWorkspaceParent = ~qmwuWorkspaceWindow;
        ~qtpWorkspaceEntry = Button(~qmwuWorkspaceWindow,Rect(18,336,204,34))
            .states_([["TRANSITIONS",Color.white,Color.fromHexString("17465b")]])
            .font_(Font("Helvetica Neue",11,true))
            .toolTip_("Bring the note/body panel forward. A removed layer reopens disarmed.")
            .action_({ ~qtpOpenPanel.value });
    });
};
~qtpInstallNavigation = {
    var owner = ~qmwuWorkspaceButton, originalAction, wrappedAction;
    if(owner.notNil, {
        originalAction = owner.action;
        wrappedAction = { |view|
            originalAction !? { |action| action.value(view) };
            ~qtpEnsureWorkspaceEntry.value;
        };
        owner.action_(wrappedAction);
        ~qtpDetachNavigation = {
            if(owner.action === wrappedAction, { owner.action_(originalAction) });
            if(~qtpWorkspaceParent.notNil and: { ~qtpWorkspaceParent === ~qmwuWorkspaceWindow }, {
                ~qtpWorkspaceEntry !? _.remove;
            });
            ~qtpWorkspaceParent=nil; ~qtpWorkspaceEntry=nil;
        };
        ~qtpEnsureWorkspaceEntry.value;
    }, { "QMW TRANSITIONS: WORKSPACE unavailable; use ~qtpOpenPanel.value to recover.".warn });
};
~qtpInstallNavigation.value;

install = {
    if((~qrmOutputChannels ? 2) != 2 or: { s.options.numOutputBusChannels != 2 }, {
        "QMW TRANSITIONS: this opt-in adapter requires a declared two-output stereo session.".warn;
    }, {
        if(~qriVoiceGainBus.isNil or: { ~qriFXSendBus.isNil } or: { ~qriFXGroup.isNil }
            or: { ~qriFXProxyGroup.isNil } or: { ~qriVoiceFuzzSendBus.isNil } or: { ~qriVoiceFXSendBus.isNil }, {
            "QMW TRANSITIONS: waiting for V3 mixer/FX bus ownership; no fallback output.".warn;
        }, {
            SynthDef(\qtpEventV1, { |outBus=0, noteHz=220, strength=0, excitationMode=0, duration=0.001|
                var frequencies = \frequencies.kr(Array.fill(16,220));
                var gains = \gains.kr(Array.fill(16,0));
                var tau = \tau.kr(Array.fill(16,0.18));
                var strike = EnvGen.ar(Env([0,1,0],[0.0005,0.0005],\lin));
                var pitched = SinOsc.ar(noteHz,0) * EnvGen.ar(Env([0,1,0],[duration*0.5,duration*0.5],\sine));
                // Declared acoustic profile calibration, independent of rho.
                var excitation = Select.ar(excitationMode,[strike,pitched*0.02]) * strength;
                var signal = Mix(Ringz.ar(excitation,frequencies,tau*6.907755) * gains)
                    * (48000 / SampleRate.ir);
                var life = EnvGen.kr(Env([1,1,0],[duration+1.45,0.03]),doneAction:2);
                Out.ar(outBus, (LeakDC.ar(signal)*life).dup / 1.4142135623730951);
            }).add;
            SynthDef(\qtpFXFeedV1, { |privateBus=0, selectedBus=0, beforeBus=0, fxSendBus=0,
                gateBus=0, voiceGainBus=0, voiceFuzzSendBus=0, voiceFXSendBus=0,
                fuzzDrive=8, fuzzBias=0.12, fuzzTone=5200|
                var tail=In.ar(privateBus,2), gate=In.kr(gateBus,3);
                var simple=In.kr(voiceGainBus,8)[0].clip(0,1.5);
                var amount=Lag.kr(In.kr(voiceFuzzSendBus,8)[0].clip(0,1),0.03);
                var send=Lag.kr(In.kr(voiceFXSendBus,8)[0].clip(0,1),0.03);
                var drive=Lag.kr(fuzzDrive.clip(1,40),0.03);
                var bias=Lag.kr(fuzzBias.clip(-0.45,0.45),0.03);
                var first=((HPF.ar(tail,24)*drive)+bias).tanh;
                var second=((first*(1.6+(drive.sqrt*0.32)))+(bias*0.55)).tanh;
                var fuzzed=LPF.ar(LeakDC.ar(second.clip(-0.72+(bias*0.12),0.50+(bias*0.12))),
                    fuzzTone.clip(800,12000))*0.92;
                // Same per-voice fuzz law and SIMPLE sends as the native instrument.
                var selected=Limiter.ar(XFade2.ar(tail,fuzzed,(amount*2)-1)*gate[0]*simple*gate[2],0.7);
                var previous=In.ar(0,2), previousFX=In.ar(fxSendBus,2), dry;
                selected=selected*(gate[0]>0)*(simple>0)*(gate[2]>0);
                dry=Select.ar(gate[1],[previous+selected,selected]);
                ReplaceOut.ar(selectedBus,selected);
                ReplaceOut.ar(beforeBus,dry);
                ReplaceOut.ar(0,dry);
                ReplaceOut.ar(fxSendBus,Select.ar(gate[1],[previousFX+(selected*send),selected*send]));
            }).add;
            SynthDef(\qtpFXCaptureV1, { |beforeBus=0, wetBus=0|
                // Capture the existing FX monitor contribution without moving or
                // duplicating Clouds, VST instances, or their return controls.
                ReplaceOut.ar(wetBus,In.ar(0,2)-In.ar(beforeBus,2));
            }).add;
            SynthDef(\qtpStereoReturnV1, { |selectedBus=0, wetBus=0, gateBus=0, voiceGainBus=0|
                var gate=In.kr(gateBus,3), simple=In.kr(voiceGainBus,8)[0];
                var soloSignal=In.ar(selectedBus,2)+In.ar(wetBus,2);
                soloSignal=soloSignal*(gate[0]>0)*(simple>0)*(gate[2]>0);
                ReplaceOut.ar(0,Select.ar(gate[1],[In.ar(0,2),soloSignal]));
            }).add;
            SynthDef(\qtpChordEventV1, { |outBus=0, strength=0, duration=0.25|
                var frequencies=\chordHz.kr([220,275,330,412.5]);
                var amplitudes=\chordGains.kr([0.25,0.25,0.25,0.25]);
                var bodyGains=\gains.kr(Array.fill(16,0.25));
                var envelope=EnvGen.ar(Env.perc(0.008,duration.max(0.04),1,-4),doneAction:2);
                // Declared pitched chord adapter: the four fundamentals remain
                // audible; density-derived body weights colour upper partials.
                var voices=SinOsc.ar(frequencies)
                    +(SinOsc.ar(frequencies*2)*bodyGains.copyRange(0,3)*0.5)
                    +(SinOsc.ar(frequencies*3)*bodyGains.copyRange(4,7)*0.25);
                var signal=Mix(voices*amplitudes)*envelope*strength*16;
                Out.ar(outBus,LeakDC.ar(signal).dup/1.4142135623730951);
            }).add;
            // A QMW onset launches this finite cloud. Grain timing is a declared
            // acoustic texture inside that event, never another quantum clock.
            SynthDef(\qtpGranularChordV1, { |outBus=0, strength=0, duration=0.25,
                grainMs=45, grainRate=32, texture=0.7, spread=0.7|
                var frequencies=\chordHz.kr([220,275,330,412.5]).clip(20,16000);
                var amplitudes=\chordGains.kr([0.25,0.25,0.25,0.25]).clip(0,1);
                var bodyGains=\gains.kr(Array.fill(16,0.25)).clip(0,1);
                var grainDuration=grainMs.clip(6,250)*0.001;
                var rate=grainRate.clip(2,120);
                var burstDuration=duration.clip(0.01,2);
                var active=Line.ar(0,1,burstDuration)<1;
                var trigger=Impulse.ar(rate)*active;
                var width=spread.clip(0,1);
                var pan=[-0.85,-0.28,0.28,0.85]*width;
                var safeIndex=(SampleRate.ir*0.4/frequencies-1).floor.max(0).min(4);
                var index=(texture.clip(0,4)*(0.5+bodyGains.copyRange(0,3))).min(safeIndex);
                var voices=Array.fill(4,{|i|
                    GrainFM.ar(2,trigger,grainDuration,frequencies[i],frequencies[i],
                        index[i],pan[i],-1,64)*amplitudes[i]
                });
                // Overlap is bounded to 30 grains per tone, below maxGrains 64.
                // Normalize overlap; retain diagnostic strength as a linear gain.
                var signal=Mix(voices)/(rate*grainDuration).max(1);
                var life=EnvGen.kr(Env([1,1,0],[burstDuration+grainDuration,0.02]),doneAction:2);
                Out.ar(outBus,LeakDC.ar(signal)*life*strength.clip(0,1)*16);
            }).add;
            s.sync;
            ~qtpPrivateBus=Bus.audio(s,2); ~qtpSelectedBus=Bus.audio(s,2);
            ~qtpBeforeBus=Bus.audio(s,2); ~qtpWetBus=Bus.audio(s,2);
            ~qtpGateBus=Bus.control(s,3); ~qtpGateBus.setn([0,0,1]);
            ~qtpRoot=Group.basicNew(s,0);
            ~qtpFeedGroup=Group.before(~qriFXGroup).register;
            ~qtpVoiceGroup=Group.before(~qtpFeedGroup).register;
            ~qtpCaptureGroup=Group.after(~qriFXProxyGroup).register;
            ~qtpRouterGroup=Group.tail(~qtpRoot).register;
            ~qtpFeed=Synth.tail(~qtpFeedGroup,\qtpFXFeedV1,[
                \privateBus,~qtpPrivateBus.index,\selectedBus,~qtpSelectedBus.index,
                \beforeBus,~qtpBeforeBus.index,\fxSendBus,~qriFXSendBus.index,
                \gateBus,~qtpGateBus.index,\voiceGainBus,~qriVoiceGainBus.index,
                \voiceFuzzSendBus,~qriVoiceFuzzSendBus.index,\voiceFXSendBus,~qriVoiceFXSendBus.index]);
            Synth.tail(~qtpCaptureGroup,\qtpFXCaptureV1,[\beforeBus,~qtpBeforeBus.index,\wetBus,~qtpWetBus.index]);
            ~qtpRouter=Synth.tail(~qtpRouterGroup,\qtpStereoReturnV1,[
                \selectedBus,~qtpSelectedBus.index,\wetBus,~qtpWetBus.index,
                \gateBus,~qtpGateBus.index,\voiceGainBus,~qriVoiceGainBus.index]);
            ~qtpInstalled = true;
            if("QMW_TRANSITION_OUTPUT".getenv.notNil, {
                ~qtpOnsetLog=File("QMW_TRANSITION_OUTPUT".getenv +/+ ("transition-onsets-" ++ Date.getDate.stamp ++ ".tsv"),"w");
                ~qtpOnsetLog.write("clock\telapsed_s\tsession\tframe_seq\tsource_revision\tconfig_revision\tqmw_trigger\tqmw_channel\tqmw_kind\tsource\ttarget\tpitch_hz\tdiagnostic_strength\tchord_cell\tchord_hz\tvoice_mode\tgrain_ms_rate_texture_spread\n");
            });
            ~qtpInstallFollow.value;

            OSCdef(\qtpCompleteFrame, { |message,time,address|
                var a=message.copyRange(1,message.size-1), newSession, now=Main.elapsedTime;
                if(address.ip == "127.0.0.1" and: { validPacket.(a) }, {
                    newSession=~qtpSession.isNil or: { ~qtpSession != a[1] };
                    if(newSession, {
                        ~qtpSession !? { ~qtpRetired.add(~qtpSession) };
                        ~qtpAllowNewSession=false;
                        "QMW_TRANSITION_SOURCE_CONNECTED".postln;
                    });
                    ~qtpSession=a[1]; ~qtpSequence=a[2]; ~qtpObservedRevision=a[3]; ~qtpSourceRevision=a[4];
                    if(a[6] != ~qtpAppliedRevision, {~qtpFollowCycle=0});
                    ~qtpAppliedRevision=a[6]; ~qtpLastValidAt=now; ~qtpPacket=a;
                    ~qtpCandidates=if(a[1625] > 0,{a.copyRange(1626,1625+(a[1625]*5)).clump(5)},{[]});
                    ~qtpHarmony=a.copyRange(1626+(a[1625]*5),a.size-1);
                    ~qtpChordCells=~qtpHarmony.copyRange(4,195).clump(12);
                    if(~qtpChordCurrent.isNil or: {newSession}, {~qtpChordCurrent=~qtpHarmony[3].asInteger}, {
                        var best=~qtpHarmony[3].asInteger;
                        if(~qtpChordCells[best][3]>(~qtpChordCells[~qtpChordCurrent][3]*1.1),{~qtpChordCurrent=best});
                    });
                    ~qtpCells=a.copyRange(88,1623).clump(6); ~qtpSourceHash=a[22];
                    if(newSession, { ~qtpSendConfig.value });
                    ~qtpSourceLabel=if(a[7] == 1, {"HELD H / RHO"}, {"LIVE H / RHO"})
                        ++ "   source " ++ a[4] ++ "   incoming " ++ a[3] ++ "   controls " ++ a[6]
                        ++ "   |   " ++ a[9] ++ " eligible connections\nA = " ++ a[8];
                    if(a[1624] == 0 and: { ~qtpControls[18] == 0 } and: {a[10] >= 0}, {
                        s.bind({~qtpEmit.(a.copyRange(10,14),"INDEPENDENT")});
                    });
                }, {
                    if(now-~qtpLastRejectAt >= 5, {
                        ~qtpLastRejectAt=now;
                        ("QMW TRANSITIONS rejected frame: " ++ (~qtpRejectReason ? "non-loopback sender")).warn;
                    });
                });
            }, "/qmw/transitions/v3/frame", recvPort:17934);
            OSCdef(\qtpSaved, { |message,time,address|
                if(address.ip == "127.0.0.1", { ~qtpSaveLabel="Saved " ++ message[1].asString });
            }, "/qmw/transitions/v1/saved", recvPort:17934);


            ~qtpWindow = Window("QMW TRANSITIONS",Rect(70,70,1040,760)).background_(Color.fromHexString("111a24")).front;
            ~qtpWindow.alwaysOnTop_(false);
            ~qtpText = { |rect,text,size=12|
                StaticText(~qtpWindow,rect).string_(text).stringColor_(Color.fromHexString("dde6ec"))
                    .font_(Font("Helvetica Neue",size));
            };
            ~qtpText.(Rect(20,12,360,32),"TRANSITION OBSERVER",22);
            ~qtpText.(Rect(530,15,490,24),"QMW  /  FOUR QUBITS  /  16 ENERGY STATES",12);
            ~qtpReadout=~qtpText.(Rect(20,50,1000,42),~qtpSourceLabel,12);
            ~qtpArmButton=Button(~qtpWindow,Rect(20,102,155,30))
                .states_([["EVENTS OFF",Color.white,Color.fromHexString("364250")],
                          ["EVENTS ARMED",Color.black,Color.fromHexString("70d5b3")]])
                .action_({ |v| ~qtpArmed=v.value==1; if(~qtpArmed.not,{~qtpVoiceGroup.freeAll;~qtpNodes.clear}) });
            ~qtpSoloButton=Button(~qtpWindow,Rect(185,102,155,30))
                .states_([["MIX WITH QMW"],["SOLO TRANSITIONS",Color.black,Color.fromHexString("e6bf73")]])
                .action_({ |v| ~qtpSolo=v.value==1 });
            ~qtpHoldButton=Button(~qtpWindow,Rect(350,102,155,30))
                .states_([["FOLLOW LIVE"],["HOLD SNAPSHOT",Color.black,Color.fromHexString("75b9ed")]])
                .action_({ |v| ~qtpControls[7]=v.value;~qtpSendConfig.value });
            Button(~qtpWindow,Rect(530,102,155,30)).states_([["REFRESH CONNECTION"]]).action_({~qtpReconnect.value});
            Button(~qtpWindow,Rect(695,102,155,30)).states_([["SAVE FRAME"]])
                .action_({~qtpConfigTarget.sendMsg("/qmw/transitions/v1/save")});
            Button(~qtpWindow,Rect(860,102,155,30)).states_([["STOP EVENTS"]])
                .action_({~qtpArmed=false;~qtpArmButton.value_(0);~qtpVoiceGroup.freeAll;~qtpNodes.clear});

            ~qtpText.(Rect(20,145,485,24),"SOURCE across  /  TARGET down  /  click a connection",12);
            ~qtpMatrix=UserView(~qtpWindow,Rect(20,175,486,484)).background_(Color.fromHexString("18232e"));
            ~qtpMatrix.drawFunc_({
                var cells=~qtpCells, values, peak=1, cell, value, mag, phase, color, x,y,rect,eligible;
                if(~qtpDrawCount == 0, { "QMW_TRANSITION_MATRIX_DRAWING".postln });
                ~qtpDrawCount = ~qtpDrawCount + 1;
                Pen.font=Font("Helvetica Neue",10);
                16.do { |i|
                    Pen.color=Color.fromHexString("aebeca");
                    Pen.stringAtPoint((i+1).asString,Point(34+(i*28),5));
                    Pen.stringAtPoint((i+1).asString,Point(5,33+(i*28)));
                };
                if(cells.notNil, {
                    values=cells.collect { |c| switch(~qtpView,
                        0,{c[5]},1,{(c[0].squared+c[1].squared).sqrt},
                        2,{(c[0].squared+c[1].squared).sqrt},3,{(c[2].squared+c[3].squared).sqrt}) };
                    peak=values.maxItem.max(1e-15);
                });
                256.do { |i|
                    x=i%16; y=(i/16).floor.asInteger; rect=Rect(28+(x*28),28+(y*28),26,26);
                    color=Color.fromHexString("253544");
                    if(cells.notNil, {
                        cell=cells[i]; mag=(cell[0].squared+cell[1].squared).sqrt;
                        value=(values[i]/peak).clip(0,1).sqrt;
                        phase=atan2(cell[1],cell[0]);
                        color=if(~qtpView==2, {Color.hsv((phase/(2pi)+1)%1,0.65,0.12+(0.85*value))},
                            {Color.fromHexString("263c4a").blend(Color.fromHexString("6dd2bc"),value)});
                        eligible=(x!=y) and: {mag>~qtpControls[5]} and: {cell[5]>~qtpControls[6]} and: {cell[4].abs>1e-9};
                        if(eligible.not, {color=color.blend(Color.fromHexString("17222d"),0.55)});
                    });
                    if(x==y, {color=Color.fromHexString("374451")});
                    Pen.fillColor=color;Pen.fillRect(rect);
                    if(x==~qtpControls[9] and: {y==~qtpControls[10]}, {
                        Pen.strokeColor=Color.white;Pen.width=2;Pen.strokeRect(rect.insetBy(1,1));
                    });
                };
            });
            ~qtpMatrix.mouseDownAction_({ |view,x,y|
                var column=((x-28)/28).floor.asInteger, row=((y-28)/28).floor.asInteger;
                if(column>=0 and: {column<16 and: {row>=0 and: {row<16}}}, {
                    ~qtpControls[9]=column;~qtpControls[10]=row;~qtpSendConfig.value;
                });
            });
            ~qtpCellReadout=~qtpText.(Rect(20,666,485,72),"Select any cell. Labels 1-16 are current ascending energy ranks.",11);

            ~qtpText.(Rect(530,145,480,24),"OBSERVABLE A",15);
            ~qtpScopeMenu=PopUpMenu(~qtpWindow,Rect(530,178,175,27)).items_(["Local qubit","Collective mean","Adjacent pair"])
                .action_({|v|~qtpControls[1]=v.value;~qtpSendConfig.value});
            ~qtpQubitMenu=PopUpMenu(~qtpWindow,Rect(715,178,130,27)).items_(["Qubit 1","Qubit 2","Qubit 3","Qubit 4"])
                .action_({|v|~qtpControls[2]=v.value;~qtpSendConfig.value});
            ~qtpAxisMenu=PopUpMenu(~qtpWindow,Rect(855,178,160,27)).items_(["X axis","Y axis","Z axis"]).value_(2)
                .action_({|v|~qtpControls[3]=v.value;~qtpSendConfig.value});
            ~qtpBlend=EZSlider(~qtpWindow,Rect(530,215,485,28),"blend to next axis",ControlSpec(0,1,\lin),
                {|v|~qtpControls[4]=v.value;~qtpSendConfig.value},0,labelWidth:145);
            ~qtpText.(Rect(530,245,485,22),"Blend: X to Y, Y to Z, Z to X. Pair uses the next qubit.",11);
            ~qtpAmplitude=EZSlider(~qtpWindow,Rect(530,276,485,28),"amplitude floor",ControlSpec(1e-10,1,\exp),
                {|v|~qtpControls[5]=v.value;~qtpSendConfig.value},1e-8,labelWidth:145);
            ~qtpActivity=EZSlider(~qtpWindow,Rect(530,312,485,28),"activity floor",ControlSpec(1e-10,1,\exp),
                {|v|~qtpControls[6]=v.value;~qtpSendConfig.value},1e-8,labelWidth:145);
            [~qtpAmplitude,~qtpActivity].do { |control|
                control.round_(1e-12); control.numberView.decimals_(10); control.value_(1e-8);
            };
            ~qtpViewMenu=PopUpMenu(~qtpWindow,Rect(530,351,235,27)).items_(["View: diagnostic activity","View: matrix magnitude","View: matrix phase","View: density coherence"])
                .action_({|v|~qtpView=v.value;~qtpMatrix.refresh});
            ~qtpSelectionMenu=PopUpMenu(~qtpWindow,Rect(780,351,235,27)).items_(["Play: strongest","Play: cycle connections","Play: selected cell"])
                .action_({|v|~qtpControls[8]=v.value;~qtpSendConfig.value});
            ~qtpText.(Rect(530,392,160,23),"MUSICAL EVENTS",15);
            ~qtpTimingMenu=PopUpMenu(~qtpWindow,Rect(710,389,305,27))
                .items_(["Timing: independent pulse","Timing: follow QMW"]).value_(~qtpControls[18])
                .action_({|view|
                    ~qtpArmed=false;~qtpArmButton.value_(0);~qtpVoiceGroup.freeAll;~qtpNodes.clear;
                    ~qtpControls[18]=view.value;~qtpCandidates=[];~qtpSendConfig.value;
                    ~qtpRate.labelView.string_(if(view.value == 1,{"max events/sec"},{"pulse events/sec"}));
                });
            ~qtpRate=EZSlider(~qtpWindow,Rect(530,425,485,28),"max events/sec",ControlSpec(0.25,10,\exp),
                {|v|~qtpControls[11]=v.value;~qtpSendConfig.value},2,labelWidth:145);
            ~qtpBase=EZSlider(~qtpWindow,Rect(530,461,485,28),"base pitch Hz",ControlSpec(55,880,\exp),
                {|v|~qtpControls[12]=v.value;~qtpSendConfig.value},220,labelWidth:145);
            ~qtpDuration=EZSlider(~qtpWindow,Rect(530,497,485,28),"note duration sec",ControlSpec(0.01,2,\exp),
                {|v|~qtpControls[14]=v.value;~qtpSendConfig.value},0.25,labelWidth:145);
            ~qtpExcitationMenu=PopUpMenu(~qtpWindow,Rect(530,535,155,27)).items_(["Broad strike (single)","Pitched note (single)"]).value_(1)
                .action_({|v|~qtpControls[17]=v.value;~qtpSendConfig.value});
            ~qtpVoicesMenu=PopUpMenu(~qtpWindow,Rect(695,535,155,27)).items_(["1 voice","2 voices","4 voices","8 voices"]).value_(2)
                .action_({|v|~qtpControls[15]=[1,2,4,8][v.value];~qtpSendConfig.value});
            ~qtpBodyMenu=PopUpMenu(~qtpWindow,Rect(860,535,155,27)).items_(["Identity body","Fourier body"])
                .action_({|v|~qtpControls[16]=v.value;~qtpSendConfig.value});
            ~qtpLevelControl=EZSlider(~qtpWindow,Rect(530,572,485,28),"output level",ControlSpec(0,2,\lin),
                {|v|~qtpLevel=v.value},1,labelWidth:145);
            ~qtpRoutingReadout=~qtpText.(Rect(530,613,485,74),"",11);
            Button(~qtpWindow,Rect(530,690,235,30)).states_([["CHORD MATRIX / DENSITY CV"]]).action_({~qtpOpenHarmony.value});
            Button(~qtpWindow,Rect(780,690,235,30)).states_([["MAIN CLOUDS / VST FX"]]).action_({~qriOpenFXControls !? _.value});
            ~qtpText.(Rect(530,728,485,25),"SIMPLE fuzz + FX sends apply. Solo keeps FX returns. HOLD fixes H/rho.",10);
            ~qtpWindow.view.children.do { |view|
                if(view.isKindOf(CompositeView), { view.children.do { |child|
                    if(child.isKindOf(StaticText), {child.stringColor_(Color.fromHexString("dde6ec"))});
                }});
            };

            // Restore supplied controls without invoking their actions.
            ~qtpScopeMenu.value_(~qtpControls[1]);~qtpQubitMenu.value_(~qtpControls[2]);
            ~qtpAxisMenu.value_(~qtpControls[3]);~qtpBlend.value_(~qtpControls[4]);
            ~qtpAmplitude.value_(~qtpControls[5]);~qtpActivity.value_(~qtpControls[6]);
            ~qtpHoldButton.value_(~qtpControls[7]);~qtpSelectionMenu.value_(~qtpControls[8]);
            ~qtpRate.value_(~qtpControls[11]);~qtpBase.value_(~qtpControls[12]);
            ~qtpDuration.value_(~qtpControls[14]);~qtpVoicesMenu.value_([1,2,4,8].indexOf(~qtpControls[15]) ? 2);
            ~qtpBodyMenu.value_(~qtpControls[16]);~qtpExcitationMenu.value_(~qtpControls[17]);
            ~qtpRate.labelView.string_(if(~qtpControls[18] == 1,{"max events/sec"},{"pulse events/sec"}));

            ~qtpWindow.onClose_({ ~qtpWindow=nil;~qtpRemove.value });
            AppClock.sched(0.02, {
                var gate;
                if(~qtpGeneration === generation and: { ~qtpInstalled }, {
                    gate=if(~qtpCanSound.value, {
                        (~qrmMaster ? 0).clip(0,0.9) * (~qriMix ? 0).clip(0,1) * (~qriEventGain ? 0).clip(0,2)
                    }, { 0 });
                    ~qtpGateBus.setn([gate,~qtpSolo.asInteger,~qtpLevel]);
                    ~qtpVoiceGroup.moveBefore(~qtpFeedGroup);
                    ~qtpFeedGroup.moveBefore(~qriFXGroup);
                    ~qtpCaptureGroup.moveAfter(~qriFXProxyGroup);
                    ~qtpRouterGroup.moveToTail(~qtpRoot);
                    ~qtpFeed.set(\fuzzDrive,~qrmFuzzDrive ? 8,\fuzzBias,~qrmFuzzBias ? 0.12,\fuzzTone,~qrmFuzzTone ? 5200);
                    ~qtpUpdateClouds !? _.value;
                    ~qtpHarmonyView !? _.refresh;

                    ~qtpRoutingReadout.string_(
                        if(~qtpCanSound.value, {"Audio ready"}, {"Audio gated: use PLUCK + AUDIO and enable SIMPLE"})
                        ++ if(~qtpSolo, {" / SOLO"}, {" / mixed with QMW"})
                        ++ " / QMW attacks " ++ ~qtpQMWTriggers ++ " / played " ++ ~qtpFollowOnsets
                        ++ "\nLast musical event: " ++ ~qtpLastNoteLabel
                        ++ "\n" ++ ~qtpSaveLabel
                    );
                    ~qtpReadout.string_(~qtpSourceLabel ++ if(Main.elapsedTime-~qtpLastValidAt>1.5,
                        {"\nSource stale: transition output gated"}, {""}));
                    if(~qtpCells.notNil, {
                        var n=~qtpControls[9], m=~qtpControls[10], c=~qtpCells[m*16+n];
                        var magnitude=(c[0].squared+c[1].squared).sqrt;
                        var p=~qtpCells[n*16+n][2];
                        ~qtpCellReadout.string_("Selected " ++ (n+1) ++ " > " ++ (m+1)
                            ++ "   |A| " ++ magnitude.round(0.000001)
                            ++ "   phase " ++ atan2(c[1],c[0]).round(0.001)
                            ++ "\nDelta E " ++ c[4].round(0.000001) ++ "   omega " ++ c[4].round(0.000001)
                            ++ "   activity " ++ c[5].round(0.000001)
                            ++ "\np(source) " ++ p.round(0.000001)
                            ++ "   rho[m,n] " ++ c[2].round(0.000001) ++ " + i " ++ c[3].round(0.000001)
                            ++ "\nEnergy ranks are frame-local; HOLD for a fixed-state comparison.");
                    });
                    ~qtpMatrix.refresh;

                    0.1
                }, { nil });
            });
            ~qtpOpenHarmony.value;
            if(~qtpSoundChoice==2,{~qtpOpenGrains.value});
            "QMW_TRANSITION_GRANULAR_READY: bounded event clouds, existing chord and FX path".postln;
            "QMW_TRANSITION_PANEL_READY: disarmed, SIMPLE lane 0, main FX send and SIMPLE fuzz, complete UDP 17934.".postln;
        });
    });
};
// The opt-in bootstrap calls this only after the existing V3 server/mixer boot.
Routine({ install.value }).play(AppClock);
)
