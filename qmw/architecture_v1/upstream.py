"""Explicit, fingerprint-checked imports of approved external QMW source owners.

These repository-relative paths are declared in the integration manifest.
No external code is downloaded, generated, or silently replaced by a fixture.
"""
from __future__ import annotations
import hashlib
import importlib
import importlib.util
import json
from pathlib import Path
import sys
from types import MappingProxyType, SimpleNamespace

SOURCE_ROOT = Path(__file__).resolve().parents[2]
REGISTRY = SOURCE_ROOT / 'docs/qmw_architecture/external-sources.json'


def resolve_source(relative_path):
    """Resolve an approved path within this checkout, independently of cwd."""
    relative = Path(relative_path)
    path = (SOURCE_ROOT / relative).resolve()
    if relative.is_absolute() or not path.is_relative_to(SOURCE_ROOT):
        raise ValueError('registered source must remain inside the repository')
    return path


def verify_files(root, fingerprints):
    root=Path(root).resolve()
    for name,expected in fingerprints.items():
        path=(root/name).resolve()
        if not path.is_relative_to(root) or not path.is_file():
            raise ValueError(f'registered source unavailable: {path}')
        actual=hashlib.sha256(path.read_bytes()).hexdigest()
        if actual!=expected:
            raise ValueError(f'registered source changed: {path}; request an explicit source handoff refresh')


def _registry():
    return json.loads(REGISTRY.read_text())


def _load_names(root,names):
    # Reject already-loaded packages from a different checkout before import.
    for name in names:
        for prefix in (name.split('.')[0],name):
            m=sys.modules.get(prefix)
            if m is not None and not str(getattr(m,'__file__','')).startswith(str(root)+'/'):
                raise ValueError(f'{prefix} already loaded from another source')
    if str(root) not in sys.path:sys.path.insert(0,str(root))
    result=[]
    for name in names:
        m=importlib.import_module(name)
        if not str(m.__file__).startswith(str(root)+'/'):
            raise ValueError(f'{name} resolved outside approved source')
        result.append(m)
    return result


def load_collider_runtime():
    spec=_registry()['collider'];root=resolve_source(spec['root'])
    verify_files(root,spec['files'])
    model,io,backend,synthetic,spectrum=_load_names(root,[
        'collider_001a.model','collider_001a.io','collider_001a.backend',
        'collider_001a.synthetic','collider_001b.spectrum'])
    return SimpleNamespace(root=str(root),fingerprints=MappingProxyType(spec['files']),
        model=model,io=io,backend=backend,synthetic=synthetic,spectrum=spectrum)


def load_decay_runtime():
    spec=_registry()['decay'];archive=resolve_source(spec['archive'])
    verify_files(archive.parent,{archive.name:spec['sha256']})
    prefix=Path(spec['package_prefix'])
    if prefix.is_absolute() or '..' in prefix.parts:
        raise ValueError('registered archive package must remain inside the repository archive')
    root=str(archive)+'/'+prefix.as_posix()
    contracts,validation,admission,fixtures=_load_names(root,[
        'qmw_decay.contracts','qmw_decay.validation','qmw_decay.admission','qmw_decay.fixtures'])
    return SimpleNamespace(archive=str(archive),sha256=spec['sha256'],contracts=contracts,
        validation=validation,admission=admission,fixtures=fixtures)


def load_lorentz_frame_type():
    spec=_registry()['lorentz_frame'];path=resolve_source(spec['path'])
    verify_files(path.parent,{path.name:spec['sha256']})
    name='_qmw_architecture_existing_lorentz_frame'
    if name not in sys.modules:
        module_spec=importlib.util.spec_from_file_location(name,path)
        module=importlib.util.module_from_spec(module_spec)
        sys.modules[name]=module
        try:module_spec.loader.exec_module(module)
        except BaseException:
            sys.modules.pop(name,None)
            raise
    elif Path(sys.modules[name].__file__).resolve() != path:
        raise ValueError('LorentzFrame already loaded from another source')
    return sys.modules[name].LorentzFrame
