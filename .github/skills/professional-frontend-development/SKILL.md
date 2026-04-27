---
name: professional-frontend-development
description: Build and design professional, high-quality frontend UIs with a focus on information density and speed.
---

# Professional Frontend Development

> **Purpose:** Build and design professional, high-quality frontend UIs from scratch — dashboards, admin panels, SaaS tools, internal tools, or any web app.
> **Audience:** Any team building a production-grade frontend.
> **Trigger:** Use when building new UI from scratch, refactoring an existing UI, or designing/implementing components for any professional web project.

---

## 1. Design Philosophy

- **Tool-grade, not template-grade.** Prioritize information density, scannability, and speed over decoration. The UI should feel like it was built by senior engineers for power users.
- **Reject generic AI aesthetics.** No pastel gradients, no over-rounded everything, no excessive whitespace, no bubbly/friendly feel. Reference points: Stripe Dashboard, Linear, Vercel Console, Raycast.
- **White canvas, color through intent.** Default background is white. Color is used sparingly and purposefully — to indicate actions, status, hierarchy, or emphasis. Never decorative.
- **Quiet confidence.** Every pixel should justify its existence. Clean, intentional, fast.

---

## 2. Color System

Adapt tokens to your brand. The structure below is the required architecture — replace hex values with your brand colors.

### 2.1 Core Palette

| Token | Role | Notes |
|-------|------|-------|
| `--color-primary` | Primary actions, active states, key CTAs | Your brand's dominant action color |
| `--color-primary-hover` | Primary button hover | ~10% darker than primary |
| `--color-primary-light` | Primary tinted backgrounds (selected rows, active badges) | ~95% lightness tint |
| `--color-primary-subtle` | Soft highlights, tag backgrounds | Between light and surface |
| `--color-secondary` | Secondary actions, nav background, section headers | Contrasting brand color |
| `--color-secondary-hover` | Secondary hover | ~10% darker than secondary |
| `--color-secondary-light` | Secondary tinted backgrounds | ~95% lightness tint |
| `--color-accent` | Links, info indicators, tertiary actions | Distinct from primary/secondary |
| `--color-accent-light` | Accent tinted backgrounds | ~95% lightness tint |

**Default neutral-base starter (override with your brand):**
```css
:root {
  --color-primary:        #2563EB; /* blue-600 */
  --color-primary-hover:  #1D4ED8; /* blue-700 */
  --color-primary-light:  #EFF6FF; /* blue-50 */
  --color-primary-subtle: #DBEAFE; /* blue-100 */

  --color-secondary:      #1E1B4B; /* indigo-950 */
  --color-secondary-hover:#312E81; /* indigo-900 */
  --color-secondary-light:#EEF2FF; /* indigo-50 */

  --color-accent:         #7C3AED; /* violet-600 */
  --color-accent-light:   #F5F3FF; /* violet-50 */
}
```

### 2.2 Neutral Palette

Do not change these — they are intentionally brand-agnostic.

| Token | Hex | Usage |
|-------|-----|-------|
| `--color-neutral-950` | `#0A0A0A` | Primary text, headings |
| `--color-neutral-800` | `#262626` | Body text |
| `--color-neutral-600` | `#525252` | Secondary text, labels, placeholders |
| `--color-neutral-400` | `#A3A3A3` | Disabled text, muted icons |
| `--color-neutral-200` | `#E5E5E5` | Borders, dividers |
| `--color-neutral-100` | `#F5F5F5` | Table headers, subtle fills |
| `--color-neutral-50`  | `#FAFAFA` | Page background alt, card hover |
| `--color-white`       | `#FFFFFF` | Card backgrounds, page background |

### 2.3 Semantic Colors

| Token | Hex | Usage |
|-------|-----|-------|
| `--color-success`       | `#15803D` | Active, published, positive |
| `--color-success-light` | `#F0FDF4` | Success banners, status badges |
| `--color-warning`       | `#C2410C` | Pending, draft, attention |
| `--color-warning-light` | `#FFF7ED` | Warning banners |
| `--color-error`         | `#DC2626` | Destructive actions, errors |
| `--color-error-light`   | `#FEF2F2` | Error backgrounds |
| `--color-info`          | `#0369A1` | Info states (alias accent if preferred) |
| `--color-info-light`    | `#F0F9FF` | Info backgrounds |

---

## 3. Typography

### 3.1 Font Stack

