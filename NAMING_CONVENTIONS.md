# Naming Conventions and Project Structure

This document clarifies the naming conventions used in the Poker Therapist project to avoid confusion.

## Project Names

### Main Application: "Poker-Therapist"
- **Purpose**: AI-powered poker coaching with therapy and wellness focus
- **Vercel Project**: `poker-therapist`
- **Vercel URL**: `https://poker-therapist.vercel.app`
- **Root Directory**: `/` (repository root)
- **Focus**: Mental game coaching, therapy, AI-powered advice

### Poker-Coach-Grind API (Vercel: "Poker-Coaches")
- **Purpose**: Bankroll tracking, hand history, and performance analytics
- **Vercel Project**: `poker-coaches`
- **Vercel URL**: `https://poker-coaches.vercel.app`
- **Root Directory**: `Poker-Coach-Grind/`
- **Focus**: Financial tracking, hand analysis, crypto integration

## Why "Poker-Coach-Grind"?

The folder name "Poker-Coach-Grind" uses poker terminology:

- **"Grind"** in poker refers to the consistent, systematic process of playing many hands to build a bankroll over time
- This module handles the practical, numbers-focused aspects of poker: bankroll management, hand tracking, session analysis
- It's distinct from the therapy/wellness focus of the main application

## Vercel Deployment Structure

The repository deploys to **two separate Vercel projects**:

| Vercel Project | Folder | URL | Purpose |
|---|---|---|---|
| poker-therapist | `/` (root) | poker-therapist.vercel.app | Main coaching app |
| poker-coaches | `Poker-Coach-Grind/` | poker-coaches.vercel.app | Grind/analytics API |

## Common Questions

**Q: Why not just call it "Poker-Coaches"?**
A: The Vercel project is called "poker-coaches", but the folder is "Poker-Coach-Grind" to clearly indicate it handles the "grind" aspect (analytics, tracking) rather than general coaching.

**Q: Should I use "Poker-Coaches" or "poker-coaches"?**
A: 
- Vercel project name: `poker-coaches` (lowercase, hyphenated)
- Vercel URL: `poker-coaches.vercel.app` (lowercase, hyphenated)
- Folder name: `Poker-Coach-Grind` (Title Case)

**Q: What about "Versace"?**
A: There is no "Versace" in this project. If you see this name, it's likely a typo that should be "Vercel" (the hosting platform).

## Summary

- ✅ **poker-therapist.vercel.app** - Main therapy and coaching app
- ✅ **poker-coaches.vercel.app** - Grind/analytics API (lives in `Poker-Coach-Grind/` folder)
- ✅ Two independent Vercel projects from the same repository
- ✅ No "Versace" - only "Vercel" (the hosting service)
