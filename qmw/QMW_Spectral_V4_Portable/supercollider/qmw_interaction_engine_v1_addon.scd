/*
QMW Interaction / Scattering Engine V1 display and pulse adapter.

Load after qmw_scalar_field_observer_v4_4.scd.  It receives only the adapter
frames from qmw.qmw_interaction_engine on UDP 17872; it never sends OSC back,
does not alter rho/flow/GPE/scalar-field evolution, and treats every diagram
as a Feynman-inspired coherent-process visualization rather than a literal
particle history.  The primary view deliberately renders at most four
dominant paths.  It is not a topology editor.
*/
(
var root = "/qmw/interaction/v1";
var addonPath = thisProcess.nowExecutingPath;
var port = (~qmwInteractionV1Port ? 17872).asInteger;
var window, diagram, inspector, status, selectedPath = 0;
var drawDiagram, refreshInspector, commitFrame, close, animationTask, setTopology;

thisProcess.openUDPPort(port);
~qmwInteractionV1Root = root;
~qmwInteractionV1Port = port;
~qmwInteractionV1Sonify = ~qmwInteractionV1Sonify ? 0;
~qmwInteractionV1StageValid = false;
~qmwInteractionV1Frame = (paths: Array.new, channels: IdentityDictionary.new,
    modals: Array.new, global: nil, time: 0.0, revision: -1);

~qmwInteractionV1DominantPaths = {
    (~qmwInteractionV1Frame[\paths] ? []).select { |path|
        path[\amplitude].abs > 1e-12
    }.sort { |a, b|
        a[\amplitude].abs > b[\amplitude].abs
    }.copyRange(0, 3)
};

refreshInspector = {
    var paths = ~qmwInteractionV1DominantPaths.();
    var path = paths.wrapAt(selectedPath);
    var channel, phase;
    if(path.isNil, {
        inspector.string_("SELECT A PROCESS / waiting for an atomic interaction frame")
    }, {
        channel = ~qmwInteractionV1Frame[\channels][path[\label]] ? (expectation: 0, coupling: 0);
        phase = path[\amplitude].angle;
        inspector.string_(
            "%  %  inputs %  outputs %\n<P> = %  |g| = %  path phase = %\nflow strength = %  modal excitation = %"
            .format(
                path[\label], path[\kind], path[\inputs], path[\outputs],
                channel[\expectation].round(0.001), channel[\coupling].abs.round(0.001), phase.round(0.001),
                (~qmwInteractionV1Frame[\global] ? [0, 0])[0].round(0.001),
                (~qmwInteractionV1Frame[\global] ? [0, 0, 0, 0])[3].round(0.001)
            )
        )
    })
};

setTopology = { |wantLoop|
    var paths = ~qmwInteractionV1DominantPaths.();
    var path = paths.wrapAt(selectedPath);
    var family, suffix, identifier, client;
    if(path.isNil, {
        status.string_("topology selection needs an active interaction path")
    }, {
        family = case
        { path[\kind] == "2_to_2" } { "scattering" }
        { path[\kind] == "1_to_2" } { "splitting" }
        { path[\kind] == "2_to_1" } { "fusion" }
        { "scattering" };
        suffix = if(wantLoop, { "one_loop" }, { "tree" });
        identifier = "%_%_%".format(path[\label].toLower, suffix, family);
        client = NetAddr("127.0.0.1", 17874);
        client.sendMsg("/qmw/interaction/composer/v1/select", identifier);
        client.sendMsg("/qmw/interaction/composer/v1/commit", 1);
        status.string_("requested % grammar for % — applies to subsequent adapter frames"
            .format(if(wantLoop, { "one-loop" }, { "tree" }), path[\label]));
    });
};

drawDiagram = {
    var paths = ~qmwInteractionV1DominantPaths.();
    var bounds = diagram.bounds, maximum, tick, selected, phase;
    var alpha, width, pulse, leftVertex, rightVertex, drawFermion, drawWavy;
    var drawLoop, inputY, outputY, inputCount, outputCount, mediatorLabel;
    Pen.fillColor = Color.black.alpha_(0.88);
    Pen.fillRect(bounds);
    Pen.color = Color.cyan(0.78);
    Pen.stringAtPoint("PROCESS  —  DECLARED INTERACTION GRAMMAR", Point(14, 12), Font("Helvetica", 14));
    if(paths.isEmpty, {
        Pen.color = Color.gray.alpha_(0.8);
        Pen.stringAtPoint("waiting for coherent interaction paths", Point(14, bounds.height * 0.5), Font("Helvetica", 16));
    }, {
        maximum = paths.collect { |path| path[\amplitude].abs }.maxItem.max(1e-9);
        tick = Main.elapsedTime;
        selected = paths.wrapAt(selectedPath);
        alpha = (0.30 + (0.70 * (selected[\amplitude].abs / maximum))).clip(0.25, 1.0);
        width = (1.5 + (6 * alpha)).clip(1.5, 7.5);
        leftVertex = Point(bounds.width * 0.39, bounds.height * 0.43);
        rightVertex = Point(bounds.width * 0.61, bounds.height * 0.43);
        phase = selected[\amplitude].angle;
        pulse = 0.74 + (0.26 * (tick * 4).sin.abs);
        inputCount = selected[\inputs].size;
        outputCount = selected[\outputs].size;
        inputY = { |index, count|
            if(count == 1, { bounds.height * 0.43 }, {
                bounds.height * (0.22 + (index / (count - 1).max(1) * 0.48))
            })
        };
        outputY = { |index, count| inputY.(index, count) };
        drawFermion = { |from, to, label, input, offset|
            var color = if(input, { Color.cyan.alpha_(alpha) }, { Color.magenta.alpha_(alpha) });
            var travel = (tick * 0.42 + offset).frac;
            var dx = to.x - from.x, dy = to.y - from.y;
            var norm = (dx.squared + dy.squared).sqrt.max(1e-6);
            var ux = dx / norm, uy = dy / norm;
            var direction = if(input, { 1.0 }, { -1.0 });
            var px = from.x + (dx * (0.32 + (travel * 0.32)));
            var py = from.y + (dy * (0.32 + (travel * 0.32)));
            Pen.color = color;
            Pen.width = width;
            Pen.moveTo(from); Pen.lineTo(to); Pen.stroke;
            // Animated arrowheads make propagation visible without claiming
            // literal particle trajectories.
            Pen.width = 1.6;
            Pen.line(Point(px, py), Point(px - (direction * ux * 11) + (uy * 4), py - (direction * uy * 11) - (ux * 4)));
            Pen.line(Point(px, py), Point(px - (direction * ux * 11) - (uy * 4), py - (direction * uy * 11) + (ux * 4)));
            Pen.stroke;
            Pen.color = Color.white.alpha_(0.86);
            Pen.stringAtPoint(label, if(input, { from + Point(-8, -16) }, { to + Point(-46, -16) }), Font("Helvetica", 11));
        };
        drawWavy = { |from, to, color|
            var segments = 32, dx = to.x - from.x, dy = to.y - from.y;
            var norm = (dx.squared + dy.squared).sqrt.max(1e-6);
            var ux = dx / norm, uy = dy / norm, px = 0 - uy, py = ux;
            Pen.color = color;
            Pen.width = width * 0.55;
            segments.do { |index|
                var t0 = index / segments;
                var t1 = (index + 1) / segments;
                var phase0 = (t0 * 10 * pi) - (tick * 5);
                var phase1 = (t1 * 10 * pi) - (tick * 5);
                var a = Point(from.x + (dx * t0) + (px * phase0.sin * 8), from.y + (dy * t0) + (py * phase0.sin * 8));
                var b = Point(from.x + (dx * t1) + (px * phase1.sin * 8), from.y + (dy * t1) + (py * phase1.sin * 8));
                Pen.line(a, b);
            };
            Pen.stroke;
        };
        drawLoop = { |vertex, order|
            var radius = 22 + ((tick * 2).sin.abs * 5);
            Pen.color = Color.yellow.alpha_(alpha);
            Pen.width = width * 0.52;
            Pen.addOval(Rect(vertex.x - radius, vertex.y - radius - 42, radius * 2, radius * 2));
            Pen.stroke;
            Pen.color = Color.yellow.alpha_(0.9);
            Pen.stringAtPoint("virtual loop L%".format(order), vertex + Point(-28, -52), Font("Helvetica", 10));
        };
        selected[\inputs].do { |mode, lane|
            drawFermion.(Point(58, inputY.(lane, inputCount)), leftVertex,
                "m% incoming".format(mode), true, lane * 0.17);
        };
        drawWavy.(leftVertex, rightVertex, Color(0.42, 0.48, 1.0, alpha));
        mediatorLabel = if(selected[\loop] > 0, { "virtual mediator + correction" }, { "internal mediator" });
        Pen.color = Color(0.62, 0.68, 1.0, 0.9);
        Pen.stringAtPoint(mediatorLabel, Point(bounds.width * 0.42, leftVertex.y - 30), Font("Helvetica", 10));
        selected[\outputs].do { |mode, lane|
            drawFermion.(rightVertex, Point(bounds.width - 58, outputY.(lane, outputCount)),
                "m% outgoing".format(mode), false, 0.42 + (lane * 0.17));
        };
        if(selected[\loop] > 0, {
            drawLoop.(leftVertex, selected[\loop]);
        });
        Pen.fillColor = Color.white.alpha_(pulse);
        Pen.addOval(Rect(leftVertex.x - 10, leftVertex.y - 10, 20, 20)); Pen.fill;
        Pen.addOval(Rect(rightVertex.x - 10, rightVertex.y - 10, 20, 20)); Pen.fill;
        Pen.fillColor = Color.black;
        Pen.addOval(Rect(leftVertex.x - 4, leftVertex.y - 4, 8, 8)); Pen.fill;
        Pen.addOval(Rect(rightVertex.x - 4, rightVertex.y - 4, 8, 8)); Pen.fill;
        Pen.color = Color.white.alpha_(0.92);
        Pen.stringAtPoint("%  %  |A| %  phase %".format(
            selected[\label], selected[\kind], selected[\amplitude].abs.round(0.001), phase.round(0.001)
        ), Point(bounds.width * 0.34, leftVertex.y + 32), Font("Helvetica", 12));
        Pen.color = Color.grey(0.72);
        Pen.stringAtPoint("incoming fermion-like modes", Point(20, 42), Font("Helvetica", 10));
        Pen.stringAtPoint("outgoing fermion-like modes", Point(bounds.width - 164, 42), Font("Helvetica", 10));
        paths.do { |path, index|
            var x = 18 + (index * ((bounds.width - 36) / paths.size));
            var cardWidth = (bounds.width - 36) / paths.size - 8;
            var cardColor = if(path == selected, { Color.cyan(0.65) }, { Color.grey(0.35) });
            Pen.color = cardColor;
            Pen.width = if(path == selected, { 2 }, { 1 });
            Pen.addRect(Rect(x, bounds.height - 46, cardWidth, 30)); Pen.stroke;
            Pen.stringAtPoint("%  |A| %".format(path[\label], path[\amplitude].abs.round(0.001)), Point(x + 7, bounds.height - 36), Font("Helvetica", 10));
        }
    });
};

commitFrame = {
    var paths = ~qmwInteractionV1DominantPaths.();
    status.string_("interaction frame % / % active paths / display top %".format(
        ~qmwInteractionV1Frame[\revision], ~qmwInteractionV1Frame[\paths].size, paths.size
    ));
    selectedPath = selectedPath.clip(0, (paths.size - 1).max(0));
    refreshInspector.(); diagram.refresh;
    // Pulses represent interaction vertices in the pre-existing V4.4 voice
    // system.  They are off until the performer explicitly enables this
    // downstream sound adapter.
    if((~qmwInteractionV1Sonify > 0) and: { ~qmwQFTV3RenderPulse.notNil }, {
        paths.do { |path|
            path[\outputs].do { |mode|
                ~qmwQFTV3RenderPulse.valueArray([
                    mode.clip(0, (~qmwQFTSiteCount ? 16) - 1),
                    path[\amplitude].abs.clip(0, 1), path[\amplitude].angle,
                    path[\amplitude].imag, path[\amplitude].abs.squared,
                    path[\amplitude].real, path[\amplitude].imag, 0,
                    1, path[\amplitude].abs.clip(0, 1), 0
                ]);
            };
        };
    });
};

window = Window("QMW Interaction / Scattering V1", Rect(100, 90, 760, 520)).front;
~qmwInteractionV1Window = window;
diagram = UserView(window, Rect(10, 10, 740, 360));
diagram.drawFunc = drawDiagram;
diagram.mouseDownAction = { |view, x, y|
    var paths = ~qmwInteractionV1DominantPaths.();
    if(paths.notEmpty, { selectedPath = (selectedPath + 1) % paths.size; refreshInspector.(); view.refresh })
};
status = StaticText(window, Rect(12, 375, 730, 22)).string_("waiting for interaction frame");
inspector = StaticText(window, Rect(12, 404, 730, 74)).stringColor_(Color.white).background_(Color.gray(0.12));
Button(window, Rect(12, 484, 180, 24)).states_([["SONIFY VERTICES OFF"], ["SONIFY VERTICES ON"]]).value_(~qmwInteractionV1Sonify.asInteger.clip(0, 1)).action_({ |button| ~qmwInteractionV1Sonify = button.value });
Button(window, Rect(205, 484, 112, 24)).states_([["TREE"]]).action_({ setTopology.(false) });
Button(window, Rect(325, 484, 112, 24)).states_([["1-LOOP"]]).action_({ setTopology.(true) });
StaticText(window, Rect(446, 486, 294, 20)).string_("Select grammar; the display remains read-only.");

// Frame arrivals update the declared process data at 8 Hz. This separate,
// small 10 Hz display clock only advances propagator packets/waves and virtual
// loop breathing; it never advances rho, GPE, or modal dynamics.
~qmwInteractionV1AnimationTask !? { |task| task.stop };
animationTask = Routine({
    loop {
        0.10.wait;
        { diagram !? _.refresh }.defer;
    }
}).play(AppClock);
~qmwInteractionV1AnimationTask = animationTask;

OSCdef(\qmwInteractionV1Begin, { |msg|
    ~qmwInteractionV1Frame = (paths: Array.new, channels: IdentityDictionary.new,
        modals: Array.new, global: nil, time: msg[2].asFloat, revision: msg[1].asInteger);
    ~qmwInteractionV1StageValid = (msg[3].asString == "qmw.interaction_scattering.v1");
}, root ++ "/frame/begin", recvPort: port);
OSCdef(\qmwInteractionV1Channel, { |msg|
    if(~qmwInteractionV1StageValid and: { msg[1].asInteger == ~qmwInteractionV1Frame[\revision] }, {
        ~qmwInteractionV1Frame[\channels][msg[3].asString] = (expectation: msg[4].asFloat, coupling: Complex(msg[5].asFloat, msg[6].asFloat));
    })
}, root ++ "/channel", recvPort: port);
OSCdef(\qmwInteractionV1Path, { |msg|
    var inputCount, outputCount, inputs, outputs, graphOffset, graph, loopOrder;
    if(~qmwInteractionV1StageValid and: { msg[1].asInteger == ~qmwInteractionV1Frame[\revision] }, {
        inputCount = msg[7].asInteger; outputCount = msg[8].asInteger;
        inputs = msg.copyRange(9, 8 + inputCount).collect(_.asInteger);
        outputs = msg.copyRange(9 + inputCount, 8 + inputCount + outputCount).collect(_.asInteger);
        graphOffset = 9 + inputCount + outputCount;
        graph = if(msg.size > graphOffset, { msg[graphOffset].asString }, { "tree" });
        loopOrder = if(msg.size > (graphOffset + 1), { msg[graphOffset + 1].asInteger }, { 0 });
        ~qmwInteractionV1Frame[\paths] = ~qmwInteractionV1Frame[\paths].add((
            label: msg[3].asString, kind: msg[4].asString,
            amplitude: Complex(msg[5].asFloat, msg[6].asFloat), inputs: inputs, outputs: outputs,
            graph: graph, loop: loopOrder
        ));
    })
}, root ++ "/path", recvPort: port);
OSCdef(\qmwInteractionV1Modal, { |msg|
    if(~qmwInteractionV1StageValid and: { msg[1].asInteger == ~qmwInteractionV1Frame[\revision] }, {
        ~qmwInteractionV1Frame[\modals] = ~qmwInteractionV1Frame[\modals].add((mode: msg[2].asInteger, magnitude: msg[3].asFloat, phase: msg[4].asFloat, excitation: msg[5].asFloat, flux: msg[6].asFloat));
    })
}, root ++ "/modal", recvPort: port);
OSCdef(\qmwInteractionV1Global, { |msg|
    if(~qmwInteractionV1StageValid and: { msg[1].asInteger == ~qmwInteractionV1Frame[\revision] }, {
        ~qmwInteractionV1Frame[\global] = msg.copyRange(2, 7).collect(_.asFloat);
    })
}, root ++ "/global", recvPort: port);
OSCdef(\qmwInteractionV1End, { |msg|
    if(~qmwInteractionV1StageValid and: { msg[1].asInteger == ~qmwInteractionV1Frame[\revision] }, {
        { commitFrame.() }.defer; ~qmwInteractionV1StageValid = false;
    })
}, root ++ "/frame/end", recvPort: port);

close = {
    animationTask !? { |task| task.stop };
    if(~qmwInteractionV1AnimationTask === animationTask) {
        ~qmwInteractionV1AnimationTask = nil
    };
    [\qmwInteractionV1Begin, \qmwInteractionV1Channel, \qmwInteractionV1Path,
        \qmwInteractionV1Modal, \qmwInteractionV1Global, \qmwInteractionV1End].do { |key| OSCdef(key).free };
};
window.onClose = {
    close.();
    if(~qmwInteractionV1Window === window) { ~qmwInteractionV1Window = nil }
};
~qmwInteractionV1OpenPanel = {
    if(~qmwInteractionV1Window.notNil, {
        ~qmwInteractionV1Window.front
    }, {
        thisProcess.interpreter.executeFile(addonPath)
    })
};
)
