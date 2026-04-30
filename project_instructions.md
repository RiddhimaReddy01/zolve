# PROJECT_INSTRUCTIONS.md

## Zolve Gamified Financial Ecosystem (Z-Coins System)

---

## 0. Objective

Design and implement a **closed-loop behavioral finance system** that:

* Incentivizes financially responsible actions
* Drives daily engagement and retention
* Enables social reinforcement via clubs
* Captures high-resolution behavioral + financial data
* Monetizes via merchant partnerships, interchange amplification, and cross-sell timing

This is **not a rewards system**.
This is a **behavioral operating system layered on top of fintech infrastructure**.

---

## 1. System Architecture Overview

### Core Layers

| Layer              | Function                         |
| ------------------ | -------------------------------- |
| Incentive Layer    | Z-Coins economy                  |
| Commerce Layer     | Z-Kart marketplace               |
| Status Layer       | Tier systems (individual + club) |
| Social Layer       | Z-Clubs                          |
| Engagement Layer   | Gamification mechanics           |
| Intelligence Layer | Data flywheel                    |

Each layer must be independently functional but tightly integrated via shared state.

---

## 2. Z-Coins (Currency Engine)

### Design Constraints

* Non-withdrawable (closed-loop currency)
* Earned via **financially desirable actions**
* Inflation controlled via sinks (spend mechanisms)
* Weighted earning (behavior > ads)

### Earning Events (Priority Order)

| Category             | Event                     | Weight            |
| -------------------- | ------------------------- | ----------------- |
| Financial Discipline | On-time payment           | High              |
| Credit Improvement   | Score increase            | High              |
| Savings Behavior     | Milestone achieved        | High              |
| Banking Setup        | Direct deposit activation | Medium            |
| Education            | Module completion         | Medium            |
| Engagement           | Daily check-in            | Low               |
| Ads                  | Optional viewing          | Very Low (capped) |
| Growth               | Referrals                 | High              |
| Exploration          | Easter eggs               | Variable          |

### Spending Sinks

* Z-Kart discounts
* Club Deals
* Auctions
* Flash deals
* Spin wheel entries

**Constraint:**
Total coin emission must be balanced by sinks → prevent inflation collapse.

---

## 3. Z-Kart (Commerce Layer)

### Core Function

A **discount marketplace + intent capture engine**.

### Features

1. **Base Discount Layer**

   * Default: ~10% (existing infrastructure)

2. **Coin Boost Layer**

   * Additional 5–10% via Z-Coins
   * Dynamic pricing engine required

3. **Price Comparison Hook**

   * External benchmarking (e.g., Amazon parity)
   * Goal: force **habitual pre-purchase check**

4. **Brand Promotions**

   * Sponsored placements
   * Native integration (not banner ads)

5. **Club Deals**

   * Group-only pricing
   * Unlock condition: minimum participants

### Key Metric

* **Pre-purchase interception rate**

---

## 4. Tier System (Status Layer)

### Individual Tier Logic

Inputs:

* Credit score
* Coin balance / velocity
* Completed behaviors

| Tier   | Capabilities                      |
| ------ | --------------------------------- |
| Basic  | Entry features                    |
| Silver | Multipliers, flash deals          |
| Gold   | Auctions, ad-free, premium access |

### Club Tier Logic

Inputs:

* Member tier homogeneity
* Collective actions
* Referrals

| Tier   | Unlock                 |
| ------ | ---------------------- |
| Bronze | Default                |
| Silver | Coordination achieved  |
| Gold   | High-performance group |

### Design Principle

Status must be:

* Visible
* Earned
* Difficult to fake

---

## 5. Z-Clubs (Social Layer)

### Structure

* Size: 2–6 members
* Shared coin pool (optional)
* Persistent identity

### Mechanics

1. **Group Purchases**

   * Initiated by one member
   * Time-constrained participation

2. **Referral Injection**

   * New users enter via clubs
   * Rewards distributed to all members

3. **Club Quests**

   * Coordinated actions required

4. **Leaderboard**

   * Competitive ranking

### Behavioral Mechanism

Peer pressure → compliance with financial discipline.

---

## 6. Gamification Layer

### 6.1 Scratch Cards

Trigger:

* Transactions > $20

Reward Distribution:

* Skewed probability
* High “try again” rate (~40%)

Goal:

