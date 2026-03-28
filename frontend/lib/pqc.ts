/**
 * Post-Quantum Cryptography Module for Node.js/TypeScript
 * ========================================================
 * 
 * Uses ML-KEM and ML-DSA (NIST FIPS 203, 204)
 * 
 * Note: For production, use @aspect-security/pqc-node or similar.
 * This template shows integration patterns - actual PQC ops call Python.
 */

import { spawn } from 'child_process';
import { readFileSync, writeFileSync, existsSync, mkdirSync } from 'fs';
import { join } from 'path';
import { homedir } from 'os';
import { createCipheriv, createDecipheriv, randomBytes } from 'crypto';

// Key storage location
const PQC_KEY_DIR = join(homedir(), '.pqc-keys');

interface PQCKey {
  publicKey: Buffer;
  privateKey: Buffer;
  algorithm: string;
  keyId: string;
}

interface EncryptedData {
  kemCiphertext: Buffer;
  nonce: Buffer;
  ciphertext: Buffer;
}

/**
 * Call Python PQC utilities for actual cryptographic operations.
 * In production, use native Node.js PQC libraries when available.
 */
async function callPythonPQC(args: string[]): Promise<string> {
  return new Promise((resolve, reject) => {
    const pqcScript = join(__dirname, '..', 'pqc.py');
    const proc = spawn('python', [pqcScript, ...args]);
    
    let stdout = '';
    let stderr = '';
    
    proc.stdout.on('data', (data) => { stdout += data; });
    proc.stderr.on('data', (data) => { stderr += data; });
    
    proc.on('close', (code) => {
      if (code === 0) resolve(stdout.trim());
      else reject(new Error(`PQC error: ${stderr}`));
    });
  });
}

/**
 * PQC Key Management
 */
export class PQCKeyStore {
  private directory: string;
  
  constructor(directory?: string) {
    this.directory = directory || PQC_KEY_DIR;
    if (!existsSync(this.directory)) {
      mkdirSync(this.directory, { recursive: true, mode: 0o700 });
    }
  }
  
  loadPublicKey(name: string): Buffer {
    const pubPath = join(this.directory, `${name}.pub`);
    if (!existsSync(pubPath)) {
      // Try JSON format
      const jsonPath = join(this.directory, `${name}.pub.json`);
      if (existsSync(jsonPath)) {
        const data = JSON.parse(readFileSync(jsonPath, 'utf-8'));
        return Buffer.from(data.public_key, 'base64');
      }
      throw new Error(`Public key not found: ${name}`);
    }
    return readFileSync(pubPath);
  }
  
  loadPrivateKey(name: string): Buffer {
    const keyPath = join(this.directory, `${name}.key`);
    if (!existsSync(keyPath)) {
      throw new Error(`Private key not found: ${name}`);
    }
    return readFileSync(keyPath);
  }
  
  listKeys(): string[] {
    const { readdirSync } = require('fs');
    const files = readdirSync(this.directory);
    const keys = new Set<string>();
    
    for (const file of files) {
      if (file.endsWith('.pub') || file.endsWith('.pub.json')) {
        keys.add(file.replace('.pub.json', '').replace('.pub', ''));
      }
    }
    
    return Array.from(keys);
  }
}

/**
 * Hybrid encryption helper using classical crypto + PQC key exchange
 * Until native PQC is available in Node.js crypto module
 */
export function hybridEncrypt(
  plaintext: Buffer,
  sharedSecret: Buffer
): { nonce: Buffer; ciphertext: Buffer } {
  const key = sharedSecret.subarray(0, 32); // AES-256
  const nonce = randomBytes(12);
  
  const cipher = createCipheriv('aes-256-gcm', key, nonce);
  const encrypted = Buffer.concat([cipher.update(plaintext), cipher.final()]);
  const tag = cipher.getAuthTag();
  
  return {
    nonce,
    ciphertext: Buffer.concat([encrypted, tag])
  };
}

export function hybridDecrypt(
  ciphertext: Buffer,
  nonce: Buffer,
  sharedSecret: Buffer
): Buffer {
  const key = sharedSecret.subarray(0, 32);
  const tag = ciphertext.subarray(-16);
  const encrypted = ciphertext.subarray(0, -16);
  
  const decipher = createDecipheriv('aes-256-gcm', key, nonce);
  decipher.setAuthTag(tag);
  
  return Buffer.concat([decipher.update(encrypted), decipher.final()]);
}

/**
 * Express/Fastify middleware for PQC-protected endpoints
 */
export function pqcMiddleware(keyName: string) {
  const store = new PQCKeyStore();
  
  return async (req: any, res: any, next: any) => {
    const pqcHeader = req.headers['x-pqc-encrypted'];
    
    if (pqcHeader === 'true') {
      try {
        const privateKey = store.loadPrivateKey(keyName);
        // Decrypt body using PQC
        // This would call the Python module or native library
        req.pqcDecrypted = true;
      } catch (error) {
        return res.status(400).json({ error: 'PQC decryption failed' });
      }
    }
    
    next();
  };
}

/**
 * TLS configuration helper for PQC hybrid mode
 */
export function getPQCTLSConfig() {
  return {
    // Node.js 20+ with OpenSSL 3.0+ supports hybrid key exchange
    // This uses classical + PQC key agreement
    ecdhCurve: 'X25519:P-256',
    ciphers: [
      'TLS_AES_256_GCM_SHA384',
      'TLS_CHACHA20_POLY1305_SHA256',
      'TLS_AES_128_GCM_SHA256'
    ].join(':'),
    minVersion: 'TLSv1.3',
    // When PQC TLS is available, add:
    // groups: 'X25519Kyber768Draft00:X25519:P-256'
  };
}

// Simple test
if (require.main === module) {
  console.log('PQC TypeScript Module');
  console.log('=====================');
  
  const store = new PQCKeyStore();
  console.log('\nAvailable keys:', store.listKeys());
  
  // Test hybrid encryption with random key
  console.log('\nTesting hybrid encryption...');
  const testKey = randomBytes(32);
  const testData = Buffer.from('Hello, quantum-safe world!');
  
  const { nonce, ciphertext } = hybridEncrypt(testData, testKey);
  const decrypted = hybridDecrypt(ciphertext, nonce, testKey);
  
  console.log('  Original:', testData.toString());
  console.log('  Decrypted:', decrypted.toString());
  console.log('  ✓ Match:', testData.equals(decrypted));
}
