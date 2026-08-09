#!/usr/bin/env python3
"""Molecular Geometry Layer v1: curated molecules, graph spectra, and shared packet export."""
from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
from typing import Any
import argparse, json, math
import numpy as np

if __package__:
    from .spectral_geometry_packet_v1 import SpectralGeometryPacket
else:  # Direct-script compatibility.
    from spectral_geometry_packet_v1 import SpectralGeometryPacket

# Common elements used by molecular, biological, and materials datasets.
ATOMIC_DATA={
'H':(1,1.00784),'He':(2,4.002602),'Li':(3,6.94),'Be':(4,9.0121831),'B':(5,10.81),
'C':(6,12.011),'N':(7,14.007),'O':(8,15.999),'F':(9,18.998403163),'Ne':(10,20.1797),
'Na':(11,22.98976928),'Mg':(12,24.305),'Al':(13,26.9815385),'Si':(14,28.085),
'P':(15,30.973761998),'S':(16,32.06),'Cl':(17,35.45),'Ar':(18,39.948),
'K':(19,39.0983),'Ca':(20,40.078),'Sc':(21,44.955908),'Ti':(22,47.867),
'V':(23,50.9415),'Cr':(24,51.9961),'Mn':(25,54.938044),'Fe':(26,55.845),
'Co':(27,58.933194),'Ni':(28,58.6934),'Cu':(29,63.546),'Zn':(30,65.38),
'Ga':(31,69.723),'Ge':(32,72.630),'As':(33,74.921595),'Se':(34,78.971),
'Br':(35,79.904),'Kr':(36,83.798),'I':(53,126.90447)
}
ATOMIC_NUMBERS={k:v[0] for k,v in ATOMIC_DATA.items()}
ATOMIC_MASSES={k:v[1] for k,v in ATOMIC_DATA.items()}

@dataclass
class MolecularGeometry:
    name: str
    elements: list[str]
    positions: np.ndarray
    bonds: np.ndarray
    bond_orders: np.ndarray
    charges: np.ndarray | None = None
    metadata: dict[str,Any] | None = None
    def __post_init__(self):
        self.positions=np.asarray(self.positions,dtype=float).reshape((-1,3)); self.bonds=np.asarray(self.bonds,dtype=int).reshape((-1,2))
        self.bond_orders=np.asarray(self.bond_orders,dtype=float).reshape(-1)
        if len(self.elements)!=len(self.positions): raise ValueError('element/position mismatch')
        if len(self.bonds)!=len(self.bond_orders): raise ValueError('bond/order mismatch')
        self.charges=np.zeros(len(self.elements)) if self.charges is None else np.asarray(self.charges,dtype=float)
        self.metadata={} if self.metadata is None else dict(self.metadata)
    @property
    def masses(self):
        try: return np.array([ATOMIC_MASSES[e] for e in self.elements],float)
        except KeyError as exc: raise ValueError(f'unsupported element symbol: {exc.args[0]}') from exc
    @property
    def atomic_numbers(self):
        try: return np.array([ATOMIC_NUMBERS[e] for e in self.elements],int)
        except KeyError as exc: raise ValueError(f'unsupported element symbol: {exc.args[0]}') from exc

def _geom(name,elements,positions,bonds,orders=None,**meta):
    return MolecularGeometry(name,elements,np.array(positions,float),np.array(bonds,int),np.ones(len(bonds)) if orders is None else np.array(orders,float),metadata=meta)

