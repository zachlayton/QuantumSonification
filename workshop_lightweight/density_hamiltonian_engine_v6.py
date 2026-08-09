"""Density-matrix-driven two-spin Hamiltonian line analysis for workshop V6."""
from __future__ import annotations
import numpy as np

I=np.eye(2,dtype=complex)
X=np.array([[0,1],[1,0]],complex)
Y=np.array([[0,-1j],[1j,0]],complex)
Z=np.array([[1,0],[0,-1]],complex)
P={"I":I,"X":X,"Y":Y,"Z":Z}
LABELS=("XI","YI","ZI","IX","IY","IZ","XX","XY","XZ","YX","YY","YZ","ZX","ZY","ZZ")

def density_from_pauli15(values: dict[str,float]) -> np.ndarray:
    rho=np.kron(I,I)
    for label in LABELS:
        rho += float(values[label])*np.kron(P[label[0]],P[label[1]])
    return rho/4.0

def density_hamiltonian_transitions(values: dict[str,float], field=(0.,0.,1.), gamma_hz=12., coupling_hz=2., base_hz=33.):
    """Return six (frequency, magnitude, phase) density-modulated lines.

    Hamiltonian entries are expressed in Hz, so eigenvalue gaps directly map
    to acoustic frequency offsets.  The transverse magnetic-dipole operator
    supplies transition selection strength; rho supplies complex excitation.
    """
    b=np.asarray(field,float); norm=float(np.linalg.norm(b))
    if norm==0: b=np.array([0.,0.,1.]); norm=0.
    single=b[0]*X+b[1]*Y+b[2]*Z
    h=-0.5*gamma_hz*(np.kron(single,I)+np.kron(I,single))+0.25*coupling_hz*np.kron(Z,Z)
    energies,vectors=np.linalg.eigh(h)
    rho_e=vectors.conj().T@density_from_pauli15(values)@vectors
    # Dipole component perpendicular to B; choose a stable orthogonal axis.
    bhat=b/(np.linalg.norm(b) or 1.); ref=np.array([1.,0.,0.])
    if abs(float(np.dot(bhat,ref)))>.9: ref=np.array([0.,1.,0.])
    transverse=np.cross(bhat,ref); transverse/=np.linalg.norm(transverse)
    dip=transverse[0]*X+transverse[1]*Y+transverse[2]*Z
    dip_e=vectors.conj().T@(np.kron(dip,I)+np.kron(I,dip))@vectors
    lines=[]
    for lo in range(4):
        for hi in range(lo+1,4):
            excitation=rho_e[lo,hi]*dip_e[hi,lo]
            lines.append((max(1.,base_hz+float(energies[hi]-energies[lo])),float(abs(excitation)),float(np.angle(excitation))))
    return lines
