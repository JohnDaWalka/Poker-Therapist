# Post-Quantum Cryptography Artifact Signing

## Overview

The Poker Therapist project uses **CRYSTALS-Dilithium** (NIST ML-DSA) for post-quantum cryptographic signing of build artifacts and releases. This ensures that even with the advent of quantum computers, the integrity and authenticity of our software can be verified.

## 🔐 Why Post-Quantum Cryptography?

Traditional digital signatures (RSA, ECDSA) will become vulnerable once large-scale quantum computers exist. Post-quantum cryptography algorithms like CRYSTALS-Dilithium are designed to resist attacks from both classical and quantum computers.

### CRYSTALS-Dilithium (ML-DSA)

- **NIST Standardized**: Selected by NIST as the primary post-quantum signature standard (ML-DSA)
- **Security Level**: Dilithium3 provides ~128-bit post-quantum security
- **Performance**: Fast signature generation and verification
- **License**: Open-source (CC0/Apache-2.0/MIT)

## 🚀 Quick Start

### Verifying Signatures

Download the signature bundle from GitHub Actions artifacts:

1. Go to the [Actions tab](../../actions/workflows/pqc-artifact-signing.yml)
2. Click on the latest successful workflow run
3. Download `pqc-dilithium3-signatures` artifact
4. Extract and verify:

```bash
# Extract the bundle
tar -xzf pqc-signatures.tar.gz
cd signed-artifacts

# Verify a file
openssl dgst -sha256 -verify dilithium3-public.pem \
  -provider oqsprovider -provider default \
  -signature requirements.txt.dilithium3.sig requirements.txt
```

## 📋 Prerequisites for Verification

To verify signatures, you need:

1. **OpenSSL 3.x** with **oqs-provider** plugin
2. The **dilithium3-public.pem** from the signature bundle
3. The original artifact files

### Installation Options

#### Option 1: Using Docker (Recommended)

The easiest way to verify signatures is using a Docker container with pre-built OQS tools:

```bash
# Pull the OQS OpenSSL image
docker pull openquantumsafe/curl

# Run verification in container
docker run -it --rm \
  -v $(pwd)/signed-artifacts:/workspace \
  openquantumsafe/curl \
  openssl dgst -sha256 -verify /workspace/dilithium3-public.pem \
    -provider oqsprovider -provider default \
    -signature /workspace/requirements.txt.dilithium3.sig \
    /workspace/requirements.txt
```

#### Option 2: Build from Source (Linux)

For advanced users who want to build the tools locally:

```bash
# Install build dependencies
sudo apt-get update
sudo apt-get install -y ninja-build cmake build-essential git

# Build liboqs
git clone https://github.com/open-quantum-safe/liboqs.git
cd liboqs
mkdir build && cd build
cmake -GNinja -DCMAKE_INSTALL_PREFIX=/opt/liboqs ..
ninja
sudo ninja install
cd ../..

# Build OpenSSL 3.x
git clone --branch openssl-3.4 https://github.com/openssl/openssl.git
cd openssl
./config --prefix=/opt/oqs-openssl
make -j$(nproc)
sudo make install_sw
cd ..

# Build oqs-provider
git clone https://github.com/open-quantum-safe/oqs-provider.git
cd oqs-provider
cmake -DOPENSSL_ROOT_DIR=/opt/oqs-openssl -DCMAKE_PREFIX_PATH=/opt/liboqs -S . -B _build
cmake --build _build
sudo cmake --install _build

# Test installation
/opt/oqs-openssl/bin/openssl list -providers -provider oqsprovider
```

## 🔧 Using the Signing Workflow

### Automatic Signing

Signatures are automatically generated:
- On every **release** (when you publish a GitHub release)
- Can be triggered **manually** via workflow dispatch

### Manual Trigger

To manually trigger signing:

1. Go to [Actions > Post-Quantum Artifact Signing](../../actions/workflows/pqc-artifact-signing.yml)
2. Click "Run workflow"
3. Optionally specify artifact patterns
4. Click "Run workflow" button

### What Gets Signed

The workflow signs:
- Python source files (`.py`)
- Configuration files (`requirements.txt`, `pyproject.toml`)
- Documentation (`README.md`)
- Any additional files specified

Each signed artifact gets:
- A `.dilithium3.sig` signature file
- An entry in `MANIFEST.txt` with SHA-256 hash

## 📁 Signature Bundle Contents

The signature bundle (`pqc-signatures.tar.gz`) contains:

