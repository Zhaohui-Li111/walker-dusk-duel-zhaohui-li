# CONCEPT — walker-dusk-duel

> Version 1 · 2026-10-05 · written before any generation.
> Drafted by Claude Code from choices Zhaohui Li made in chat (fighting game, cartoon not realistic,
> two martial artists, accepted the proposed characters/proportions/arena). Zhaohui reviews and owns
> every decision below; later revisions are appended, not rewritten.

## The game in two sentences

You are **Akaken**, a stocky red-gi brawler with oversized fists, fighting a one-on-one duel at dusk
in a stone temple courtyard. Read your opponent **Aotake**, a tall straw-hatted kicker, and choose
each moment whether to close in and strike, block, or back off until one fighter is knocked out.

## Core loop

- **Repeat:** step in → choose punch / kick / block / back off → see and hear the result → reset spacing.
- **Decide each time:** is the opponent in range, and are they about to attack or about to block?
- **Risk:** a whiffed strike leaves you open for a moment; a mistimed block wastes your turn to hit.
  Health is the only resource; the round ends at 0.

## Design pillars

| Pillar | Meaning | Visual choice that honors it | Sound choice that honors it |
|---|---|---|---|
| **Every hit is felt** | Contact must be unmistakable | Distinct hurt pose leaning *away* from the attacker; white hit spark at the contact point | Short, dry, bass-heavy impact with no reverb tail (SFX-HIT) |
| **Read the opponent** | You win by reading the other fighter, not by mashing | Two silhouettes that cannot be confused: topknot + headband vs. wide straw hat + braid; warm vs. cool body color | Whiff (SFX-WHIFF) and block (SFX-BLOCK) sound clearly different from a hit, so the ear confirms what the eye saw |
| **Dusk ritual** | A quiet, ceremonial duel, not a gore show | Low-contrast dusk-purple stone and warm lanterns behind bright fighters; no blood | Sparse taiko-and-wood-flute loop; music stops completely at KO so the silence marks the ending |
| **One more round** | Losing should make you want to retry right away | Rematch prompt appears at once; fighters snap back to their idle stances | Music restarts from the top on rematch |

## Art direction

**Flat cel-shaded cartoon, about 5 heads tall, thick dark outline, 3–5 flat colors per fighter.**
Big heads and big fists make poses readable when a fighter is only ~112 px tall in a 640×360 view,
which serves *Read the opponent*. Flat color with no texture keeps generated poses consistent with
each other, and the bright fighters over a darker courtyard serve *Dusk ritual*.

Reference notes (words only, no artist names):
- Materials: cotton gi with clean folds, woven straw, worn grey temple stone, paper lanterns.
- Lighting: late dusk; ambient purple sky, warm orange lantern pools; fighters lit flat and evenly.
- Era / mood: timeless East-Asian temple courtyard, ceremonial and calm before violence.

## Audio direction

- The player should feel **calm focus that tightens**: a steady low taiko pulse and an airy flute.
- Impacts are short and dry so they cut through the music.
- **Pause:** music ducks to about -12 dB with a low-pass filter (a muffled "held breath").
- **KO:** music stops at once; only the KO sound plays, then silence.
- **Rematch:** music restarts from the beginning of the loop.
- **Muted:** every event also has a visible signal (pose change, spark, block flash, health bar,
  KO text), so the game is playable silent.
