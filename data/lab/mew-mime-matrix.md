# Smart Mime Jr. Strategy & Tactical Optimization Report

**Date**: September 20, 2026  
**Format**: Standard 60 (Standard-Legal, No Pokémon-as-Energy)  
**Sample Size**: 16,000 Monte Carlo games (1000 games/cell)  
**Compute Time**: 8.4s  

---

## Overall Leaderboard

| Rank | Deck Variant | Overall WR | vs Dragapult (T60) | vs Hedrick Worlds | vs Clefable (C60) | vs Ogerpon (D60) |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: |
| **#1** | **V5-Mime2-I3: 2 Mime Jr. / 3 Igglybuff / 3 Budew** | **79.9%** | 76.5% | 74.2% | 71.1% | 97.8% |
| **#2** | **V5-Mime2-B2: 2 Mime Jr. / 2 Budew (Prize-Safe)** | **78.9%** | 74.3% | 72.8% | 71.6% | 96.8% |
| **#3** | **V5-Mime1: 1 Mime Jr. (Smart AI & Tutor)** | **77.3%** | 77.8% | 74.8% | 70.2% | 86.3% |
| **#4** | **V5-Mime0-Control: 0 Mime Jr. (No Mimed Games)** | **55.6%** | 77.3% | 73.1% | 69.3% | 2.7% |

---

## Key Tactical Findings & Analysis

### 1. The Power of Forced Opponent Choice ("选无可选")
- **Cornerstone Ogerpon ex (D60)**: Against Ogerpon ex, the opponent's entire active and bench pool has only **Demolish** (140 damage). The opponent is forced to pick Demolish. Mew ex copies Demolish for 0 energy and, because Demolish ignores all effects on the active Pokémon, it bypasses *Cornerstone Stance*! This transforms the deck's single worst matchup into a dominating win.
- **0 Mime Jr. Control Comparison**: When Mime Jr. is excluded (0 copies), win rate against D60 drops dramatically because *Bouncy Circle* deals 0 damage against Cornerstone Stance!

### 2. 1 Mime Jr. vs 2 Mime Jr. Ratio Analysis
- **Prize Safety**: In 10% of games, a 1-of Mime Jr. is prized, disabling *Mimed Games* until prizes are drawn. Running 2 copies virtually eliminates this failure mode (1% prize rate).
- **Opening Consistency**: 2 copies makes turn 1 benching significantly more reliable without compromising *Buddy-Buddy Poffin* synergy, as all babies remain 30 HP.

---