```css
:root {
  --font-headline: 'Inter', system-ui, -apple-system, sans-serif;
  --font-body:     'Inter', system-ui, -apple-system, sans-serif;
  --font-mono:     'JetBrains Mono', 'SF Mono', 'Fira Code', monospace;
}
```

Prefer **Inter** for body/UI text. Swap `--font-headline` to **Manrope**, **Plus Jakarta Sans**, or **DM Sans** for a distinct heading feel if desired.

### 3.2 Type Scale

| Token | Size | Weight | Font | Usage |
|-------|------|--------|------|-------|
| `--text-page-title`    | 24px / 1.2 | 700 | Headline | Page titles |
| `--text-section-title` | 18px / 1.3 | 600 | Headline | Section headings, card group headers |
| `--text-card-title`    | 15px / 1.4 | 600 | Body | Card titles, modal titles |
| `--text-body`          | 14px / 1.5 | 400 | Body | Default body text |
| `--text-body-medium`   | 14px / 1.5 | 500 | Body | Emphasized body (table cells, values) |
| `--text-label`         | 12px / 1.4 | 600 | Body | Form labels, column headers (uppercase, +0.5px tracking) |
| `--text-caption`       | 12px / 1.4 | 400 | Body | Helper text, descriptions, timestamps |
| `--text-mono`          | 13px / 1.5 | 400 | Mono | Code, IDs, technical values |

### 3.3 Rules

- **NEVER** use all-uppercase for anything except `--text-label` (column headers, form labels).
- Headings: `--color-neutral-950`. Body text: `--color-neutral-800`. Captions: `--color-neutral-600`.
- No text shadow. No text gradients. No decorative font weight mixing.

---

## 4. Spacing & Layout

### 4.1 Base Unit

```css
--space-unit: 4px;
```

Scale: `4, 8, 12, 16, 20, 24, 32, 40, 48, 64`

### 4.2 Layout Grid

```css
--content-max-width: 1440px; /* or 100% for data-dense apps */
--grid-columns:      12;
--grid-gutter:       24px;
--page-padding-x:    32px;
--page-padding-y:    24px;
```

Use `100%` max-width for data-dense tools (tables, grids). Use `1440px` or `1280px` for content-focused pages. Never center-crop when the user needs table real-estate.

### 4.3 Page Structure

```
┌─────────────────────────────────────────────────────────────────┐
│  Nav Bar (--color-secondary bg, 56px height, sticky)            │
├─────────────────────────────────────────────────────────────────┤
│  Page Header (white bg, border-bottom)                          │
│  Title + Subtitle (left) | Page-level Actions (right)           │
├─────────────────────────────────────────────────────────────────┤
│  Content Area (white bg, full-width, padded with page-padding)  │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │  Section / Panel                                        │    │
│  └─────────────────────────────────────────────────────────┘    │
│  24px gap                                                       │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │  Section / Panel                                        │    │
│  └─────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────┘
```

**CRITICAL:** No gradient hero banners. Page header = left-aligned title + optional subtitle, right-aligned page-level actions. One line. `border-bottom: 1px solid var(--color-neutral-200)`.

---

## 5. Components

### 5.1 Navigation Bar

```
Background:   var(--color-secondary)
Height:       56px
Text:         white, 14px, 500 weight
Active item:  white text + 2px bottom border in var(--color-primary)
Hover:        rgba(255,255,255,0.1) background
Dropdown:     white bg, shadow-lg, 4px radius, 200px min-width
User pill:    top-right — user name in white, optional avatar/initials
```

- Logo / product name: left-aligned.
- Nav items: left-aligned after logo (or center for marketing sites).
- User info + logout: right-aligned via `margin-left: auto`. Do NOT use `justify-content: space-between` with three flex children.
- Include a descriptive `aria-label` on icon-only nav elements.
- Always include a skip-to-content link for keyboard accessibility.

### 5.2 Buttons

Four tiers. All buttons: `14px`, `500 weight`, `height: 36px`, `padding: 0 16px`, `border-radius: 4px`, `cursor: pointer`. Transition: `150ms ease` on background and border.

| Variant | Default | Hover | Disabled |
|---------|---------|-------|----------|
| **Primary** | bg: `--color-primary`, text: white | bg: `--color-primary-hover` | bg: `--color-neutral-200`, text: `--color-neutral-400` |
| **Secondary** | bg: transparent, text: `--color-secondary`, border: 1px `--color-secondary` | bg: `--color-secondary-light` | border: `--color-neutral-200`, text: `--color-neutral-400` |
| **Ghost** | bg: transparent, text: `--color-neutral-800`, no border | bg: `--color-neutral-100` | text: `--color-neutral-400` |
| **Destructive** | bg: `--color-error`, text: white | bg: darkened error | bg: `--color-neutral-200`, text: `--color-neutral-400` |

