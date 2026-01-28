"""
PQC File Encryption Service
===========================
Encrypt files at rest with post-quantum cryptography.

Usage:
    from pqc_files import PQCFileService
    
    fs = PQCFileService()
    fs.encrypt_directory(Path("./sensitive"), "my-key")
    fs.decrypt_directory(Path("./sensitive"), "my-key")
"""

import os
import shutil
from pathlib import Path
from typing import List, Optional
from concurrent.futures import ThreadPoolExecutor
import json

try:
    from .pqc import PQCrypto, PQCKeyStore
except ImportError:
    from pqc import PQCrypto, PQCKeyStore


class PQCFileService:
    """Service for encrypting/decrypting files at rest."""
    
    ENCRYPTED_EXTENSION = ".pqc"
    MANIFEST_FILE = ".pqc-manifest.json"
    
    def __init__(self, key_store_path: Path = None):
        self._pqc = PQCrypto()
        self._store = PQCKeyStore(key_store_path)
    
    def encrypt_file(self, input_path: Path, key_name: str, 
                     output_path: Path = None, delete_original: bool = False) -> Path:
        """Encrypt a single file."""
        if output_path is None:
            output_path = input_path.with_suffix(input_path.suffix + self.ENCRYPTED_EXTENSION)
        
        pub_key = self._store.load_public_key(key_name)
        self._pqc.encrypt_file(input_path, output_path, pub_key)
        
        if delete_original:
            # Secure delete: overwrite before removing
            self._secure_delete(input_path)
        
        return output_path
    
    def decrypt_file(self, input_path: Path, key_name: str,
                     output_path: Path = None) -> Path:
        """Decrypt a single file."""
        if output_path is None:
            # Remove .pqc extension
            if input_path.suffix == self.ENCRYPTED_EXTENSION:
                output_path = input_path.with_suffix('')
            else:
                output_path = input_path.with_suffix('.decrypted')
        
        priv_key = self._store.load_private_key(key_name)
        self._pqc.decrypt_file(input_path, output_path, priv_key)
        
        return output_path
    
    def encrypt_directory(self, directory: Path, key_name: str,
                          patterns: List[str] = None, 
                          exclude: List[str] = None,
                          delete_originals: bool = False,
                          parallel: bool = True) -> dict:
        """
        Encrypt all files in a directory.
        
        Args:
            directory: Directory to encrypt
            key_name: Name of the key to use
            patterns: File patterns to include (e.g., ["*.txt", "*.json"])
            exclude: Patterns to exclude (e.g., ["*.log", ".git/*"])
            delete_originals: Securely delete original files after encryption
            parallel: Use parallel processing
        
        Returns:
            dict with encrypted files count and manifest
        """
        if patterns is None:
            patterns = ["*"]
        if exclude is None:
            exclude = [".git/*", "__pycache__/*", "*.pqc", self.MANIFEST_FILE]
        
        # Find all files
        files = []
        for pattern in patterns:
            for file_path in directory.rglob(pattern):
                if file_path.is_file():
                    # Check exclusions
                    excluded = False
                    for exc in exclude:
                        if file_path.match(exc):
                            excluded = True
                            break
                    if not excluded:
                        files.append(file_path)
        
        # Encrypt files
        manifest = {"encrypted_files": [], "key_name": key_name}
        
        def encrypt_one(path):
            try:
                out = self.encrypt_file(path, key_name, delete_original=delete_originals)
                return {"original": str(path), "encrypted": str(out), "status": "ok"}
            except Exception as e:
                return {"original": str(path), "status": "error", "error": str(e)}
        
        if parallel and len(files) > 1:
            with ThreadPoolExecutor(max_workers=4) as executor:
                results = list(executor.map(encrypt_one, files))
        else:
            results = [encrypt_one(f) for f in files]
        
        manifest["encrypted_files"] = results
        
        # Save manifest
        manifest_path = directory / self.MANIFEST_FILE
        manifest_path.write_text(json.dumps(manifest, indent=2))
        
        return manifest
    
    def decrypt_directory(self, directory: Path, key_name: str,
                          delete_encrypted: bool = False) -> dict:
        """Decrypt all .pqc files in a directory."""
        manifest_path = directory / self.MANIFEST_FILE
        
        # Find encrypted files
        encrypted_files = list(directory.rglob(f"*{self.ENCRYPTED_EXTENSION}"))
        
        results = []
        for enc_path in encrypted_files:
            try:
                out = self.decrypt_file(enc_path, key_name)
                if delete_encrypted:
                    enc_path.unlink()
                results.append({"encrypted": str(enc_path), "decrypted": str(out), "status": "ok"})
            except Exception as e:
                results.append({"encrypted": str(enc_path), "status": "error", "error": str(e)})
        
        # Clean up manifest
        if manifest_path.exists():
            manifest_path.unlink()
        
        return {"decrypted_files": results}
    
    def _secure_delete(self, path: Path, passes: int = 3):
        """Securely delete a file by overwriting with random data."""
        size = path.stat().st_size
        with open(path, 'r+b') as f:
            for _ in range(passes):
                f.seek(0)
                f.write(os.urandom(size))
                f.flush()
                os.fsync(f.fileno())
        path.unlink()