```
signed-artifacts/
├── dilithium3-public.pem          # Public key for verification
├── README.md                        # Verification instructions
├── MANIFEST.txt                     # File checksums
├── requirements.txt                 # Original artifact
├── requirements.txt.dilithium3.sig  # Signature
├── pyproject.toml
├── pyproject.toml.dilithium3.sig
└── ...
```

## 🛡️ Security Best Practices

### For Contributors Verifying Signatures

1. **Always verify the public key fingerprint**: Compare the public key in the bundle with the one in the official repository
2. **Check multiple sources**: Verify that the workflow succeeded in GitHub Actions
3. **Use trusted tools**: Only use official OpenSSL and OQS builds
4. **Report issues**: If verification fails, report it immediately

### For Maintainers

1. **Private keys are ephemeral**: Each workflow run generates new keys
2. **Keys are never stored**: Private keys exist only during workflow execution
3. **Public keys are distributed**: Only public keys are included in artifacts
4. **Audit workflow runs**: Review Actions logs for any anomalies

## 🔬 Technical Details

### Signature Algorithm

- **Scheme**: CRYSTALS-Dilithium3 (ML-DSA-65)
- **Hash**: SHA-256
- **Security Level**: NIST Level 3 (~192-bit classical, ~128-bit quantum)
- **Public Key Size**: 1,952 bytes
- **Signature Size**: 3,293 bytes
- **Private Key Size**: 4,000 bytes

### Implementation

We use:
- **liboqs**: C library implementing quantum-safe algorithms (MIT License)
- **oqs-provider**: OpenSSL 3 provider plugin (MIT License)
- **OpenSSL 3.x**: Industry-standard cryptographic library (Apache 2.0)

### Comparison with Traditional Signatures

| Feature | ECDSA (P-256) | Dilithium3 | RSA-2048 |
|---------|---------------|------------|----------|
| Quantum-Safe | ❌ No | ✅ Yes | ❌ No |
| Public Key | 64 bytes | 1,952 bytes | 256 bytes |
| Signature | 64 bytes | 3,293 bytes | 256 bytes |
| Sign Speed | Fast | Very Fast | Medium |
| Verify Speed | Fast | Very Fast | Fast |

## 📚 Additional Resources

### Official Documentation
- [Open Quantum Safe](https://openquantumsafe.org/)
- [liboqs GitHub](https://github.com/open-quantum-safe/liboqs)
- [oqs-provider GitHub](https://github.com/open-quantum-safe/oqs-provider)
- [NIST Post-Quantum Cryptography](https://csrc.nist.gov/projects/post-quantum-cryptography)

### Academic Papers
- [CRYSTALS-Dilithium Paper](https://pq-crystals.org/dilithium/)
- [NIST ML-DSA Standard](https://csrc.nist.gov/pubs/fips/204/ipd)

### Community
- [OQS Community](https://github.com/open-quantum-safe)
- [PQC Forum](https://groups.google.com/a/list.nist.gov/g/pqc-forum)

## 🐛 Troubleshooting

### "Provider 'oqsprovider' not found"

**Solution**: Ensure oqs-provider is properly installed and OpenSSL can find it:
```bash
# Check if provider is available
openssl list -providers -provider oqsprovider
```

### "Verification failed"

**Possible causes**:
1. File was modified after signing
2. Wrong public key used
3. Signature file corrupted

**Solution**: Re-download the signature bundle and original artifacts.

### "Algorithm 'dilithium3' not found"

**Solution**: Your OpenSSL doesn't have the oqs-provider loaded:
```bash
# Load provider explicitly
openssl dgst -sha256 -verify dilithium3-public.pem \
  -provider-path /opt/oqs-provider/lib \
  -provider oqsprovider \
  -provider default \
  -signature file.sig file.txt
```

## 🤝 Contributing

If you find issues with the signing workflow or have suggestions:

1. Check existing [Issues](../../issues)
2. Review the [workflow file](../../.github/workflows/pqc-artifact-signing.yml)
3. Open a new issue with:
   - Clear description
   - Steps to reproduce
   - Expected vs actual behavior
   - Your environment details

## 📝 License

This implementation uses:
- **liboqs**: MIT License
- **oqs-provider**: MIT License  
- **OpenSSL**: Apache 2.0 License
- **CRYSTALS-Dilithium**: CC0 (public domain)

All components are open-source and freely usable per the requirements.

---

**Last Updated**: 2026-01-25  
**Maintained By**: Poker Therapist Team  
**Status**: ✅ Active and Production-Ready
