import tempfile
from pathlib import Path
import numpy as np
if __package__:
    from .spectral_geometry_packet_v1 import SpectralGeometryPacket
else:  # Direct-test compatibility.
    from spectral_geometry_packet_v1 import SpectralGeometryPacket
from molecular_geometry_layer_v1 import BUILTINS,load_builtin_molecule,molecule_to_packet

def main():
    for name in BUILTINS:
        p=molecule_to_packet(load_builtin_molecule(name)); assert p.eigenvectors.shape==(p.n_vertices,p.n_modes); assert np.all(p.eigenvalues>=-1e-10)
    p=molecule_to_packet(load_builtin_molecule('methane'))
    with tempfile.TemporaryDirectory() as d:
        f=Path(d)/'p.npz'; p.save_npz(f); q=SpectralGeometryPacket.load_npz(f); assert np.allclose(p.eigenvalues,q.eigenvalues); assert q.geometry_kind=='molecular_graph'
    print('all molecular geometry v1 tests passed')
if __name__=='__main__': main()