**Size variants:**
- `sm`: height 28px, padding 0 10px, font 12px
- `md`: height 36px (default)
- `lg`: height 40px, padding 0 20px

**Icon buttons:** Square, same heights, padding 0, equal width/height. Icon 16px (sm), 18px (md), 20px (lg).

**Rules:**
- One primary button per visible context.
- Destructive buttons require a confirmation step (modal or inline confirm).
- "+ Add Item" → Ghost button with `+` icon prefix.
- Remove/delete inside cards → Ghost + red text, not a full destructive button.

### 5.3 Form Elements

#### Text Input
```css
height:        36px;
padding:       0 12px;
border:        1px solid var(--color-neutral-200);
border-radius: 4px;
font-size:     14px;
background:    white;
/* focus */
border-color:  var(--color-accent);
box-shadow:    0 0 0 2px var(--color-accent-light);
/* error */
border-color:  var(--color-error);
box-shadow:    0 0 0 2px var(--color-error-light);
```

#### Textarea
Same as text input. `resize: vertical`. Min-height: 80px.

#### Select / Dropdown
Same dimensions as text input. Custom chevron icon (not native `<select>`). Dropdown panel: white bg, `shadow-lg`, max-height 280px with overflow scroll, 4px radius. Options: 36px height, hover `--color-neutral-50`.

#### Checkbox
```
Size:          16px × 16px
Border:        1.5px solid var(--color-neutral-400)
Checked:       bg var(--color-primary), white checkmark SVG
Border-radius: 3px
```

#### Radio Button
Same sizing as checkbox. Circular. Checked state: inner filled circle in `--color-primary`.

#### Toggle Switch
Use only when the setting has an immediate effect (not inside a form that requires Save). `width: 36px, height: 20px`. Active: `--color-primary`. Inactive: `--color-neutral-300`.

#### File Upload Zone
```
Border:        1px dashed var(--color-neutral-300)
Border-radius: 4px
Padding:       32px
Background:    var(--color-neutral-50)
Text:          "Drop file here or click to browse" in --color-neutral-600
Hover:         border-color var(--color-accent), background var(--color-accent-light)
Icon:          upload SVG icon, 24px, --color-neutral-400
```

#### Form Layout
- Label above input, 4px gap.
- Labels use `--text-label` (12px, 600, uppercase).
- Helper text below input, 4px gap, `--text-caption` in `--color-neutral-600`.
- Error text below input, 4px gap, `--text-caption` in `--color-error`.
- Adjacent fields in rows: CSS grid with `gap: 16px`.
- Related cascading selects (e.g., Country → State → City): single row, equal width, 12px gap.

### 5.4 Cards

#### Display Card (read-only item)
```
Border:        1px solid var(--color-neutral-200)
Border-radius: 4px
Background:    white
Padding:       16px
Hover:         box-shadow 0 1px 3px rgba(0,0,0,0.08)

Structure:
  Optional image/icon header
  Title      — --text-body-medium
  Subtitle   — --text-caption, --color-neutral-600
  Meta/stats — --text-caption or key-value pairs
  Footer (optional): action buttons, right-aligned
```

#### Editable Card (form-in-a-card)
```
Border:        1px solid var(--color-neutral-200)
Border-radius: 4px
Padding:       16px
Background:    white

Header row: item name + identifier on same line
Divider: 1px --color-neutral-200
Form fields stacked with 12px gap
Footer: primary "Save" / "Update" button (sm, right-aligned)
```

#### Container / Group Card (wraps a list of items)
```
Border:        1px solid var(--color-neutral-200)
Border-radius: 4px
Background:    var(--color-neutral-50)
Padding:       16px

Header row: group title input (editable) | "Remove" (ghost + red text)
Content: nested cards or list of items
Footer: "+ Add Item" ghost button
```

**Card grid:**
```css
grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
gap: 16px;
```
Max 4 cards per row on desktop.

### 5.5 Data Tables

