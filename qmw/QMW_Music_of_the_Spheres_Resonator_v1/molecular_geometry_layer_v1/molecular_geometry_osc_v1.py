#!/usr/bin/env python3
"""OSC bridge for Molecular Geometry Layer v1. Control 7440, output 7441."""
from __future__ import annotations
import argparse, queue, signal, threading, time
from typing import Any
import numpy as np
try:
    from pythonosc.dispatcher import Dispatcher
    from pythonosc.osc_server import ThreadingOSCUDPServer
    from pythonosc.udp_client import SimpleUDPClient
except ImportError as exc:
    raise SystemExit('python-osc is required: pip install python-osc') from exc
from molecular_geometry_layer_v1 import BUILTINS, load_builtin_molecule, molecule_to_packet

class MolecularGeometryOSC:
    def __init__(self,host='127.0.0.1',control_port=7440,out_host='127.0.0.1',out_port=7441,molecule='methane',rate=10.0,base_frequency=55.0):
        self.host=host; self.control_port=control_port; self.client=SimpleUDPClient(out_host,out_port); self.rate=max(.1,rate)
        self.molecule_name=molecule; self.base_frequency=base_frequency; self.mass_weighted=True; self.normalized=False; self.distance_power=1.0
        self.commands: queue.SimpleQueue[tuple[str,tuple[Any,...]]]=queue.SimpleQueue(); self.alive=True; self.enabled=True; self.dirty=True
        d=Dispatcher(); d.set_default_handler(self._enqueue); self.server=ThreadingOSCUDPServer((host,control_port),d); self.thread=threading.Thread(target=self.server.serve_forever,daemon=True)
        self.packet=None; self.molecule=None
    def _enqueue(self,address,*args): self.commands.put((address,tuple(args)))
    def _process(self):
        while not self.commands.empty():
            address,args=self.commands.get()
            if address=='/molecular/set': self.molecule_name=str(args[0]).lower(); self.dirty=True
            elif address=='/molecular/base_frequency': self.base_frequency=max(.001,float(args[0])); self.dirty=True
            elif address=='/molecular/distance_power': self.distance_power=max(0.0,float(args[0])); self.dirty=True
            elif address=='/molecular/mass_weighted': self.mass_weighted=bool(int(args[0])); self.dirty=True
            elif address=='/molecular/normalized': self.normalized=bool(int(args[0])); self.dirty=True
            elif address=='/molecular/rate': self.rate=max(.1,float(args[0]))
            elif address=='/molecular/enabled': self.enabled=bool(int(args[0]))
            elif address=='/molecular/send': self.dirty=True
            elif address=='/molecular/quit': self.alive=False
            else: print(f'unknown OSC command: {address}')
    def _rebuild(self):
        self.molecule=load_builtin_molecule(self.molecule_name); self.packet=molecule_to_packet(self.molecule,base_frequency_hz=self.base_frequency,distance_power=self.distance_power,mass_weighted=self.mass_weighted,normalized=self.normalized); self.dirty=False
    def _send(self):
        m,p=self.molecule,self.packet; c=self.client
        c.send_message('/molecular/name',m.name); c.send_message('/molecular/formula',p.metadata.get('formula','')); c.send_message('/molecular/atom/count',len(m.elements)); c.send_message('/molecular/bond/count',len(m.bonds)); c.send_message('/molecular/mode/count',p.n_modes)
        for i,(el,pos,mass,charge) in enumerate(zip(m.elements,m.positions,m.masses,m.charges)):
            c.send_message(f'/molecular/atom/{i}/element',el); c.send_message(f'/molecular/atom/{i}/position',[float(x) for x in pos]); c.send_message(f'/molecular/atom/{i}/mass',float(mass)); c.send_message(f'/molecular/atom/{i}/charge',float(charge))
        for k,((i,j),order,w) in enumerate(zip(m.bonds,m.bond_orders,p.edge_weights)):
            c.send_message(f'/molecular/bond/{k}/atoms',[int(i),int(j)]); c.send_message(f'/molecular/bond/{k}/order',float(order)); c.send_message(f'/molecular/bond/{k}/weight',float(w))
        for k in range(p.n_modes):
            c.send_message(f'/molecular/mode/{k}/eigenvalue',float(p.eigenvalues[k])); c.send_message(f'/molecular/mode/{k}/frequency',float(p.frequencies_hz[k])); c.send_message(f'/molecular/mode/{k}/weight',float(p.mode_weights[k])); c.send_message(f'/molecular/mode/{k}/vector',[float(x) for x in p.eigenvectors[:,k]])
        for key in ['spectral_gap','spectral_entropy','radius_of_gyration','shape_anisotropy','mean_coordination','cycle_rank']:
            c.send_message(f'/molecular/descriptor/{key}',float(p.metadata[key]))
        c.send_message('/molecular/frame',int(time.time()*1000)%2147483647)
    def run(self):
        self.thread.start(); print('Molecular Geometry OSC v1'); print(f'  control: udp://{self.host}:{self.control_port}'); print('  commands: /molecular/set methane | /molecular/send 1 | /molecular/quit 1')
        try:
            while self.alive:
                t=time.perf_counter(); self._process()
                if self.dirty: self._rebuild()
                if self.enabled: self._send()
                time.sleep(max(0,1/self.rate-(time.perf_counter()-t)))
        finally: self.server.shutdown(); self.server.server_close()
def main():
    p=argparse.ArgumentParser(); p.add_argument('--host',default='127.0.0.1'); p.add_argument('--control-port',type=int,default=7440); p.add_argument('--out-host',default='127.0.0.1'); p.add_argument('--out-port',type=int,default=7441); p.add_argument('--molecule',default='methane',choices=sorted(BUILTINS)); p.add_argument('--rate',type=float,default=10); p.add_argument('--base-frequency',type=float,default=55)
    a=p.parse_args(); bridge=MolecularGeometryOSC(a.host,a.control_port,a.out_host,a.out_port,a.molecule,a.rate,a.base_frequency)
    signal.signal(signal.SIGINT,lambda *_: setattr(bridge,'alive',False)); signal.signal(signal.SIGTERM,lambda *_: setattr(bridge,'alive',False)); bridge.run()
if __name__=='__main__': main()
