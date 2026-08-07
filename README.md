# RorinLabs a Zenless Zone Zero Build Calculator

A tool for evaluating disks, W-Engines, and teams in ZZZ, built to help figure out in which situations one build option is actually better than another.

It started from my own Grace Howard runs, which I used to post on DA. Over time I felt I needed something more rigorous to compare options, so I ended up building this calculator, mostly on my own with occasional help from a friend of mine (thanks, Aris).

## Project Status

I'm stepping away from this project due to lack of time and motivation to keep maintaining it actively. I'm putting it up here so it stays free and available: anyone who wants to continue it, improve it, or fork it is more than welcome to do so with no restrictions from me.

Known pending items:
- Characters from version 3.0 onward are missing (Velina and Norma, and whoever comes after)
- ES/EN translations are nearly complete; a few loose strings may still be untranslated in some tabs
- The **DA Buffs**, **Recommendations**, **Upgrade Guide**, and **Global Leaderboards** tabs are at different stages of completion (details below)
- The `n` and `b` values used for substat quality were tuned through manual testing and may need further adjustment

If you feel like picking it back up, all the code is available to fork or send PRs against.

## Tabs

### DPS
Main tab. Shows the DPS agent's combat stats, including buffs from supports, their W-Engine, 4-piece sets (both DPS and support sets), DA/boss buffs and debuffs, cores, passives, and mindscapes.

It also lets you view enemy stats (elemental resistance debuffs, defense reduction, miasma, etc.), freely swap disks to compare damage, switch languages, and import agents via UID. It generates build cards as well, designed with help from my friend.

### Agents in Team
Support tab. Lets you configure which characters are on the team, adjust their mindscapes, W-Engines, 4-piece sets, and tweak the stats that affect their buffs. Relevant stats are automatically highlighted (for example, ATK for Astra Yao).

### DA Buffs
Lets you customize DA buffs by selecting which buffs and debuffs are included in the calculations, including mode-specific cards and boss effects.

### Compare Builds
My favorite tab. Lets you compare two agents or two builds by evaluating crit damage, anomaly damage, sheer damage, total damage (anomaly + crit), or substat quality. Comparing two builds gives you a 1-to-1 stat comparison plus a simulated damage test against a basic enemy.

### Recommendations
A mini guide per agent, including substat evaluation via a radar chart, reference W-Engine comparisons, and theoretical "perfect disk" recommendations for different quality levels (80%, 90%, 100%).

### Upgrade Guide
Shows a rating of your current agents and highlights which ones need improvement the most, along with brief suggestions.

### Global Leaderboards
Similar to Interknot. An attempt at a ranking system based on all UIDs stored in the cloud.

### Graphs
A simple tab where you can simulate different stat buffs and compare them (for example, ATK% vs AP for anomaly damage).

### Info
Information about me / the project.

## How does it calculate things?

### 1. Damage
This follows exactly the formulas from [this document](https://docs.google.com/document/d/e/2PACX-1vSB_gaua-DY-JlsGt1-CpI5Ik3jiCeSmBfQKQdpx1dX2o0ZH9DJ0hbeWdIK05uUc_eyu4yLfHSt2AaD/pub#h.4df9wm5xuc8x). Multiple tests were run to verify that damage scales proportionally to what the calculator shows, and results were consistent.

### 2. Substat and build quality
This part is more complex. The system evaluates disk rolls based on how good they are for a given character:

- **Ideal** rolls (amber) → `+n` points
- **Decent** rolls (cyan) → `+b` points
- Any other substat → 0 points

For disks IV, V, and VI, if they have recommended or at least useful main stats (ATK%, PEN ratio, HP for rupture, etc.), they add `+1.7` or `+1.5` to the total score.

**Final score tiers:**

| Score | Tier |
|---|---|
| 8.5 | GOD |
| 8 | PERFECT |
| 7 | SSS |
| 6 | SS |
| 5 | S |
| 4 | A |
| 3 | B |
| 2 | C |
| < 2 | MID |

The `n` and `b` values are not fixed: they depend on how many ideal and decent stats a given character has, defined in an internal dictionary. For example:

- **Soldier 0 Anby** (3 ideal stats: ATK%, Crit DMG, Crit Rate): `n = 1.0`, `b = 0.75`
- **Vivian** (heavily AP-dependent): `n = 1.20`, `b = 0.95`

This makes it easier to get a "good" disk for characters that rely more heavily on specific stats. These values are meant to be adjusted with further testing.

Weapons are also factored in, though through a generic calculation:

- Very good weapon → `+10%`
- Anything else → no bonus

Why only 10%? To avoid heavily penalizing players who don't have the signature weapon, though this criteria might change later.

## A Note on How This Was Built

Full honesty here: parts of the code were written with the help of AI, since I don't come from a programming background. On top of that, planning was pretty much nonexistent, I mostly built things as I went rather than designing the project upfront. That shows: the codebase is messy, the organization is inconsistent in places, and there are structural mistakes throughout that a more experienced or better-planned project wouldn't have.

I'm aware of that, and I'm not trying to hide it. I just hope that, given the context, it's something you can forgive, and if you're picking this project up, it's also fair warning about what you're getting into.

## Final notes

I'm not a trained programmer, so there are probably plenty of things done in a less than optimal way. Any feedback, suggestions, issues, or PRs are more than welcome.

## Links

- [RorinLabs](https://rorin.duckdns.org/)
