# Tree / Hierarchy

**Best for:** org charts, dependency trees, taxonomy, file trees, decision breakdowns, skill trees.

## Layout conventions

- Root at top, children fan out below (or root at left, children right).
- Nodes are small labeled rectangles (`rx=6`), 12–14px body-sans name + optional monospace 9px sublabel. Width 120–180px, height 40–52px.
- **Connectors are orthogonal (elbow-style), never diagonal.** Parent drops a short vertical line, then a horizontal bus connects siblings, then each child has a short vertical drop into its top edge. 1px `colors.text_secondary` stroke.
- Leaf indicator: thinner stroke (0.8) or different fill — OR let terminal position do the work.
- **Max depth: 4** (root + 3 tiers). **Max breadth per level: 5.**
- `colors.accent` on **one** node: root OR critical leaf. Not both.
- Draw connectors before nodes so z-order puts lines behind boxes.

## Node primitive

```html
<!-- Standard tree node -->
<rect x="X" y="Y" width="160" height="44" rx="6"
      fill="{{ colors.page_bg }}"
      stroke="{{ colors.text }}" stroke-width="1"/>
<text x="X+80" y="Y+28" fill="{{ colors.text }}" font-size="12" font-weight="600"
      text-anchor="middle" font-family="inherit">Parent</text>
```

## Orthogonal connector

```html
<!-- Vertical drop from parent bottom -->
<line x1="PX" y1="PY+44" x2="PX" y2="PY+68"
      stroke="{{ colors.text_secondary }}" stroke-width="1"/>

<!-- Horizontal sibling bus -->
<line x1="CX1" y1="BUS_Y" x2="CX3" y2="BUS_Y"
      stroke="{{ colors.text_secondary }}" stroke-width="1"/>

<!-- Vertical drops into each child -->
<line x1="CX1" y1="BUS_Y" x2="CX1" y2="CY"
      stroke="{{ colors.text_secondary }}" stroke-width="1"/>
<line x1="CX2" y1="BUS_Y" x2="CX2" y2="CY"
      stroke="{{ colors.text_secondary }}" stroke-width="1"/>
<line x1="CX3" y1="BUS_Y" x2="CX3" y2="CY"
      stroke="{{ colors.text_secondary }}" stroke-width="1"/>
```

## Focal leaf (accent)

```html
<rect x="X" y="Y" width="160" height="44" rx="6"
      fill="{{ colors.accent }}" fill-opacity="0.08"
      stroke="{{ colors.accent }}" stroke-width="1"/>
<text x="X+80" y="Y+28" fill="{{ colors.accent }}" font-size="12" font-weight="700"
      text-anchor="middle" font-family="inherit">Critical path</text>
```

## Bilingual

- Node labels translate — overlay via `.diagram-label`.
- Tree geometry is hierarchical, not directional — don't mirror for AR.
- Role-name trees (org charts) in AR: same layout, names in `.diagram-label`.

## Anti-patterns

- Tree 5+ levels deep on a single page (illegible — split into subtrees).
- Nodes of wildly varying widths — pick 2 widths max and stick to them.
- Diagonal connector lines.
- Skipped levels (parent connected to grandchild with no middle node).
- `colors.accent` on root AND a leaf — pick one.
- Breadth > 5 at any level — group into sub-categories.
