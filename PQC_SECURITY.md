# Post-Quantum Cryptography Security Notes

## Implementation Security

### Key Management

**Private Keys:**
- Generated fresh for each workflow run
- Never stored in GitHub Secrets or repository
- Exist only in workflow runner memory during execution
- Automatically destroyed when workflow completes
- Cannot be recovered or reused

**Public Keys:**
- Distributed with signature bundles
- Safe to share publicly
- Used only for verification, not signing
- Should be cross-referenced with official sources

### Why Ephemeral Keys?

This implementation uses **ephemeral (one-time) keys** instead of long-lived keys because:

1. **Reduced Attack Surface**: No persistent key storage means no keys to steal
2. **Simplified Key Rotation**: Every release gets new keys automatically
3. **Defense in Depth**: Compromising one release doesn't affect others
4. **Workflow Isolation**: Each workflow run is cryptographically independent

### Trust Model

The security of this implementation relies on:

1. **GitHub Actions Security**: Workflows run in isolated, ephemeral environments
2. **Open Source Transparency**: All workflow code is publicly auditable
3. **Reproducibility**: Anyone can verify the signature generation process
4. **Distribution Integrity**: Signatures are distributed via GitHub's infrastructure

### Verification Chain

To trust a signed artifact:

1. ✅ Verify the signature with the included public key
2. ✅ Verify the workflow ran successfully in GitHub Actions
3. ✅ Verify the workflow is from the official repository
4. ✅ Compare artifact checksums in MANIFEST.txt

## Post-Quantum Security

### Algorithm: CRYSTALS-Dilithium3

- **Standard**: NIST FIPS 204 (ML-DSA-65)
- **Security Level**: NIST Level 3
  - Classical security: ~192 bits
  - Quantum security: ~128 bits (equivalent to AES-128)
- **Basis**: Module-LWE lattice problem
- **Status**: NIST-standardized, production-ready

### Threat Model

**Protected Against:**
- ✅ Classical computer attacks (now and future)
- ✅ Quantum computer attacks (Shor's algorithm)
- ✅ Signature forgery
- ✅ Message tampering

**Not Protected Against:**
- ❌ Compromised GitHub Actions infrastructure
- ❌ Malicious code in the workflow itself
- ❌ Social engineering attacks
- ❌ Vulnerabilities in verification tools

### Comparison with Classical Signatures

| Attack Type | RSA-2048 | ECDSA P-256 | Dilithium3 |
|-------------|----------|-------------|------------|
| Classical Brute Force | ✅ Secure | ✅ Secure | ✅ Secure |
| Shor's Algorithm (Quantum) | ❌ Broken | ❌ Broken | ✅ Secure |
| Grover's Algorithm (Quantum) | ⚠️ Weakened | ⚠️ Weakened | ✅ Secure |

## Implementation Details

### Libraries Used

All libraries are **open-source** and **actively maintained**:

| Library | License | Purpose | Repository |
|---------|---------|---------|------------|
| liboqs | MIT | PQC algorithm implementations | [open-quantum-safe/liboqs](https://github.com/open-quantum-safe/liboqs) |
| oqs-provider | MIT | OpenSSL 3 provider plugin | [open-quantum-safe/oqs-provider](https://github.com/open-quantum-safe/oqs-provider) |
| OpenSSL | Apache 2.0 | Cryptographic operations | [openssl/openssl](https://github.com/openssl/openssl) |

### Build Process Security

The workflow:
1. Builds all tools from source (no pre-compiled binaries)
2. Uses shallow clones from official repositories
3. Verifies tool functionality before signing
4. Creates tamper-evident manifest files

### Signature Format

```
Signature Algorithm: CRYSTALS-Dilithium3 (ML-DSA-65)
Hash Algorithm: SHA-256
Signature Size: 3,293 bytes
Format: DER-encoded (OpenSSL compatible)
```

Each artifact gets:
- A `.dilithium3.sig` signature file
- A SHA-256 hash in `MANIFEST.txt`
- Inclusion in the signed bundle

## Audit and Verification

### Workflow Auditability

Anyone can audit the signing process:

1. **View Workflow Logs**: All build steps are logged
2. **Review Workflow Code**: `.github/workflows/pqc-artifact-signing.yml` is public
3. **Verify Build Reproducibility**: Same inputs produce same outputs
4. **Check Artifact Integrity**: Workflow artifacts are immutable

### Third-Party Verification

To independently verify signatures without trusting our tools:

```bash
# Use official OQS Docker image
docker pull openquantumsafe/curl

# Verify a signature
docker run --rm -v $(pwd):/workspace openquantumsafe/curl \
  openssl dgst -sha256 -verify /workspace/dilithium3-public.pem \
    -provider oqsprovider -provider default \
    -signature /workspace/file.dilithium3.sig /workspace/file
```

## Best Practices for Users

### DO ✅

- Always verify signatures before using artifacts
- Use official verification tools (our script or OQS Docker image)
- Check that workflow ran successfully in GitHub Actions
- Compare file checksums with MANIFEST.txt
- Report any verification failures immediately

### DON'T ❌

- Use artifacts with failed signature verification
- Trust signatures without verifying them
- Use modified or unofficial verification tools
- Share or reuse private keys (they're ephemeral anyway)
- Skip verification for "trusted" sources

## Incident Response

### If Signature Verification Fails

1. **Stop**: Do not use the artifact
2. **Re-download**: Try downloading the artifact bundle again
3. **Verify Workflow**: Check that the GitHub Actions workflow succeeded
4. **Report**: Open a security issue if problem persists

### If Security Issue is Found

Report security issues to:
- GitHub Security Advisory (preferred)
- Repository Issues (for non-sensitive issues)

Include:
- Description of the issue
- Steps to reproduce
- Potential impact
- Suggested mitigation

## Future Considerations

### Algorithm Agility

This implementation can be extended to support:
- Multiple signature algorithms simultaneously
- Hybrid classical+quantum signatures
- Future NIST PQC standards (Falcon, SPHINCS+)

### Long-Term Archival

For long-term artifact preservation:
- Consider using multiple signature algorithms
- Store public keys separately from artifacts
- Document the verification process comprehensively
- Archive workflow code and logs

### Quantum Computer Timeline

Current estimates suggest large-scale quantum computers capable of breaking RSA/ECDSA may arrive in 10-30 years. This implementation provides protection starting **now**.

## References

### Standards
- [NIST FIPS 204](https://csrc.nist.gov/pubs/fips/204/ipd) - ML-DSA Standard
- [NIST PQC Project](https://csrc.nist.gov/projects/post-quantum-cryptography)

### Research
- [CRYSTALS-Dilithium](https://pq-crystals.org/dilithium/) - Official specification
- [OQS Project](https://openquantumsafe.org) - Implementation details

### Security Analysis
- Multiple independent security audits
- NIST evaluation process (2016-2024)
- Ongoing cryptanalysis by research community

---

**Last Updated**: 2026-01-25
**Version**: 1.0
**Status**: Production Ready ✅
