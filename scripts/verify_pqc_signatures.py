#!/usr/bin/env python3
"""
Post-Quantum Signature Verification Script

This script helps contributors verify CRYSTALS-Dilithium signatures
on Poker Therapist artifacts without manually running OpenSSL commands.

Requirements:
- Docker (recommended) OR
- OpenSSL 3.x with oqs-provider installed locally

Usage:
    python verify_pqc_signatures.py <signature-bundle-dir>
    python verify_pqc_signatures.py signed-artifacts/

License: MIT
"""

import argparse
import subprocess
import sys
from pathlib import Path
from typing import List, Tuple


class Colors:
    """ANSI color codes for terminal output"""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'


def print_header(text: str) -> None:
    """Print a formatted header"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*70}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text:^70}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*70}{Colors.END}\n")


def print_success(text: str) -> None:
    """Print success message"""
    print(f"{Colors.GREEN}✓ {text}{Colors.END}")


def print_error(text: str) -> None:
    """Print error message"""
    print(f"{Colors.RED}✗ {text}{Colors.END}")


def print_warning(text: str) -> None:
    """Print warning message"""
    print(f"{Colors.YELLOW}⚠ {text}{Colors.END}")


def print_info(text: str) -> None:
    """Print info message"""
    print(f"{Colors.BLUE}ℹ {text}{Colors.END}")


def check_docker() -> bool:
    """Check if Docker is available"""
    try:
        result = subprocess.run(
            ["docker", "--version"],
            capture_output=True,
            text=True,
            timeout=5
        )
        return result.returncode == 0
    except (subprocess.SubprocessError, FileNotFoundError):
        return False


def check_local_openssl() -> bool:
    """Check if local OpenSSL with oqs-provider is available"""
    openssl_paths = [
        "/opt/oqs-openssl/bin/openssl",
        "openssl"
    ]
    
    for openssl_path in openssl_paths:
        try:
            result = subprocess.run(
                [openssl_path, "list", "-providers", "-provider", "oqsprovider"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0 and "oqsprovider" in result.stdout.lower():
                return True
        except (subprocess.SubprocessError, FileNotFoundError):
            continue
    
    return False


def verify_signature_docker(
    bundle_dir: Path,
    artifact: Path,
    signature: Path,
    public_key: Path
) -> bool:
    """Verify signature using Docker container"""
    try:
        cmd = [
            "docker", "run", "--rm",
            "-v", f"{bundle_dir.absolute()}:/workspace",
            "openquantumsafe/curl",
            "openssl", "dgst", "-sha256",
            "-verify", f"/workspace/{public_key.name}",
            "-provider", "oqsprovider",
            "-provider", "default",
            "-signature", f"/workspace/{signature.name}",
            f"/workspace/{artifact.name}"
        ]
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30
        )
        
        return result.returncode == 0 and "Verified OK" in result.stdout
    except subprocess.SubprocessError as e:
        print_error(f"Docker verification failed: {e}")
        return False


def verify_signature_local(
    artifact: Path,
    signature: Path,
    public_key: Path
) -> bool:
    """Verify signature using local OpenSSL"""
    openssl_paths = ["/opt/oqs-openssl/bin/openssl", "openssl"]
    
    for openssl_path in openssl_paths:
        try:
            cmd = [
                openssl_path, "dgst", "-sha256",
                "-verify", str(public_key),
                "-provider", "oqsprovider",
                "-provider", "default",
                "-signature", str(signature),
                str(artifact)
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0 and "Verified OK" in result.stdout:
                return True
        except (subprocess.SubprocessError, FileNotFoundError):
            continue
    
    return False


def find_signature_pairs(bundle_dir: Path) -> List[Tuple[Path, Path]]:
    """Find all artifact-signature pairs in the bundle directory"""
    pairs = []
    
    for sig_file in bundle_dir.glob("*.dilithium3.sig"):
        # Get the original artifact name by removing .dilithium3.sig
        artifact_name = sig_file.name.replace(".dilithium3.sig", "")
        artifact_file = bundle_dir / artifact_name
        
        if artifact_file.exists() and artifact_file.is_file():
            pairs.append((artifact_file, sig_file))
    
    return pairs


def main() -> int:
    """Main verification function"""
    parser = argparse.ArgumentParser(
        description="Verify CRYSTALS-Dilithium post-quantum signatures"
    )
    parser.add_argument(
        "bundle_dir",
        type=Path,
        help="Directory containing signature bundle (e.g., signed-artifacts/)"
    )
    parser.add_argument(
        "--use-docker",
        action="store_true",
        help="Force use of Docker for verification"
    )
    parser.add_argument(
        "--use-local",
        action="store_true",
        help="Force use of local OpenSSL for verification"
    )
    
    args = parser.parse_args()
    
    print_header("Post-Quantum Signature Verification")
    
    # Check if bundle directory exists
    if not args.bundle_dir.exists():
        print_error(f"Bundle directory not found: {args.bundle_dir}")
        return 1
    
    if not args.bundle_dir.is_dir():
        print_error(f"Not a directory: {args.bundle_dir}")
        return 1
    
    # Find public key
    public_key = args.bundle_dir / "dilithium3-public.pem"
    if not public_key.exists():
        print_error(f"Public key not found: {public_key}")
        print_info("Expected file: dilithium3-public.pem")
        return 1
    
    print_success(f"Found public key: {public_key.name}")
    
    # Find signature pairs
    pairs = find_signature_pairs(args.bundle_dir)
    
    if not pairs:
        print_warning("No signature files found in bundle")
        print_info("Looking for files matching pattern: *.dilithium3.sig")
        return 1
    
    print_success(f"Found {len(pairs)} artifact-signature pair(s)")
    
    # Determine verification method
    use_docker = False
    use_local = False
    
    if args.use_docker and args.use_local:
        print_error("Cannot specify both --use-docker and --use-local")
        return 1
    
    if args.use_docker:
        use_docker = True
    elif args.use_local:
        use_local = True
    else:
        # Auto-detect
        has_docker = check_docker()
        has_local = check_local_openssl()
        
        if has_docker:
            use_docker = True
            print_info("Using Docker for verification (recommended)")
        elif has_local:
            use_local = True
            print_info("Using local OpenSSL with oqs-provider")
        else:
            print_error("No suitable verification method found")
            print_info("Please install either:")
            print_info("  1. Docker (recommended), OR")
            print_info("  2. OpenSSL 3.x with oqs-provider")
            print_info("\nSee PQC_SIGNING.md for installation instructions")
            return 1
    
    # Verify each signature
    print_header("Verifying Signatures")
    
    verified_count = 0
    failed_count = 0
    
    for artifact, signature in pairs:
        print(f"\nVerifying: {Colors.BOLD}{artifact.name}{Colors.END}")
        
        try:
            if use_docker:
                verified = verify_signature_docker(
                    args.bundle_dir, artifact, signature, public_key
                )
            else:
                verified = verify_signature_local(
                    artifact, signature, public_key
                )
            
            if verified:
                print_success(f"Signature valid for {artifact.name}")
                verified_count += 1
            else:
                print_error(f"Signature verification FAILED for {artifact.name}")
                failed_count += 1
        except Exception as e:
            print_error(f"Error verifying {artifact.name}: {e}")
            failed_count += 1
    
    # Print summary
    print_header("Verification Summary")
    
    print(f"Total artifacts:     {len(pairs)}")
    print(f"Verified:           {Colors.GREEN}{verified_count}{Colors.END}")
    print(f"Failed:             {Colors.RED}{failed_count}{Colors.END}")
    
    if failed_count == 0:
        print_success("\nAll signatures verified successfully! ✓")
        print_info("Artifacts are authentic and have not been tampered with.")
        return 0
    else:
        print_error(f"\n{failed_count} signature(s) failed verification!")
        print_warning("DO NOT use artifacts with failed signatures.")
        print_info("This may indicate tampering or corruption.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
