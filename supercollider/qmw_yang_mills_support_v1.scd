// Language-side spatial coupling and atomic OSC state, independent of scsynth.
(
~qmwYMFinite = { |value|
    value.isNumber and: { value.asFloat.isNaN.not and: { value.abs < inf } }
};
~qmwYMValidRevision = { |value|
    value.isKindOf(Integer) and: { (value >= 0) and: { value <= 2147483647 } }
};

// Composition of two periodic shears on the unit torus. Each has determinant
// one and an explicit inverse. Amount scales displacement, not gauge strength.
// Bilinear splatting discretizes this invertible map as conservative mixing.
~qmwYMWeights = { |amount = 0|
    var a = amount.clip(0, 1) * 0.25;
    var matrix = Array.fill(16, { Array.fill(16, 0.0) });
    16.do { |source|
        var u = (source.div(4) + 0.5) / 4;
        var v = (source.mod(4) + 0.5) / 4;
        var warpedU = (u + (a * sin(2pi * v))).mod(1);
        var warpedV = (v + (a * sin(2pi * warpedU))).mod(1);
        var gx = (warpedU * 4) - 0.5;
        var gy = (warpedV * 4) - 0.5;
        var x0 = gx.floor.asInteger;
        var y0 = gy.floor.asInteger;
        var fx = gx - x0;
        var fy = gy - y0;
        2.do { |dx|
            2.do { |dy|
                var target = ((x0 + dx).mod(4) * 4) + (y0 + dy).mod(4);
                var wx = if(dx == 0) { 1 - fx } { fx };
                var wy = if(dy == 0) { 1 - fy } { fy };
                matrix[target][source] = matrix[target][source] + (wx * wy);
            };
        };
    };
    matrix
};

~qmwYMMap = { |magnitudes, speeds, amount = 0|
    var weights = ~qmwYMWeights.(amount);
    var inputPower = magnitudes.collect { |value| value.squared };
    var power = Array.fill(16, { |target|
        (weights[target] * inputPower).sum
    });
    var mappedSpeed = Array.fill(16, { |target|
        if(power[target] > 1e-15) {
            (weights[target] * inputPower * speeds).sum / power[target]
        } { 0.0 }
    });
    (magnitude: power.collect { |value| value.max(0).sqrt },
        speed: mappedSpeed, power: power, weights: weights)
};

~qmwYMCommitted = -1;
~qmwYMPending = nil;
~qmwYMRawMagnitude = Array.fill(16, 0.0);
~qmwYMRawSpeed = Array.fill(16, 0.0);
~qmwYMDiagnostics = nil;
~qmwYMLastFrame = nil;
~qmwYMFrames = 0;
~qmwYMTimedOut = true;
~qmwYMAmount = 0.0;
~qmwYMCouplingValue = 1.0;
~qmwYMMasterValue = 0.0;

~qmwYMRelease = {
    ~qmwYMRawMagnitude = Array.fill(16, 0.0);
    ~qmwYMRawSpeed = Array.fill(16, 0.0);
    ~qmwYMPending = nil;
    ~qmwYMTimedOut = true;
    if(~qmwYMEmit.notNil) { ~qmwYMEmit.() };
};
~qmwYMReset = {
    ~qmwYMCommitted = -1;
    ~qmwYMLastFrame = nil;
    ~qmwYMFrames = 0;
    ~qmwYMRelease.();
};
~qmwYMWatchdogCheck = { |now|
    now = now ? Main.elapsedTime;
    if(~qmwYMTimedOut.not and: { ~qmwYMLastFrame.notNil }
        and: { (now - ~qmwYMLastFrame) > 0.75 }) {
        ~qmwYMRelease.();
    };
};

~qmwYMReceive = { |kind, message, now|
    var revision = if(message.size > 1) { message[1] } { nil };
    var matches;
    now = now ? Main.elapsedTime;
    matches = ~qmwYMPending.notNil and: {
        revision == ~qmwYMPending[\revision]
    };
    switch(kind,
        \begin, {
            if((message.size == 4) and: { ~qmwYMValidRevision.(revision) }
                and: { revision > ~qmwYMCommitted }
                and: { ~qmwYMFinite.(message[2]) }
                and: { message[2] >= 0 } and: { message[3] == 16 }
                and: { ~qmwYMPending.isNil or: { revision > ~qmwYMPending[\revision] } }) {
                ~qmwYMPending = (revision: revision, magnitude: nil,
                    speed: nil, diagnostics: nil);
            };
        },
        \magnitude, {
            if(matches) {
                ~qmwYMPending[\magnitude] = if((message.size == 18)
                    and: { message.copyRange(2, 17).every { |value|
                        ~qmwYMFinite.(value) and: { value >= 0 } and: { value <= 1 }
                    } }) { message.copyRange(2, 17) } { nil };
            };
        },
        \speed, {
            if(matches) {
                ~qmwYMPending[\speed] = if((message.size == 18)
                    and: { message.copyRange(2, 17).every { |value|
                        ~qmwYMFinite.(value) and: { value >= 0 } and: { value <= 1 }
                    } }) { message.copyRange(2, 17) } { nil };
            };
        },
        \diagnostics, {
            if(matches) {
                ~qmwYMPending[\diagnostics] = if((message.size == 7)
                    and: { message.copyRange(2, 6).every { |value| ~qmwYMFinite.(value) } }) {
                    message.copyRange(2, 6)
                } { nil };
            };
        },
        \end, {
            if(matches and: { message.size == 2 }) {
                if(~qmwYMPending[\magnitude].notNil
                    and: { ~qmwYMPending[\speed].notNil }
                    and: { ~qmwYMPending[\diagnostics].notNil }) {
                    ~qmwYMRawMagnitude = ~qmwYMPending[\magnitude];
                    ~qmwYMRawSpeed = ~qmwYMPending[\speed];
                    ~qmwYMDiagnostics = ~qmwYMPending[\diagnostics];
                    ~qmwYMCommitted = revision;
                    ~qmwYMLastFrame = now;
                    ~qmwYMFrames = ~qmwYMFrames + 1;
                    ~qmwYMTimedOut = false;
                    if(~qmwYMEmit.notNil) { ~qmwYMEmit.() };
                };
                ~qmwYMPending = nil;
            };
        }
    );
};
)
