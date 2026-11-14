# food-picture-01 — Mango Sticky Rice

Entry for the make.fun **food-picture-01** bounty: "Make the best-looking
food picture."

## The picture

A bright, fresh mango sticky rice on a clean ceramic plate: glistening mango
cheeks fanned over warm sticky rice, coconut-cream drizzle, toasted sesame,
a mint leaf, soft morning light. Drawn procedurally with PIL (deterministic,
no network) — it won a 12-call pairwise vision judging against two other
concepts (sizzling butter-garlic shrimp: 4 wins; smash-burger cheese melt:
3 wins; mango sticky rice: **5 wins**).

## How to run

```sh
MAKEFUN_OUTPUT_DIR=out node main.ts
```

`main.ts` (Node 22, no dependencies) copies `entry.png` to
`$MAKEFUN_OUTPUT_DIR/entry.png` (default `/output`), validating the PNG
signature, dimensions (≤1024×1024) and size (≤1 MiB) first. The output is
byte-identical to `entry.png` on every run.