* Reinforce post-transaction app opens

---

### 6.2 Spin Wheel

Earning:

* Action-based (not time-based)

Rewards:

* Coins
* Multipliers
* Vouchers
* Access unlocks

Goal:

* Reinforce **cause → reward loop**

---

### 6.3 Flash Deals

Characteristics:

* Time-limited
* Quantity-limited
* Tier-gated access

Variants:

* Fixed price
* Auction-based

Goal:

* Induce urgency + repeat checking

---

### 6.4 Easter Eggs

Hidden triggers:

* Time-based (midnight usage)
* Consistency-based (payment streaks)
* Identity-based (university referrals)

Goal:

* Organic virality
* Power user identification

---

### 6.5 Ads

Constraints:

* User-initiated only
* Strict caps (3/day, 50 coins max)
* Lower reward vs real behavior

Goal:

* Supplemental monetization without degrading experience

---

## 7. Data Flywheel (Intelligence Layer)

### Data Sources

| Mechanic      | Signal               |
| ------------- | -------------------- |
| Scratch cards | Session timing       |
| Spins         | Retention            |
| Z-Kart        | Purchase intent      |
| Price compare | Pre-buy intent       |
| Ads           | Content preference   |
| Clubs         | Social graph         |
| Club deals    | Group intent         |
| Referrals     | Influence network    |
| Easter eggs   | Power users          |
| Tiers         | Financial trajectory |

### Output Model

Unified user profile:

```
User Profile =
{
  financial_behavior,
  purchase_intent,
  social_graph,
  engagement_pattern,
  lifecycle_stage
}
```

### Use Cases

* Loan timing optimization
* Insurance cross-sell
* Telecom/SIM targeting
* Credit limit adjustments

---

## 8. Core System Requirements

### Functional Requirements

* Event-driven coin engine
* Real-time tier recalculation
* Dynamic pricing for Z-Kart
* Club state synchronization
* Reward probability engine
* Behavioral logging pipeline

### Non-Functional Requirements

| Category    | Requirement                          |
| ----------- | ------------------------------------ |
| Latency     | <200ms for reward feedback           |
| Scalability | Handle high-frequency events         |
| Consistency | Strong consistency for coin balances |
| Security    | Financial-grade compliance           |
| Fairness    | Anti-gaming mechanisms               |

---

## 9. Anti-Abuse Design

* Detect artificial engagement loops
* Cap low-value earning sources
* Monitor abnormal referral graphs
* Prevent coordinated fraud in clubs

---

## 10. Success Metrics

### Engagement

* DAU / MAU
* Session frequency
* Retention (D1, D7, D30)

### Financial Behavior

* On-time payment rate
* Credit score improvement rate
* Savings adoption

### Monetization

* Merchant revenue
* Interchange uplift
* Cross-sell conversion

### Network Effects

* Club formation rate
* Referral conversion rate

---

## 11. Implementation Phases

### Phase 1 — Core System

* Z-Coins engine
* Basic tiering
* Scratch cards

### Phase 2 — Commerce

* Z-Kart integration
* Price comparison
* Sponsored deals

### Phase 3 — Social Layer

* Z-Clubs
* Club deals
* Leaderboards

### Phase 4 — Advanced Gamification

* Auctions
* Easter eggs
* Advanced rewards

### Phase 5 — Data Intelligence

* Behavioral modeling
* Cross-sell engine
* Personalization

---

## 12. Strategic Positioning

This system functions as:

* A **behavioral reinforcement engine**
* A **high-frequency engagement loop**
* A **data acquisition layer**
* A **distribution channel for financial products**

Primary leverage comes from:

> Converting low-frequency financial interactions into high-frequency behavioral signals.

---

## 13. Critical Risks

* Over-gamification → loss of trust
* Coin inflation → reduced perceived value
* Regulatory scrutiny (financial incentives)
* User fatigue if rewards feel artificial

---

## 14. Design Principle Summary

1. Reward behavior, not activity
2. Maintain scarcity in rewards
3. Use social pressure, not just incentives
4. Capture intent before transaction
5. Optimize for long-term retention, not short-term engagement

---

## 15. Final Note

The system’s defensibility is not in features.

It is in:

* Behavioral lock-in
* Data compounding
* Social graph formation

Execution quality will determine whether this becomes:

* A gimmick
  or
* A durable financial ecosystem