def _builtins():
    a=1.09; t=a/math.sqrt(3)
    methane=_geom('methane',['C','H','H','H','H'],[[0,0,0],[t,t,t],[t,-t,-t],[-t,t,-t],[-t,-t,t]],[[0,1],[0,2],[0,3],[0,4]],formula='CH4',symmetry='Td')
    water=_geom('water',['O','H','H'],[[0,0,0],[.9572,0,0],[-.23999,.92663,0]],[[0,1],[0,2]],formula='H2O',symmetry='C2v')
    co2=_geom('carbon_dioxide',['O','C','O'],[[-1.16,0,0],[0,0,0],[1.16,0,0]],[[0,1],[1,2]],[2,2],formula='CO2',symmetry='Dinfh')
    ammonia=_geom('ammonia',['N','H','H','H'],[[0,0,.15],[.94,0,-.20],[-.47,.814,-.20],[-.47,-.814,-.20]],[[0,1],[0,2],[0,3]],formula='NH3',symmetry='C3v')
    # planar benzene, alternating bond order
    pos=[]
    for r,z in [(1.397,0),(2.487,0)]:
        for k in range(6): pos.append([r*math.cos(k*math.pi/3),r*math.sin(k*math.pi/3),z])
    bonds=[[k,(k+1)%6] for k in range(6)]+[[k,6+k] for k in range(6)]
    benzene=_geom('benzene',['C']*6+['H']*6,pos,bonds,[1.5]*6+[1]*6,formula='C6H6',symmetry='D6h')
    hydrogen=_geom('hydrogen',['H','H'],[[-.3707,0,0],[.3707,0,0]],[[0,1]],formula='H2',symmetry='Dinfh')
    return {m.name:m for m in [hydrogen,water,co2,ammonia,methane,benzene]}
BUILTINS=_builtins()

def load_builtin_molecule(name:str)->MolecularGeometry:
    key=name.lower().replace(' ','_')
    aliases={'h2':'hydrogen','h2o':'water','co2':'carbon_dioxide','nh3':'ammonia','ch4':'methane','c6h6':'benzene'}
    key=aliases.get(key,key)
    if key not in BUILTINS: raise KeyError(f'unknown molecule {name}; choices: {sorted(BUILTINS)}')
    m=BUILTINS[key]
    return MolecularGeometry(m.name,list(m.elements),m.positions.copy(),m.bonds.copy(),m.bond_orders.copy(),m.charges.copy(),dict(m.metadata))

def bond_lengths(m): return np.linalg.norm(m.positions[m.bonds[:,1]]-m.positions[m.bonds[:,0]],axis=1)
def build_bond_adjacency(m,distance_power=1.0):
    n=len(m.elements); A=np.zeros((n,n)); lengths=bond_lengths(m)
    weights=m.bond_orders/np.maximum(lengths,1e-9)**distance_power
    for (i,j),w in zip(m.bonds,weights): A[i,j]=A[j,i]=w
    return A,weights

def build_graph_laplacian(m,distance_power=1.0,normalized=False):
    A,w=build_bond_adjacency(m,distance_power); d=A.sum(axis=1)
    if normalized:
        inv=np.zeros_like(d); mask=d>1e-12; inv[mask]=1/np.sqrt(d[mask]); L=np.eye(len(d))-(inv[:,None]*A*inv[None,:]); L[~mask,~mask]=0
    else: L=np.diag(d)-A
    return L,w

def solve_molecular_modes(m,n_modes=None,distance_power=1.0,mass_weighted=True,normalized=False):
    L,w=build_graph_laplacian(m,distance_power,normalized)
    if mass_weighted:
        inv=1/np.sqrt(m.masses); op=inv[:,None]*L*inv[None,:]
    else: op=L
    vals,vecs=np.linalg.eigh((op+op.T)*.5); order=np.argsort(vals); vals=np.clip(vals[order],0,None); vecs=vecs[:,order]
    count=len(vals) if n_modes is None else min(max(1,n_modes),len(vals)); vals=vals[:count]; vecs=vecs[:,:count]
    for k in range(count):
        idx=np.argmax(np.abs(vecs[:,k]));
        if vecs[idx,k]<0: vecs[:,k]*=-1
    return vals,vecs,w

