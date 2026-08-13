#!/usr/bin/env python3
from __future__ import annotations
import argparse,itertools,json,math
from dataclasses import dataclass,asdict
import numpy as np
NQ=8; DIM=256
P={"X":np.array([[0,1],[1,0]],complex),"Y":np.array([[0,-1j],[1j,0]],complex),"Z":np.array([[1,0],[0,-1]],complex)}
H=(P['X']+P['Z'])/math.sqrt(2)
TRI={7:("Qian","Heaven"),6:("Dui","Lake"),5:("Li","Fire"),4:("Zhen","Thunder"),3:("Xun","Wind"),2:("Kan","Water"),1:("Gen","Mountain"),0:("Kun","Earth")}
def bit(i,q): return (i>>q)&1
def apply1(psi,g,q):
 out=psi.copy(); step=1<<q
 for base in range(0,DIM,step<<1):
  for j in range(step):
   i0,i1=base+j,base+j+step; a,b=psi[i0],psi[i1]
   out[i0]=g[0,0]*a+g[0,1]*b; out[i1]=g[1,0]*a+g[1,1]*b
 return out
def ry(t):
 c,s=math.cos(t/2),math.sin(t/2); return np.array([[c,-s],[s,c]],complex)
def rz(t): return np.diag([np.exp(-.5j*t),np.exp(.5j*t)])
def cz(psi,a,b,t):
 out=psi.copy(); f=np.exp(1j*t)
 for i in range(DIM):
  if bit(i,a) and bit(i,b): out[i]*=f
 return out
def expect(psi,ops):
 x=psi
 for q,p in ops.items(): x=apply1(x,P[p],q)
 return float(np.vdot(psi,x).real)
def build(seed,depth=3):
 r=np.random.default_rng(seed); psi=np.zeros(DIM,complex); psi[0]=1
 for q in range(8):
  psi=apply1(psi,H,q); psi=apply1(psi,ry(r.uniform(-math.pi,math.pi)),q); psi=apply1(psi,rz(r.uniform(-math.pi,math.pi)),q)
 edges=[(0,1),(1,2),(2,0),(3,4),(4,5),(5,3),(0,3),(1,4),(2,5),(6,0),(6,2),(6,4),(7,1),(7,3),(7,5),(6,7)]
 for _ in range(max(1,depth)):
  r.shuffle(edges)
  for a,b in edges: psi=cz(psi,a,b,r.uniform(.15*math.pi,math.pi))
  for q in range(8): psi=apply1(apply1(psi,ry(r.uniform(-.45,.45)),q),rz(r.uniform(-.45,.45)),q)
 return psi/np.linalg.norm(psi)
def trival(lines): return (lines[2]<<2)|(lines[1]<<1)|lines[0]
def hval(lines): return sum(v<<i for i,v in enumerate(lines))
def moving_probs(psi):
 out=[]
 for q in range(6):
  vals=[abs(expect(psi,{q:'Z',6:'X'})),abs(expect(psi,{q:'X',7:'Z'})),abs(expect(psi,{q:'Y',6:'Y'}))]
  out.append(float(np.clip(sum(vals)/1.5,0,1)))
 return out
def entanglement(psi,anc):
 a=np.array([psi[h|(anc<<6)] for h in range(64)]); n=np.linalg.norm(a)
 if n<1e-15:return 0.
 s=np.linalg.svd((a/n).reshape(8,8),compute_uv=False); p=s*s; p=p[p>1e-15]
 return float(-(p*np.log2(p)).sum())
def pauli81(psi):
 qs=(0,2,3,5); f={}
 for letters in itertools.product('XYZ',repeat=4):
  w=''.join(letters); f[w]=expect(psi,dict(zip(qs,letters)))
 win=max(f,key=lambda w:abs(f[w])); return win,f[win],f
