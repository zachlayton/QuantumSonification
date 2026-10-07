"""Declared musical lookup over read-only density and transition observations.

Computational q3..q0 coordinates index a 4x4 bank: quality by row, inversion
by column. These are musical assignments, not quantum energy-frequency laws.
"""
from dataclasses import dataclass
import numpy as np
from qmw.core.transition import readonly

QUALITY_NAMES = ('major 7', 'minor 7', 'dominant 7', 'half diminished')
QUALITY_RATIOS = ((1, 5/4, 3/2, 15/8), (1, 6/5, 3/2, 9/5),
                  (1, 5/4, 3/2, 7/4), (1, 6/5, 7/5, 9/5))
HARMONY_COUNT = 4 + 16*12

@dataclass(frozen=True)
class ChordMatrixFrame:
    position_cv: float
    size_cv: float
    active_cell: int
    # root Hz, quality, inversion, weight, four frequencies, four amplitudes
    cells: np.ndarray

    def arguments(self):
        return [1, self.position_cv, self.size_cv, self.active_cell, *self.cells.ravel().tolist()]

    def audit(self):
        return dict(mapping='computational_population_and_projected_transition_bank.v1',
                    position_cv=self.position_cv, size_cv=self.size_cv,
                    active_cell=self.active_cell, cells=self.cells.tolist(),
                    quality_names=QUALITY_NAMES,
                    position_source='computational population centroid: sum(i*rho[i,i])/15',
                    size_source='computational l1 coherence: sum offdiag abs(rho)/15',
                    weights='normalized population * (1 + 16 * projected outgoing diagnostic activity)',
                    key='nearest semitone of 12 * computational population centroid; base Hz is lower key',
                    warning='musical lookup; frequencies are not delta_E/hbar')


def chord_matrix(rho, frame, *, base_hz=220., octave=0):
    """Build sixteen four-note chords and bounded density CVs without changing rho.

    Transition activity is projected to computational coordinates through |V|^2;
    an energy rank is never silently treated as a computational basis index.
    This makes the mapping insensitive to arbitrary eigenvector phase choices.
    At exact energy degeneracies individual transitions still inherit the
    observer's documented basis policy; HOLD is useful for fixed-frame study.
    """
    rho=np.asarray(rho, dtype=complex)
    if rho.shape != (16,16) or not np.isfinite(rho).all():
        raise ValueError('harmony requires the validated 16-state density matrix')
    if not np.isfinite(base_hz) or not 55 <= base_hz <= 880 or type(octave) is not int or not -2 <= octave <= 2:
        raise ValueError('invalid harmony pitch reference')
    populations=np.maximum(rho.diagonal().real,0)
    populations=populations/populations.sum()
    position=float(np.clip(populations @ np.arange(16)/15,0,1))
    coherence=float(np.clip((np.abs(rho).sum()-np.abs(rho.diagonal()).sum())/15,0,1))
    outgoing=frame.diagnostic_activity.copy()
    np.fill_diagonal(outgoing,0)
    outgoing=outgoing.sum(axis=0)
    total=outgoing.sum()
    projected=(np.abs(frame.eigenvectors)**2) @ (outgoing/total if total>0 else np.zeros(16))
    weights=populations*(1+16*projected)
    weights=weights/weights.sum()
    key=int(np.floor(12*position+.5))
    root=base_hz * 2**(octave + key/12)
    # Fold the entire chord down together at extreme reference/octave settings.
    while root*3.75 >= 16000:
        root/=2
    cells=[]
    for index in range(16):
        quality,inversion=divmod(index,4)
        ratios=np.asarray(QUALITY_RATIOS[quality])
        frequencies=np.concatenate((ratios[inversion:],2*ratios[:inversion]))*root
        # Each note's amplitude comes from the corresponding qubit marginal,
        # normalized with a nonzero floor so all four notes remain audible.
        marginals=np.array([sum(populations[i] for i in range(16) if (i>>q)&1) for q in range(4)])
        amplitudes=.25+.75*marginals
        amplitudes=amplitudes/amplitudes.sum()
        cells.append([root,quality,inversion,weights[index],*frequencies,*amplitudes])
    return ChordMatrixFrame(position,coherence,int(np.argmax(weights)),readonly(cells))


def validate_harmony_arguments(args):
    if len(args)!=HARMONY_COUNT or args[0]!=1:
        raise ValueError('incomplete harmony frame')
    a=np.asarray(args,dtype=float)
    if not np.isfinite(a).all() or not 0<=a[1]<=1 or not 0<=a[2]<=1 or a[3]!=int(a[3]) or not 0<=a[3]<16:
        raise ValueError('invalid harmony metadata')
    rows=a[4:].reshape(16,12)
    if np.any(rows[:,0]<=0) or not np.array_equal(rows[:,1],np.repeat(np.arange(4),4)) or not np.array_equal(rows[:,2],np.tile(np.arange(4),4)):
        raise ValueError('invalid chord identities')
    if np.any(rows[:,3]<0) or not np.isclose(rows[:,3].sum(),1,atol=1e-5):
        raise ValueError('invalid chord weights')
    if np.any(rows[:,4:8]<=0) or np.any(rows[:,4:8]>=18000) or np.any(np.diff(rows[:,4:8],axis=1)<=0):
        raise ValueError('invalid chord voicing')
    if np.any(rows[:,8:]<=0) or not np.allclose(rows[:,8:].sum(axis=1),1,atol=1e-5):
        raise ValueError('invalid chord note amplitudes')
    return True