```
Width:          100%
Border-collapse: separate
Border-spacing: 0
Border:         1px solid var(--color-neutral-200)
Border-radius:  4px
Overflow:       hidden

Header Row:
  Background:   var(--color-neutral-100)
  Text:         --text-label (12px, 600, uppercase)
  Height:       40px
  Padding:      0 16px
  Border-bottom: 1px solid var(--color-neutral-200)

Body Row:
  Height:       48px (adjust to 40px for compact tables)
  Padding:      0 16px
  Border-bottom: 1px solid var(--color-neutral-200)
  Hover:        background var(--color-neutral-50)

Last row: no border-bottom.
Actions column: right-aligned, icon buttons, 8px gap.
```

**Complex values in table cells:**
- NEVER display raw JSON or long strings unstyled.
- Render as key-value chips: `key: value` in small pill badges (`--text-caption`, `--color-neutral-100` bg, `4px radius`).
- Too many values: show first 2 + "+N more" chip that expands on click.
- Code/IDs: use `--font-mono` at `--text-mono` size.

#### Table Toolbar (above table)
```
Left:  filter dropdowns / selects, 8px gap
Right: search input with icon
```

#### Pagination
```
Height:      48px
Alignment:   center
Pages:       32×32px squares
Active:      bg var(--color-primary), text white, 4px radius
Inactive:    text --color-neutral-600, hover bg --color-neutral-100
Prev/Next:   ghost buttons with arrow SVG icons
Info text:   "Showing 1–20 of 180 records" left-aligned, --text-caption
```

### 5.6 Modals / Dialogs

```
Overlay:     rgba(10, 10, 10, 0.5)
Container:
  Background:    white
  Border-radius: 8px
  Box-shadow:    0 20px 60px rgba(0,0,0,0.15)
  Width:         480px (sm) | 640px (md) | 800px (lg)
  Max-height:    85vh
  Overflow-y:    auto

Header: 20px padding, title (--text-section-title), close button (ghost icon, top-right)
Body:   20px padding, 0 top padding
Footer: 20px padding, border-top 1px --color-neutral-200, buttons right-aligned, 8px gap
```

**Rules:**
- Destructive confirmations: title describes what happens ("Delete entry?"), body explains consequences. Buttons: "Cancel" (ghost) + "Delete" (destructive).
- Form modals: primary button text matches the action ("Save", "Create", "Update") — never generic "Submit".
- Never stack more than 2 modals.

### 5.7 Badges & Status Indicators

| Status | Background | Text | Border |
|--------|-----------|------|--------|
| Active / Success | `--color-success-light` | `--color-success` | none |
| Pending / Warning | `--color-warning-light` | `--color-warning` | none |
| Error / Failed | `--color-error-light` | `--color-error` | none |
| Info / Default | `--color-info-light` | `--color-info` | none |
| Neutral | `--color-neutral-100` | `--color-neutral-600` | none |

```css
padding:      2px 8px;
border-radius: 4px;
font:         --text-caption, 500 weight;
display:      inline-flex;
align-items:  center;
gap:          4px;
```

### 5.8 Empty States

```
Container:   centered, max-width 360px, padding 48px
Icon:        48px SVG, --color-neutral-300
Title:       --text-card-title, --color-neutral-800
Description: --text-body, --color-neutral-600, centered
Action:      primary button (optional, contextual)
```

Never leave a blank area. Every empty list, table, or grid needs: icon + descriptive message + optional action.

### 5.9 Loading States

- **Tables:** Skeleton rows (5 rows, pulsing `--color-neutral-100` → `--color-neutral-50` animation).
- **Cards:** Skeleton card placeholders with pulsing fills.
- **Buttons:** Inline spinner + disabled state while the action is in progress. Restore on completion. Never use spinners outside the triggering element.
- **Page-level:** Semi-transparent overlay with centered spinner for full-page async actions (save, delete, publish). Show before fetch, hide in `finally`.
- **Rule:** Every button triggering an async request MUST show a loading state. No silent waits.

### 5.10 Toast / Notification

```
Position:     top-right, 24px from edges
Min-width:    300px, max-width: 440px
Border-radius: 8px
Shadow:       0 8px 24px rgba(0,0,0,0.12)
Padding:      14px 20px
Background:   solid semantic color (success/error/info/warning)
Text:         white
Auto-dismiss: 5s (success/info), 8s (errors)
Animation:    slide-in from right, spring easing
```

### 5.11 Confirm Dialog

```
Overlay:  rgba(10, 10, 10, 0.45), fade-in 150ms
Dialog:   white bg, 8px radius, 400px width, centered
  Icon:   40px SVG — warning icon for destructive, info icon for neutral
  Title:  --font-headline, 18px, 600
  Body:   14px, --color-neutral-600
  Footer: Cancel (secondary) + Confirm (primary or destructive)
Animation: slide-up 200ms spring
```

