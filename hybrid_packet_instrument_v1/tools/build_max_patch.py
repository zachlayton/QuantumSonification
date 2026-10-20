#!/usr/bin/env python3
"""Rebuild the Max 8/9 control and audio adapter, with explicit audio routes."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
boxes=[]; lines=[]
def box(id,text,x,y,w=240,cls='newobj',**extra):
    d=dict(id=id,maxclass=cls,patching_rect=[x,y,w,24])
    if text is not None:d['text']=text
    d.update(extra);boxes.append({'box':d});return id
def link(a,b,out=0,inp=0):lines.append({'patchline':{'source':[a,out],'destination':[b,inp]}})
def label(id,text,x,y,w=550):return box(id,text,x,y,w,'comment')
def msg(id,text,x,y,target,w=170):
    box(id,text,x,y,w,'message');link(id,target)
def control(name,default,x,y,dest='sc',prefix='control',lo=None,hi=None):
    label(name+'label',name,x,y,125)
    opts={'format':6}
    if lo is not None:opts['minimum']=lo
    if hi is not None:opts['maximum']=hi
    box(name+'num',None,x+130,y,90,'flonum',**opts)
    box(name+'pre',f'prepend /qmw/hybrid/{prefix}/{name}',x+230,y,300)
    link(name+'num',name+'pre');link(name+'pre',dest)
    # Visible reset value is explicit; opening the patch does not overwrite SC settings.
    msg(name+'default',str(default),x+545,y,name+'num',70)
label('title','QMW HYBRID PACKETS v1 — SuperCollider excitation / existing v4.2b FX / Max + Spat',20,15,1100)
label('setup','Start SC wrapper and Python backend first. Select the audio loopback driver: SC outputs must arrive at the same Max input numbers.',20,45,1180)
box('sc','udpsend 127.0.0.1 17920',20,110,250)
box('physics','udpsend 127.0.0.1 17921',660,110,250)
msg('start','/qmw/hybrid/start',20,80,'sc')
msg('stop','/qmw/hybrid/stop',205,80,'sc')
msg('burst','/qmw/hybrid/burst',390,80,'sc')
msg('reset','/qmw/hybrid/physics/reset',660,80,'physics',240)
label('synthtitle','SYNTHESIS / SHARED BODY (right-hand value boxes apply defaults when clicked)',20,150,620)
label('physicstitle','HAMILTONIAN — parameter changes prepare a new state; rate only changes time scale',660,150,650)
shared=[('blend',0,0,1),('density',8,0,4000),('duration',.08,.002,2),('carrier',165,1,12000),('center',.5,0,1),('width',.15,.01,1),('f0',55,15,1000),('decay',2,.02,20),('gain',.03,0,.2),('attack',.1,.001,10),('release',1,.005,20),('densityDepth',0,0,1),('envelopeDepth',0,0,1),('normalize',1,0,1),('fxSend',0,0,1),('spatial',0,0,1),('phase',0,-3.14159,3.14159)]
for i,(name,d,lo,hi) in enumerate(shared):control(name,d,20,185+30*i,lo=lo,hi=hi)
# Prefix UI IDs to avoid collisions; retain the backend parameter in the OSC address.
for i,(name,d,lo,hi) in enumerate([('potential',1,0,1),('center',-.35,-.8,.8),('width',.12,.02,.8),('momentum',2,-80,80),('phase',0,-3.14159,3.14159),('omega',8,0,30),('rate',.1,0,10)]):
    key='h_'+name;y=185+30*i
    label(key+'label',name,660,y,125)
    box(key+'num',None,790,y,90,'flonum',minimum=lo,maximum=hi)
    box(key+'pre','prepend /qmw/hybrid/physics/'+name,890,y,300)
    link(key+'num',key+'pre');link(key+'pre','physics')
    msg(key+'default',str(d),1205,y,key+'num',70)
label('help','blend: 0=synthesis, 1=Hamiltonian projection. Burst shapes cloud density and/or force. Modal decay continues after excitation.',660,420,630)
label('help2','Physics: potential 0=box, 1=harmonic inside hard walls. Dimensionless hbar=m=1. This is pure-state projection sonification.',660,455,630)
label('help3','Existing QMW window retains ring, wavefold, fuzz and Clouds/VST controls. Hybrid fxSend feeds the existing shared effects return.',660,490,630)
label('help4','The 16 pickup channels are dry. Processed stereo includes the existing instrument master and effects. Select one route below.',660,525,630)
label('help5','High packet rates are limited by grain capacity. This version has no physical temperature bath or anharmonic material simulation.',660,560,630)
label('audiotitle','AUDIO ROUTING — configure loopback/aggregate device; this patch never turns DSP on automatically',20,720,1180)
box('adc','adc~ '+ ' '.join(str(i) for i in range(1,21)),20,760,650)
box('fieldpack','mc.pack~ 16',20,810,140)
box('masterpack','mc.pack~ 16',240,810,140)
for i in range(16):link('adc','fieldpack',i+4,i)
for i in range(2):link('adc','masterpack',i,i)
box('select','mc.selector~ 2',20,870,160)
link('fieldpack','select',0,1);link('masterpack','select',0,2)
msg('fieldselect','1',440,800,'select',40)
label('fieldlabel','16 dry field pickups (SC5–20)',490,800,370)
msg('masterselect','2',440,835,'select',40)
label('masterlabel','Processed stereo master (SC1–2 → source1/2)',490,835,480)
msg('muteselect','0',440,870,'select',40)
label('mutelabel','Mute input',490,870,200)
box('renderer','qmw_craive_spat128_renderer16_v9',20,930,350)
link('select','renderer')
# Distinct explicit layouts: 16 field sample positions on a line, stereo at two front sources.
field=', '.join(f'/source/{i+1}/xyz {-2+4*i/15:.6f} 2. 0.' for i in range(16))
box('fieldpositions',field,20,1120,1280,'message');link('fieldpositions','renderer',0,1)
label('fieldposlabel','CLICK BELOW to place the 16 pickups on a 4 m line. Geometry is playback scale, independent of model box size.',20,1080,1180)
msg('stereopositions','/source/1/xyz -1. 2. 0., /source/2/xyz 1. 2. 0.',660,930,'renderer',570)
# Fix routing of the position message to the spatial inlet.
lines[-1]['patchline']['destination'][1]=1
box('gain','mc.*~ 0.',20,980,130);link('renderer','gain')
box('level',None,190,980,85,'flonum',minimum=0,maximum=1);link('level','gain',0,1)
label('levellabel','Array gain starts at 0. Configure CRAIVE output map before raising.',300,980,800)
box('dac','mc.dac~ '+ ' '.join(str(i) for i in range(1,129)),20,1020,1200)
link('gain','dac');box('status','print QMW_Hybrid_Spat',660,1020,250);link('renderer','status',2)
label('final','FX fidelity path = processed stereo master; spatial-field path = 16 dry pickups. Never sum either input to stereo before WFS.',20,1170,1260)
p={'patcher':{'fileversion':1,'appversion':{'major':8,'minor':6,'revision':0,'architecture':'x64','modernui':1},'classnamespace':'box','rect':[40,40,1320,1240],'bglocked':0,'openinpresentation':0,'default_fontsize':12,'default_fontface':0,'default_fontname':'Arial','boxes':boxes,'lines':lines}}
(ROOT/'max'/'QMW_Hybrid_Packets_Spat.maxpat').write_text(json.dumps(p,indent=2)+'\n')
if __name__=='__main__':print('Wrote QMW_Hybrid_Packets_Spat.maxpat')
