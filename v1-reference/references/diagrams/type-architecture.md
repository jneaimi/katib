# Architecture

**Best for:** system overviews, data-flow diagrams, integration maps, infra topology.

## Layout conventions

- Group components by tier or trust boundary (frontend → backend → data; public → private).
- Primary flow runs left→right or top→down. Pick one and hold it.
- Draw arrows before boxes so z-order puts connections behind components.
- 1–2 accent (`colors.accent`) focal nodes: the primary integration point, the primary data store, or the key decision node.
- Dashed boundary rectangles mark regions (VPC, security group, trust zone). Labels sit on a `colors.page_bg` mask rect over the boundary line so the text doesn't collide with the dashed stroke.

## Node choice

Pick treatment from the node-type table in [style.md](style.md):

| Component | Treatment |
|---|---|
| The primary component the diagram is about | `focal` (1–2 max) |
| Most internal services | `backend` |
| Databases, caches, queues | `store` |
| Third-party APIs, external clouds | `external` |
| Users, ingress | `input` |
| Optional paths, async workers | `optional` (dashed) |

## Boundary rectangles

```html
<!-- Dashed trust zone -->
<rect x="X" y="Y" width="W" height="H" rx="8"
      fill="none" stroke="{{ colors.accent }}" stroke-width="1"
      stroke-dasharray="4,4" opacity="0.5"/>

<!-- Label mask -->
<rect x="X+16" y="Y-6" width="120" height="12" fill="{{ colors.page_bg }}"/>
<text x="X+24" y="Y+2" fill="{{ colors.accent }}" font-size="8"
      font-family="ui-monospace, monospace" letter-spacing="0.14em"
      opacity="0.8">TRUST ZONE</text>
```

## Bilingual

- Mirror for AR via the `direction` transform (see [rtl-notes.md](rtl-notes.md)) *only* if the architecture has a strong left→right story; most architecture diagrams read fine either direction.
- Put all Arabic labels in `.diagram-label` overlays. Keep service names (`postgres`, `redis`) in the SVG — they're identifiers, not translated content.

## Anti-patterns

- Every box in `accent` ("this is important too") — hierarchy collapses.
- Bidirectional arrow when one direction is obvious from context (e.g. `request → response` is implied by an HTTP arrow).
- Legend floating inside the diagram area.
- Diagram that spans two trust zones without a boundary rectangle.
- More than 9 nodes — split into overview + detail.

## Examples

- Tutorial domain: system architecture in a `tutorial` or `handoff` doc.
- Report domain: "as-is" state in an `audit-report`.
- Editorial domain: infrastructure section in a `white-paper` or `case-study`.
