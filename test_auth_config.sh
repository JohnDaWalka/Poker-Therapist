#!/bin/bash
# test_auth_config.sh
# Test script to verify authentication configuration

set -e

echo "=================================="
echo "Authentication Configuration Test"
echo "=================================="
echo ""

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Counters
errors=0
warnings=0
passed=0

# Check if .env.local exists
if [ -f ".env.local" ]; then
    echo "✅ .env.local file found"
    # Load variables safely without exposing to entire shell
    set -a
    source .env.local 2>/dev/null
    set +a
    passed=$((passed + 1))
else
    echo -e "${YELLOW}⚠️  .env.local file not found (optional for testing)${NC}"
    warnings=$((warnings + 1))
fi

echo ""
echo "Checking Authentication Environment Variables..."
echo "------------------------------------------------"

# Define categories of environment variables
AZURE_VARS=("AZURE_AD_TENANT_ID" "AZURE_AD_CLIENT_ID" "AZURE_AD_CLIENT_SECRET")
GOOGLE_VARS=("GOOGLE_CLIENT_ID" "GOOGLE_CLIENT_SECRET")
SECURITY_VARS=("SESSION_SECRET_KEY" "JWT_SECRET_KEY")
OPTIONAL_VARS=("APPLE_CLIENT_ID" "GITHUB_CLIENT_ID" "SSO_PROVIDER")

# Check Azure AD variables
echo ""
echo "Azure AD Configuration:"
for var in "${AZURE_VARS[@]}"; do
    if [ -n "${!var}" ]; then
        if [ "${!var}" = "your-actual-${var,,}" ] || [ "${!var}" = "your-${var,,}-here" ] || [[ "${!var}" == *"your-"* ]]; then
            echo -e "  ${YELLOW}⚠️  $var is set but contains placeholder value${NC}"
            warnings=$((warnings + 1))
        else
            echo -e "  ${GREEN}✅ $var is configured${NC}"
            passed=$((passed + 1))
        fi
    else
        echo -e "  ${RED}❌ $var is not set${NC}"
        errors=$((errors + 1))
    fi
done

# Check Google OAuth variables
echo ""
echo "Google OAuth Configuration:"
for var in "${GOOGLE_VARS[@]}"; do
    if [ -n "${!var}" ]; then
        if [[ "${!var}" == *"your-"* ]]; then
            echo -e "  ${YELLOW}⚠️  $var is set but contains placeholder value${NC}"
            warnings=$((warnings + 1))
        else
            echo -e "  ${GREEN}✅ $var is configured${NC}"
            passed=$((passed + 1))
        fi
    else
        echo -e "  ${RED}❌ $var is not set${NC}"
        errors=$((errors + 1))
    fi
done

# Check security variables
echo ""
echo "Security Configuration:"
for var in "${SECURITY_VARS[@]}"; do
    if [ -n "${!var}" ]; then
        # Check length
        length=${#!var}
        if [ $length -lt 32 ]; then
            echo -e "  ${RED}❌ $var is too short (${length} chars, minimum 32 required)${NC}"
            errors=$((errors + 1))
        elif [[ "${!var}" == *"generate-"* ]] || [[ "${!var}" == *"your-"* ]]; then
            echo -e "  ${YELLOW}⚠️  $var contains placeholder value${NC}"
            warnings=$((warnings + 1))
        else
            echo -e "  ${GREEN}✅ $var is properly configured (${length} chars)${NC}"
            passed=$((passed + 1))
        fi
    else
        echo -e "  ${RED}❌ $var is not set${NC}"
        errors=$((errors + 1))
    fi
done

# Check optional variables
echo ""
echo "Optional Identity Providers:"
for var in "${OPTIONAL_VARS[@]}"; do
    if [ -n "${!var}" ]; then
        if [[ "${!var}" == *"your-"* ]]; then
            echo -e "  ${YELLOW}⚠️  $var is set but contains placeholder value${NC}"
            warnings=$((warnings + 1))
        else
            echo -e "  ${GREEN}✅ $var is configured${NC}"
            passed=$((passed + 1))
        fi
    else
        echo "  ℹ️  $var is not set (optional)"
    fi
done

# Security checks
echo ""
echo "Security Checks:"
echo "----------------"

# Check if .env.local is in git (more portable method)
if git ls-files 2>/dev/null | grep -q "^\.env\.local$"; then
    echo -e "${RED}❌ CRITICAL: .env.local is committed to git! This is a security risk!${NC}"
    errors=$((errors + 1))
else
    echo -e "${GREEN}✅ .env.local is not in version control${NC}"
    passed=$((passed + 1))
fi

# Check for credential files
echo ""
echo "Checking for credential files in repository:"
credential_files=(
    "*.p8"
    "*.pem"
    "*-key.json"
    "service-account*.json"
    "credentials.json"
    "client_secret*.json"
)

found_creds=false
for pattern in "${credential_files[@]}"; do
    if git ls-files | grep -q "$pattern" 2>/dev/null; then
        echo -e "${RED}❌ SECURITY RISK: Found credential files matching pattern: $pattern${NC}"
        errors=$((errors + 1))
        found_creds=true
    fi
done

if [ "$found_creds" = false ]; then
    echo -e "${GREEN}✅ No credential files found in repository${NC}"
    passed=$((passed + 1))
fi

# Check .gitignore
echo ""
if grep -q ".env.local" .gitignore 2>/dev/null; then
    echo -e "${GREEN}✅ .gitignore properly configured for .env.local${NC}"
    passed=$((passed + 1))
else
    echo -e "${YELLOW}⚠️  .gitignore should include .env.local${NC}"
    warnings=$((warnings + 1))
fi

# Check HTTPS configuration (for production)
echo ""
if [ "$ENVIRONMENT" = "production" ]; then
    echo "Production Environment Checks:"
    if [[ "$AZURE_AD_REDIRECT_URI" == https://* ]] || [[ "$GOOGLE_REDIRECT_URI" == https://* ]]; then
        echo -e "${GREEN}✅ Using HTTPS for redirect URIs${NC}"
        passed=$((passed + 1))
    else
        echo -e "${RED}❌ Production must use HTTPS for redirect URIs${NC}"
        errors=$((errors + 1))
    fi
fi

# Summary
echo ""
echo "=================================="
echo "Test Summary"
echo "=================================="
echo -e "${GREEN}Passed:   $passed${NC}"
echo -e "${YELLOW}Warnings: $warnings${NC}"
echo -e "${RED}Errors:   $errors${NC}"
echo ""

if [ $errors -gt 0 ]; then
    echo -e "${RED}❌ Configuration has errors. Please fix them before deployment.${NC}"
    echo ""
    echo "See AUTHENTICATION_SETUP.md for detailed configuration instructions."
    exit 1
elif [ $warnings -gt 0 ]; then
    echo -e "${YELLOW}⚠️  Configuration has warnings. Review them before production deployment.${NC}"
    echo ""
    echo "See AUTHENTICATION_SETUP.md for detailed configuration instructions."
    exit 0
else
    echo -e "${GREEN}✅ All authentication configuration checks passed!${NC}"
    exit 0
fi