### 5.12 UI Utilities Pattern

For any non-trivial app, implement a global UI utility (e.g., `AppUI` or a framework equivalent) and ensure all pages use it:

| Method | Purpose |
|--------|---------|
| `toast(message, type)` | Show toast. Types: `success`, `error`, `warning`, `info` |
| `confirm(title, msg, opts)` | Async confirm dialog. Returns `Promise<boolean>`. `opts.destructive`, `opts.okLabel` |
| `loader.show()` / `loader.hide()` | Page-level loading overlay |
| `btnLoader(btn, loading, text)` | Button spinner + disable/re-enable |

**Rules:**
- NEVER use native `alert()`, `confirm()`, or `prompt()`. Use the utility.
- ALWAYS show a loader during any async operation.
- ALWAYS handle errors and show a toast — never fail silently.

---

## 6. Interaction Patterns

### 6.1 Cascading Dropdowns
Disable downstream selects until the parent is selected. Show placeholder "Select [Field]" in the disabled state. When parent changes, clear all downstream selections. Show an inline loading indicator while fetching dependent options.

### 6.2 Inline Editing
For fields that change frequently (toggles, checkboxes), save on change with a 300–500ms debounce. Show a brief visual confirmation ("Saved ✓") that fades after 1.5s. Do not require a separate "Save" click for single-toggle fields.

### 6.3 Destructive Actions
Always require confirmation. Use inline confirmation (popover/inline expand) for low-risk deletions. Use a modal confirmation for high-risk deletions (deleting records, irreversible actions).

### 6.4 Bulk Operations
Tables/lists with checkboxes: when ≥1 item is checked, show a sticky action bar at the bottom of the viewport with: selected count + available bulk actions.

### 6.5 Search & Filter
Debounce search inputs at 300ms. Preserve filter state in the URL query string where possible (enables sharing and back-button support). Show a "clear filters" option when any filter is active.

### 6.6 Form Validation
Validate on submit (primary). Show inline field errors immediately after blur (secondary). Never show errors before the user has interacted with a field. On submit failure, focus the first errored field.

---

## 7. Implementation Notes

### 7.1 CSS Custom Properties
Define all design tokens as CSS custom properties on `:root`. This enables future theming and ensures consistency across all components.

### 7.2 Component Architecture
- **Vanilla JS / Blade:** One JS class or module per page/feature. Shared utilities in a single global helper file.
- **React/Vue/Svelte:** One component per distinct card/table/modal variant. Composition over prop-drilling. If a component takes >5 boolean props, split it.

### 7.3 Do NOT
- Use gradient backgrounds anywhere in the content area.
- Use box-shadows heavier than `0 1px 3px rgba(0,0,0,0.08)` on cards.
- Use `border-radius` > 4px on interactive elements (8px only on modals/overlays).
- Place text on colored backgrounds without WCAG AA contrast (4.5:1 for body text, 3:1 for large text).
- Use transitions longer than 200ms for UI interactions.
- Use native browser `<select>` — always use a custom styled dropdown.
- Use emoji characters (Unicode or HTML entities) in UI elements. Use inline SVGs (stroke-based, Lucide-style, `viewBox="0 0 24 24"`, `stroke="currentColor"`, `stroke-width` 1.5–2.5) instead.
- Leave async actions without visual feedback.
- Use `alert()`, `confirm()`, or `prompt()`.

### 7.4 DO
- Use `prefers-reduced-motion` media query to disable transitions for users who prefer it.
- Add visible focus indicators on all interactive elements (`--color-accent` ring, `outline-offset: 2px`).
- Add `aria-label` on all icon-only buttons.
- Ensure tables are keyboard-navigable (tab focus on rows, enter/space for actions).
- Use CSS `min()` / `clamp()` for responsive sizing rather than breakpoint overrides where possible.
- Use `<button type="button">` explicitly to prevent accidental form submissions.
- Set `loading="lazy"` on images below the fold.
- Wrap async calls in `try/catch/finally` — `finally` always restores loading state.

### 7.5 Accessibility Baseline
- All images have descriptive `alt` text; decorative images use `alt=""`.
- Form inputs are associated with `<label>` via `for`/`id` or `aria-labelledby`.
- Error messages are linked to their field via `aria-describedby`.
- Color is never the sole means of conveying information (always pair with text or icon).
- Interactive elements have a minimum 44×44px tap target size (or 36px with 4px margin).
