#!/usr/bin/env python3
"""Securely configure IBM Quantum credentials for the music environment.

Run this script interactively. The API key is collected with a hidden prompt
and saved by Qiskit's account manager, never in the project repository.
"""

from __future__ import annotations

from getpass import getpass

from qiskit_ibm_runtime import QiskitRuntimeService


ACCOUNT_NAME = "quantum-sonification-workshop"


def main() -> None:
    print("IBM Quantum credential setup")
    print("The API key will be hidden and saved in Qiskit's user credential store.")
    token = getpass("IBM Cloud API key: ").strip()
    if not token:
        raise SystemExit("No API key entered; nothing was saved.")

    QiskitRuntimeService.save_account(
        channel="ibm_quantum_platform",
        token=token,
        name=ACCOUNT_NAME,
        overwrite=True,
        set_as_default=True,
    )
    del token

    print(f"Saved account: {ACCOUNT_NAME}")
    print("Validating access (this can take a few seconds)...")
    service = QiskitRuntimeService(name=ACCOUNT_NAME)
    backends = service.backends(operational=True)
    print(f"Credential valid; {len(backends)} operational backend(s) visible.")
    for backend in backends[:5]:
        print(f"  {backend.name}")


if __name__ == "__main__":
    main()
