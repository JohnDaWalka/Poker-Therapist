# Post-Quantum Cryptography Quick Start Guide

This guide helps you get started with post-quantum artifact signing and verification.

## For Users: Verifying Signatures

### Prerequisites
- Python 3.8+
- Docker (recommended) OR OpenSSL 3.x with oqs-provider

### Steps

1. **Download the signature bundle** from GitHub Actions:
   - Go to [Actions > Post-Quantum Artifact Signing](https://github.com/JohnDaWalka/Poker-Therapist/actions/workflows/pqc-artifact-signing.yml)
   - Click on a successful workflow run
   - Download the `pqc-dilithium3-signatures` artifact
   - Extract the ZIP file

2. **Run the verification script**:
   ```bash
   cd Poker-Therapist
   python scripts/verify_pqc_signatures.py path/to/signed-artifacts/
   ```

3. **Interpret results**:
   - ✓ Green checks = Signatures verified, artifacts are authentic
   - ✗ Red errors = Verification failed, DO NOT USE these artifacts

## For Maintainers: Triggering Signing

### Manual Workflow Trigger

1. Go to [Actions > Post-Quantum Artifact Signing](https://github.com/JohnDaWalka/Poker-Therapist/actions/workflows/pqc-artifact-signing.yml)
2. Click "Run workflow"
3. Select branch (usually `main`)
4. Optionally specify artifact patterns
5. Click "Run workflow" button

### Automatic on Release

The workflow automatically runs when you:
1. Create a new GitHub release
2. Publish the release

The signatures will be:
- Uploaded as workflow artifacts
- Added to the release notes automatically

## Testing the Workflow

To test that signing works:

```bash
# 1. Trigger the workflow manually (see above)

# 2. Wait for completion (5-10 minutes)

# 3. Download the artifacts

# 4. Verify with the script
python scripts/verify_pqc_signatures.py signed-artifacts/

# 5. Check that all signatures verify successfully
```

## Advanced: Docker Verification

If you have Docker but the Python script doesn't detect it:

```bash
# Force Docker mode
python scripts/verify_pqc_signatures.py --use-docker signed-artifacts/

# Or verify manually
docker run -it --rm \
  -v $(pwd)/signed-artifacts:/workspace \
  openquantumsafe/curl \
  openssl dgst -sha256 -verify /workspace/dilithium3-public.pem \
    -provider oqsprovider -provider default \
    -signature /workspace/requirements.txt.dilithium3.sig \
    /workspace/requirements.txt
```

## Troubleshooting

### "No suitable verification method found"

**Solution**: Install Docker:
```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install docker.io
sudo systemctl start docker
sudo usermod -aG docker $USER
# Log out and back in
```

### "Signature verification FAILED"

**Possible causes**:
1. File was tampered with after signing
2. Signature file is corrupted
3. Wrong public key used

**Solution**: Re-download the artifact bundle and try again.

### "Provider 'oqsprovider' not found" (local OpenSSL)

**Solution**: Use Docker instead:
```bash
python scripts/verify_pqc_signatures.py --use-docker signed-artifacts/
```

Or install oqs-provider locally (see [PQC_SIGNING.md](../PQC_SIGNING.md))

## More Information

- Full documentation: [PQC_SIGNING.md](../PQC_SIGNING.md)
- Open Quantum Safe: https://openquantumsafe.org
- NIST PQC Project: https://csrc.nist.gov/projects/post-quantum-cryptography

## Security Notice

⚠️ **NEVER** use artifacts with failed signature verification!

This could indicate:
- Tampering or malicious modification
- Corruption during download
- Man-in-the-middle attack

Always verify signatures before using any artifacts in production.
