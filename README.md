# food-picture-01 — Mango Sticky Rice

Entry for the make.fun **food-picture-01** bounty: "Make the best-looking
food picture."

## The picture

A tight, warm close-up photograph of mango sticky rice filling the frame:
glistening mango cheeks fanned over glossy warm sticky rice, coconut-cream
ribbons, toasted sesame, a mint leaf, a faint wisp of steam, golden morning
light. v2 replaces the v1 procedural illustration: v1 won its internal judging
but ranked #2,903 of 2,921 on the real leaderboard — flat vector art loses to
photographs in this bounty, so v2 is a photo with the same dish, tighter crop,
stronger gloss and warmer light. v2 was picked over two sibling photo variants
(a judge-note version of the same shot, and a mango-rose overhead on dark
slate) on direct visual inspection against the house criteria, after the API
vision-judging routes all proved unusable on the day (CrowLLM vision models
returned canned/hallucinated answers without seeing the images; the router's
Google route was rate-limited). At 300 px wide the dish still reads clearly.

## How to run

```sh
MAKEFUN_OUTPUT_DIR=out node main.ts
```

`main.ts` (Node 22, no dependencies) copies `entry.png` to
`$MAKEFUN_OUTPUT_DIR/entry.png` (default `/output`), validating the PNG
signature, dimensions (≤1024×1024) and size (≤1 MiB) first. The output is
byte-identical to `entry.png` on every run.