@dataclass
class Reading:
 seed:int; measured_8bit:str; primary_binary:int; primary_lines:list; lower_trigram:str; upper_trigram:str; moving_lines:list; moving_probabilities:list; transformed_binary:int; transformed_lines:list; ancilla_value:int; trigram_entanglement_bits:float; purity:float; coherence_l1:float; pauli81_operator:str; pauli81_expectation:float
def consult(seed=None,depth=3):
 if seed is None: seed=int(np.random.SeedSequence().entropy)&0xffffffff
 psi=build(seed,depth); r=np.random.default_rng(seed^0x1C41C41C); probs=np.abs(psi)**2; m=int(r.choice(DIM,p=probs/probs.sum()))
 lines=[bit(m,q) for q in range(6)]; anc=(m>>6)&3; mp=moving_probs(psi); moving=[i+1 for i,p in enumerate(mp) if r.random()<p]
 changed=lines.copy()
 for i in moving: changed[i-1]^=1
 lo,up=TRI[trival(lines[:3])],TRI[trival(lines[3:])]; win,wev,field=pauli81(psi); rho=np.outer(psi,psi.conj())
 rd=Reading(seed,format(m,'08b'),hval(lines),lines,f'{lo[0]} / {lo[1]}',f'{up[0]} / {up[1]}',moving,[round(x,6) for x in mp],hval(changed),changed,anc,entanglement(psi,anc),float(np.trace(rho@rho).real),float(np.sum(np.abs(rho))-np.sum(np.abs(np.diag(rho)))),win,wev)
 return rd,psi,field
def send_osc(rd,host,port):
 try: from pythonosc.udp_client import SimpleUDPClient
 except ImportError as e: raise SystemExit('OSC requested: pip install python-osc') from e
 c=SimpleUDPClient(host,port); d=asdict(rd)
 for path,key in [('primary','primary_binary'),('transformed','transformed_binary'),('lines','primary_lines'),('moving_prob','moving_probabilities'),('entanglement','trigram_entanglement_bits')]: c.send_message('/qmw/iching/'+path,d[key])
 c.send_message('/qmw/iching/moving',d['moving_lines'] or [0]); c.send_message('/qmw/iching/pauli81/operator',d['pauli81_operator']); c.send_message('/qmw/iching/pauli81/expectation',d['pauli81_expectation'])
def render(lines,moving):
 return '\n'.join(f'{i+1}: '+('---------' if lines[i] else '---   ---')+('  *' if i+1 in moving else '') for i in range(5,-1,-1))
def main():
 ap=argparse.ArgumentParser(description='QMW 8-qubit I Ching / 81-Pauli oracle'); ap.add_argument('--seed',type=int); ap.add_argument('--depth',type=int,default=3); ap.add_argument('--json'); ap.add_argument('--osc',action='store_true'); ap.add_argument('--host',default='127.0.0.1'); ap.add_argument('--port',type=int,default=7400); a=ap.parse_args()
 rd,psi,field=consult(a.seed,a.depth); print('\nQMW I CHING QUANTUM ORACLE — 8 QUBITS\n'+'='*43); print(render(rd.primary_lines,rd.moving_lines)); print('lower:',rd.lower_trigram); print('upper:',rd.upper_trigram); print('64-space primary:',rd.primary_binary); print('moving lines:',rd.moving_lines or 'none'); print('transformed:',rd.transformed_binary); print(f'conditional lower|upper entanglement: {rd.trigram_entanglement_bits:.4f} bits'); print(f'81-space Pauli operator: {rd.pauli81_operator}  <P>={rd.pauli81_expectation:+.4f}'); print('seed:',rd.seed)
 if a.json:
  with open(a.json,'w') as f: json.dump({'reading':asdict(rd),'pauli81':field,'statevector_real':psi.real.tolist(),'statevector_imag':psi.imag.tolist()},f,indent=2)
 if a.osc: send_osc(rd,a.host,a.port)
if __name__=='__main__': main()