class PQCBackupService:
    """Encrypted backup service using PQC."""
    
    def __init__(self, backup_dir: Path, key_name: str):
        self.backup_dir = backup_dir
        self.key_name = key_name
        self._fs = PQCFileService()
        self.backup_dir.mkdir(parents=True, exist_ok=True)
    
    def backup(self, source: Path, name: str = None) -> Path:
        """Create an encrypted backup of a file or directory."""
        from datetime import datetime
        import tarfile
        import tempfile
        
        if name is None:
            name = source.name
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"{name}_{timestamp}"
        
        with tempfile.NamedTemporaryFile(suffix='.tar', delete=False) as tmp:
            tmp_path = Path(tmp.name)
        
        # Create tar archive
        with tarfile.open(tmp_path, 'w') as tar:
            tar.add(source, arcname=name)
        
        # Encrypt the archive
        encrypted_path = self.backup_dir / f"{backup_name}.tar.pqc"
        self._fs.encrypt_file(tmp_path, self.key_name, encrypted_path)
        
        # Clean up
        tmp_path.unlink()
        
        return encrypted_path
    
    def restore(self, backup_path: Path, destination: Path) -> Path:
        """Restore an encrypted backup."""
        import tarfile
        import tempfile
        
        with tempfile.NamedTemporaryFile(suffix='.tar', delete=False) as tmp:
            tmp_path = Path(tmp.name)
        
        # Decrypt
        self._fs.decrypt_file(backup_path, self.key_name, tmp_path)
        
        # Extract
        with tarfile.open(tmp_path, 'r') as tar:
            tar.extractall(destination)
        
        # Clean up
        tmp_path.unlink()
        
        return destination
    
    def list_backups(self) -> List[dict]:
        """List all backups."""
        backups = []
        for path in self.backup_dir.glob("*.tar.pqc"):
            backups.append({
                "name": path.stem.replace(".tar", ""),
                "path": str(path),
                "size": path.stat().st_size,
                "created": path.stat().st_ctime
            })
        return sorted(backups, key=lambda x: x["created"], reverse=True)


if __name__ == "__main__":
    import sys
    
    fs = PQCFileService()
    
    if len(sys.argv) < 2:
        print("PQC File Encryption Service")
        print("=" * 30)
        print("\nUsage:")
        print("  python pqc_files.py encrypt <file_or_dir> <key_name>")
        print("  python pqc_files.py decrypt <file_or_dir> <key_name>")
        print("  python pqc_files.py test")
        sys.exit(0)
    
    cmd = sys.argv[1]
    
    if cmd == "encrypt":
        path = Path(sys.argv[2])
        key = sys.argv[3]
        if path.is_file():
            result = fs.encrypt_file(path, key)
            print(f"✓ Encrypted: {result}")
        else:
            result = fs.encrypt_directory(path, key)
            print(f"✓ Encrypted {len(result['encrypted_files'])} files")
    
    elif cmd == "decrypt":
        path = Path(sys.argv[2])
        key = sys.argv[3]
        if path.is_file():
            result = fs.decrypt_file(path, key)
            print(f"✓ Decrypted: {result}")
        else:
            result = fs.decrypt_directory(path, key)
            print(f"✓ Decrypted {len(result['decrypted_files'])} files")
    
    elif cmd == "test":
        from pqc import PQCrypto
        
        print("Testing PQC File Service...")
        
        # Create test key
        pqc = PQCrypto()
        key = pqc.generate_encryption_keypair()
        store = PQCKeyStore()
        store.save_key(key, "test-file-key")
        
        # Create test file
        test_dir = Path("test_pqc_dir")
        test_dir.mkdir(exist_ok=True)
        (test_dir / "secret.txt").write_text("Top secret data!")
        (test_dir / "data.json").write_text('{"key": "value"}')
        
        # Encrypt directory
        result = fs.encrypt_directory(test_dir, "test-file-key")
        print(f"  ✓ Encrypted {len(result['encrypted_files'])} files")
        
        # Verify encrypted files exist
        assert (test_dir / "secret.txt.pqc").exists()
        
        # Decrypt
        result = fs.decrypt_directory(test_dir, "test-file-key", delete_encrypted=True)
        print(f"  ✓ Decrypted {len(result['decrypted_files'])} files")
        
        # Verify content
        assert (test_dir / "secret.txt").read_text() == "Top secret data!"
        
        # Cleanup
        shutil.rmtree(test_dir)
        print("\n✅ All file encryption tests passed!")
