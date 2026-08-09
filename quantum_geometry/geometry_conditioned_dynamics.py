"""Causal mean-field geometry-conditioned evolution on configuration space.

This is an exploratory nonlinear feedback model, not yet a strict stationary
Page-Wootters constraint solution: the current conditional state determines
the generator used for the next conditional step.
"""
from __future__ import annotations
from dataclasses import dataclass
import numpy as np


@dataclass(frozen=True)
class GeometryConditionedConfig:
    base_fraction: float = 0.25
    population_strength: float = 0.9
    coherence_strength: float = 0.7
    graph_strength: float = 0.35
    substeps: int = 4


@dataclass(frozen=True)
class GeometryConditionedHistory:
    times: np.ndarray
    states: np.ndarray
    density_matrices: np.ndarray
    weights: np.ndarray
    effective_hamiltonians: np.ndarray
    step_fidelities: np.ndarray
    hamiltonian_change_norms: np.ndarray


def local_geometry_operators(adjacency: np.ndarray, potential: np.ndarray, *, graph_strength: float=.35) -> np.ndarray:
    adjacency=np.asarray(adjacency,dtype=float); potential=np.asarray(potential,dtype=float).reshape(-1); n=len(adjacency)
    if adjacency.shape!=(n,n) or len(potential)!=n or not np.allclose(adjacency,adjacency.T): raise ValueError("invalid graph or potential")
    operators=np.zeros((n,n,n),dtype=np.complex128)
    for i in range(n):
        operators[i,i,i]=potential[i]
        for j in range(n):
            if i==j or adjacency[i,j]<=0: continue
            edge=np.zeros((n,n)); edge[i,i]=1; edge[j,j]=1; edge[i,j]=-1; edge[j,i]=-1
            operators[i]+=0.5*graph_strength*adjacency[i,j]*edge
    return operators


def effective_hamiltonian(rho: np.ndarray, base_hamiltonian: np.ndarray, local_operators: np.ndarray, adjacency: np.ndarray, config: GeometryConditionedConfig=GeometryConditionedConfig()) -> np.ndarray:
    rho=np.asarray(rho,dtype=np.complex128); base=np.asarray(base_hamiltonian,dtype=np.complex128); local=np.asarray(local_operators,dtype=np.complex128); adjacency=np.asarray(adjacency,dtype=float)
    p=np.maximum(np.real(np.diag(rho)),0); p/=p.sum()
    population=np.einsum("i,ijk->jk",p,local)
    coherence=adjacency*rho; np.fill_diagonal(coherence,0)
    h=config.base_fraction*base+config.population_strength*population-config.coherence_strength*coherence
    h=0.5*(h+h.conj().T); h-=np.trace(h).real/len(h)*np.eye(len(h))
    return h


def geometry_conditioned_history(initial_state: np.ndarray, base_hamiltonian: np.ndarray, adjacency: np.ndarray, potential: np.ndarray, *, steps: int=16, dt: float=.35, config: GeometryConditionedConfig=GeometryConditionedConfig()) -> GeometryConditionedHistory:
    psi=np.asarray(initial_state,dtype=np.complex128).reshape(-1); psi/=np.linalg.norm(psi); n=len(psi)
    if steps<2 or config.substeps<1: raise ValueError("steps and substeps must be positive")
    local=local_geometry_operators(adjacency,potential,graph_strength=config.graph_strength); states=[]; rhos=[]; hs=[]
    for frame in range(steps):
        rho=np.outer(psi,psi.conj()); h=effective_hamiltonian(rho,base_hamiltonian,local,adjacency,config)
        states.append(psi.copy()); rhos.append(rho); hs.append(h)
        if frame==steps-1: break
        for _ in range(config.substeps):
            rho=np.outer(psi,psi.conj()); h=effective_hamiltonian(rho,base_hamiltonian,local,adjacency,config)
            vals,vecs=np.linalg.eigh(h); u=(vecs*np.exp(-1j*vals*dt/config.substeps))@vecs.conj().T; psi=u@psi; psi/=np.linalg.norm(psi)
    states=np.asarray(states); rhos=np.asarray(rhos); hs=np.asarray(hs); weights=np.maximum(np.real(np.diagonal(rhos,axis1=1,axis2=2)),0); weights/=weights.sum(axis=1,keepdims=True)
    fidelity=np.abs(np.sum(states[:-1].conj()*states[1:],axis=1))**2; hchange=np.r_[0,np.linalg.norm(np.diff(hs,axis=0),axis=(1,2))]
    return GeometryConditionedHistory(np.arange(steps)*dt,states,rhos,weights,hs,fidelity,hchange)
