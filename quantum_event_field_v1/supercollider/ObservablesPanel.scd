/* Display-only panel. Reads the delayed model snapshot; never advances physics. */
(
~qefSelectedPair = 0;
~qefOpenObservables = {
    if(~qefObserverWindow.notNil, { ~qefObserverWindow.front }, {
        ~qefObserverWindow = Window("QMW observables | Bloch, coherence, Dirac", Rect(140,100,980,710));
        ~qefObserverView = UserView(~qefObserverWindow, Rect(0,0,980,710))
            .background_(Color.fromHexString("f5f7fa"));
        ~qefObserverView.drawFunc = {
            var frame=~qefDisplayed[\frame], obs=~qefDisplayed[\observables];
            var ink=Color.fromHexString("172b40"), muted=Color.fromHexString("5b6c7b");
            var grid=Color.fromHexString("cbd5df"), blue=Color.fromHexString("007c91");
            var orange=Color.fromHexString("b75630"), font=Font("Helvetica",12);
            var label, line, pair, center, radius=44, op, selected=~qefSettings[\diracIndex];
            label = { |string,x,y,color,fontSize=12|
                Pen.stringAtPoint(string,Point(x,y),Font("Helvetica",fontSize),color ? ink)
            };
            line = { |x1,y1,x2,y2,color|
                Pen.strokeColor=color; Pen.width=1;
                Pen.moveTo(Point(x1,y1)); Pen.lineTo(Point(x2,y2)); Pen.stroke;
            };
            label.("SAME STATE / XX CHAIN",16,12,ink,16);
            label.("%   |   displayed tau %".format(
                if(~qefRunning, { if((~qmwQFTV3SoundEnabled ? 1)>0,{"RUNNING"},{"PAUSED"}) }, {"STOPPED / last state"}),
                frame[\tau].round(0.001)),555,15,muted);
            label.("Local Bloch vectors: x = y = 0 in this one-excitation sector",16,40,muted);
            4.do { |i|
                var x=122+(i*244), y=125, r=40, b=obs[\bloch][i], point;
                label.("Qubit %".format(i+1),x-24,65,ink);
                Pen.strokeColor=grid; Pen.width=1;
                Pen.addOval(Rect(x-r,y-r,r*2,r*2));
                Pen.addOval(Rect(x-r,y-12,r*2,24)); Pen.stroke;
                line.(x,y-r,x,y+r,grid); line.(x-r,y,x+r,y,grid);
                // Fixed oblique projection of a unit ball, including its interior.
                point=Point(x+(r*(b[0]+(0.3*b[1]))),y-(r*(b[2]+(0.2*b[1]))));
                Pen.strokeColor=blue; Pen.width=2;
                Pen.moveTo(Point(x,y)); Pen.lineTo(point); Pen.stroke;
                Pen.fillColor=blue; Pen.addOval(Rect(point.x-4,point.y-4,8,8)); Pen.fill;
                label.("z",x+5,y-r-5,muted,10); label.("x",x+r+3,y,muted,10);
                label.("x %   y %   z %".format(*b.round(0.001)),x-95,178,ink);
                label.("p(1) %   purity %".format(frame[\p][i].round(0.001),obs[\localPurity][i].round(0.001)),x-95,200,muted);
            };
            line.(16,224,964,224,grid); line.(580,242,580,653,grid);
            label.("PAIRWISE COHERENCE  rho_ab = a_a conjugate(a_b)",16,239,ink,13);
            [["Pair",24],["Re",112],["Im",218],["Magnitude",324],["Phase (deg)",440]].do { |item|
                label.(item[0],item[1],266,muted)
            };
            obs[\coherences].do { |c,i|
                var y=289+(i*28);
                if(i == ~qefSelectedPair, {
                    Pen.fillColor=Color.fromHexString("deedf1"); Pen.addRect(Rect(16,y-3,548,26)); Pen.fill;
                });
                label.("% - %".format(*(c[\sites]+1)),24,y,ink);
                label.(c[\re].round(0.0001).asString,112,y,ink);
                label.(c[\im].round(0.0001).asString,218,y,ink);
                label.(c[\magnitude].round(0.0001).asString,324,y,ink);
                label.(if(c[\phaseValid], { (c[\phase]*180/pi).round(0.1).asString }, { "undefined" }),440,y,ink);
            };
            label.("Click a pair for its phase wheel; circle edge = magnitude 0.5.",16,461,muted,11);
            label.("SIGNED CURRENTS",16,491,ink,13);
            3.do { |i|
                var y=530+(i*40), j=frame[\j][i], width=j.abs*105;
                label.("% -> %".format(i+1,i+2),18,y-7,ink);
                line.(108,y,318,y,grid); line.(213,y-10,213,y+10,grid);
                Pen.fillColor=if(j>=0,{blue},{orange});
                Pen.addRect(Rect(if(j>=0,{213},{213-width}),y-5,width.max(0.1),10)); Pen.fill;
                label.(j.round(0.0001).asString,330,y-7,ink);
            };
            label.("Positive = rightward flow; negative = leftward.",16,640,muted,11);
            pair=obs[\coherences][~qefSelectedPair]; center=Point(486,563);
            label.("Pair % - %".format(*(pair[\sites]+1)),450,499,ink);
            Pen.strokeColor=grid; Pen.addOval(Rect(center.x-radius,center.y-radius,2*radius,2*radius)); Pen.stroke;
            line.(center.x-radius,center.y,center.x+radius,center.y,grid);
            line.(center.x,center.y-radius,center.x,center.y+radius,grid);
            Pen.strokeColor=blue; Pen.width=2; Pen.moveTo(center);
            Pen.lineTo(Point(center.x+(2*radius*pair[\re]),center.y-(2*radius*pair[\im]))); Pen.stroke;
            label.(if(pair[\phaseValid], { "phase % deg".format((pair[\phase]*180/pi).round(0.1)) }, { "phase undefined" }),434,617,muted,11);
            label.("DIRAC OPERATORS / ALGEBRAIC EXPECTATIONS",600,239,ink,13);
            op=~qefOperators[selected];
            label.("% = %".format(op[\name],op[\formula]),610,292,muted);
            obs[\dirac].do { |value,i|
                var y=330+(i*28), width=value.abs*65;
                label.(~qefOperators[i][\name],608,y-7,if(i==selected,{blue},{ink}));
                line.(740,y,870,y,grid); line.(805,y-8,805,y+8,grid);
                Pen.fillColor=if(value>=0,{blue},{orange});
                Pen.addRect(Rect(if(value>=0,{805},{805-width}),y-4,width.max(0.1),8)); Pen.fill;
                label.(value.round(0.0001).asString,884,y-7,ink);
            };
            label.("Selected fixed matrix; its expectation changes with the state.",600,447,muted,11);
            4.do { |i| 4.do { |j|
                var r=op[\re][i][j], q=op[\im][i][j], x=657+(j*57), y=474+(i*37);
                var text=if(q==0,{r.asString},{if(q>0,{"i"},{"-i"})});
                Pen.fillColor=if((r.abs+q.abs)>0,{Color.fromHexString("deedf1")},{Color.white});
                Pen.addRect(Rect(x,y,53,33)); Pen.fill;
                label.(text,x+20,y+8,ink,14);
            } };
            label.("Basis: |1000>, |0100>, |0010>, |0001>",610,633,muted,11);
            line.(16,665,964,665,grid);
            label.("Readouts follow the audio lookahead. Dirac values describe this XX state; no relativistic dynamics are implied.",16,680,muted,11);
        };
        ~qefObserverView.mouseDownAction = { |view,x,y|
            if((x<570) and: { y>=286 } and: { y<454 }, {
                ~qefSelectedPair=((y-286)/28).floor.asInteger.clip(0,5); view.refresh;
            });
        };
        ~qefDiracMenu = PopUpMenu(~qefObserverWindow,Rect(610,263,340,24))
            .items_(~qefOperators.collect { |op| op[\name] ++ "  (" ++ op[\formula] ++ ")" })
            .value_(~qefSettings[\diracIndex])
            .action_({ |view| ~qefSet.(\diracIndex,view.value) });
        ~qefObserverWindow.onClose = {
            ~qefObserverWindow=nil; ~qefObserverView=nil; ~qefDiracMenu=nil;
        };
        ~qefObserverWindow.front;
    });
};
)
