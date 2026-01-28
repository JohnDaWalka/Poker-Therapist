# Post-Quantum Cryptography (PQC) Security

This repository is protected with **NIST-standardized post-quantum cryptography**.

## Algorithms Used
- **ML-KEM-1024** (FIPS 203) - Key encapsulation
- **ML-DSA-87** (FIPS 204) - Digital signatures
- **AES-256-GCM** - Symmetric encryption

## Files
- `pqc.py` - Core PQC module
- `pqc_api.py` - API protection utilities
- `pqc_files.py` - File encryption utilities

## Usage
```python
from pqc import PQCrypto
pqc = PQCrypto()
encrypted = pqc.encrypt(data, public_key)
```

## Key Management
Public keys are in `security/` directory.
Private keys are stored locally in `~/.pqc-keys/`

---
*Secured with quantum-resistant cryptography*
