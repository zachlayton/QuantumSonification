#!/usr/bin/env python3
import tempfile
from pathlib import Path
import numpy as np

from pubchem_molecular_loader_v1 import PubChemQuery, build_record_url, pubchem_record_to_molecule
from molecular_geometry_layer_v1 import molecule_to_packet

MOCK_WATER = {
  "PC_Compounds": [{
    "id": {"id": {"cid": 962}},
    "atoms": {"aid": [1,2,3], "element": [8,1,1]},
    "bonds": {"aid1": [1,1], "aid2": [2,3], "order": [1,1]},
    "coords": [{"aid": [1,2,3], "conformers": [{
      "x": [0.0, 0.9572, -0.23999],
      "y": [0.0, 0.0, 0.92663],
      "z": [0.0, 0.0, 0.0],
      "data": [{"label": "Conformer", "value": {"sval": "mock"}}]
    }]}]
  }]
}

def main():
    q=PubChemQuery('name','water')
    assert 'record_type=3d' in build_record_url(q)
    mol=pubchem_record_to_molecule(MOCK_WATER,q)
    assert mol.elements == ['O','H','H']
    assert mol.bonds.shape == (2,2)
    assert np.allclose(mol.bond_orders,[1,1])
    packet=molecule_to_packet(mol)
    assert packet.n_vertices == 3 and packet.n_modes == 3
    assert packet.metadata['pubchem_cid'] == 962
    with tempfile.TemporaryDirectory() as td:
        path=Path(td)/'water.npz'; packet.save_npz(path); assert path.exists()
    print('pubchem loader tests passed')

if __name__=='__main__': main()