def descriptors(m,eigenvalues):
    lengths=bond_lengths(m); n=len(m.elements); b=len(m.bonds); centered=m.positions-np.average(m.positions,axis=0,weights=m.masses)
    rg=float(np.sqrt(np.sum(m.masses*np.sum(centered**2,axis=1))/m.masses.sum()))
    inertia=centered.T@(m.masses[:,None]*centered); iv=np.linalg.eigvalsh(inertia); anis=float((iv[-1]-iv[0])/(iv[-1]+1e-12))
    cycle=b-n+1
    positive=eigenvalues[eigenvalues>1e-10]; gap=float(positive[0]) if len(positive) else 0.0
    p=positive/positive.sum() if positive.sum()>0 else np.array([]); entropy=float(-(p*np.log2(p+1e-15)).sum()) if len(p) else 0.0
    return {'name':m.name,'formula':m.metadata.get('formula',''),'symmetry':m.metadata.get('symmetry',''),'atom_count':n,'bond_count':b,
      'total_mass':float(m.masses.sum()),'mean_bond_length':float(lengths.mean()) if b else 0.0,'bond_length_variance':float(lengths.var()) if b else 0.0,
      'mean_coordination':float(2*b/n),'graph_density':float(2*b/(n*(n-1))) if n>1 else 0.0,'cycle_rank':int(max(0,cycle)),
      'spectral_gap':gap,'algebraic_connectivity':gap,'spectral_entropy':entropy,'radius_of_gyration':rg,'shape_anisotropy':anis,
      'elemental_diversity':len(set(m.elements))}

def molecule_to_packet(m,n_modes=None,base_frequency_hz=55.0,distance_power=1.0,mass_weighted=True,normalized=False):
    vals,vecs,weights=solve_molecular_modes(m,n_modes,distance_power,mass_weighted,normalized)
    positive=vals[vals>1e-10]; ref=float(positive[0]) if len(positive) else 1.0
    freqs=np.zeros_like(vals); mask=vals>1e-10; freqs[mask]=base_frequency_hz*np.sqrt(vals[mask]/ref)
    participation=np.sum(np.abs(vecs)*m.masses[:,None],axis=0); participation/=participation.sum()+1e-15
    damping=.15+.5*np.sqrt(vals/(vals.max()+1e-15))
    meta=dict(m.metadata); meta.update(descriptors(m,vals)); meta.update({'operator':'mass_weighted_graph_laplacian' if mass_weighted else 'graph_laplacian','distance_power':distance_power,
       'atomic_numbers':m.atomic_numbers.tolist(),'atomic_masses':m.masses.tolist(),'charges':m.charges.tolist(),'bond_orders':m.bond_orders.tolist()})
    return SpectralGeometryPacket('molecular_graph',m.positions,vals,vecs,edges=m.bonds,faces=[],frequencies_hz=freqs,
       mode_weights=participation,damping=damping,vertex_labels=np.array(m.elements),edge_weights=weights,metadata=meta)

def main():
    p=argparse.ArgumentParser(); p.add_argument('--molecule',default='methane',choices=sorted(BUILTINS)); p.add_argument('--output',default='methane_molecular_spectrum_v1.npz')
    p.add_argument('--modes',type=int); p.add_argument('--base-frequency',type=float,default=55.0); p.add_argument('--unweighted',action='store_true'); p.add_argument('--normalized',action='store_true'); p.add_argument('--json')
    a=p.parse_args(); mol=load_builtin_molecule(a.molecule); packet=molecule_to_packet(mol,a.modes,a.base_frequency,mass_weighted=not a.unweighted,normalized=a.normalized)
    packet.save_npz(a.output)
    if a.json: packet.save_json(a.json,include_eigenvectors=True)
    print('Molecular Geometry Layer v1'); print(f'  molecule: {mol.name} ({packet.metadata["formula"]})'); print(f'  atoms/bonds: {len(mol.elements)}/{len(mol.bonds)}'); print(f'  modes: {packet.n_modes}'); print(f'  spectral gap: {packet.metadata["spectral_gap"]:.6f}'); print(f'  output: {a.output}')
if __name__=='__main__': main()
