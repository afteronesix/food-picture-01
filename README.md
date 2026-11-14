# food-picture-01 — Tonkotsu Ramen, Noodle Pull

Entry for the make.fun **food-picture-01** bounty: "Make the best-looking
food picture."

## The picture

A steaming bowl of tonkotsu ramen, chopsticks lifting a tall tangle of glossy
noodles high above the bowl: a soft jammy egg, red chili-oil swirls, a sheet
of nori, sliced green onions, golden broth, wisps of steam, dark moody
background, warm side light.

v3 replaces the v2 tight mango sticky rice photo, which ranked #2,403 of
3,196 (3W-9L) — a competent but generic crop with no drama, no action, no
story, and a pale palette. The new hypothesis is a different dish with a
moment in it: the noodle pull, the steam, the color contrast of chili oil,
egg yolk and green onion against the dark bowl. It was picked over two
sibling candidates (an overhead Mediterranean feast flat-lay — gorgeous but
too busy to read at 300 px — and a chocolate lava cake with a handwritten
"Dear Judge" note, whose text is unreadable at thumbnail size) on direct
visual inspection against the house criteria, after the CrowLLM
vision-judging routes proved blind again (hallucinated dishes and
first-presented bias on every probe call). At 300 px wide the noodle pull,
bowl, egg and chili oil are still clearly readable.

## How to run

```sh
MAKEFUN_OUTPUT_DIR=out node main.ts
```

`main.ts` (Node 22, no dependencies) copies `entry.png` to
`$MAKEFUN_OUTPUT_DIR/entry.png` (default `/output`), validating the PNG
signature, IHDR dimensions (≤1024×1024), size (≤1 MiB) and the trailing IEND
chunk first, then verifying the written copy byte-for-byte. The output is
byte-identical to `entry.png` on every run.
