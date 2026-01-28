# Post-Quantum Cryptography - Poker-Therapist

This repository is protected with **NIST post-quantum cryptography**.

## Algorithms
- **ML-KEM-1024** (FIPS 203) - Key Encapsulation
- **ML-DSA-87** (FIPS 204) - Digital Signatures
- **AES-256-GCM** - Symmetric Encryption

## Usage

```bash
# Generate keys
python pqc.py keygen poker_therapist

# Encrypt sensitive files
python pqc_files.py encrypt <file> <key_name>

# Verify signatures
python pqc.py verify <signed_file>
```

## Key Storage
Keys are stored in `~/.pqc-keys/`
- Public keys (`*.pub.json`) can be committed
- Private keys (`*.key`) must NEVER be committed
