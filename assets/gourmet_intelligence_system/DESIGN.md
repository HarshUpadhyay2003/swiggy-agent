---
name: Gourmet Intelligence System
colors:
  surface: '#f9f9f9'
  surface-dim: '#dadada'
  surface-bright: '#f9f9f9'
  surface-container-lowest: '#ffffff'
  surface-container-low: '#f3f3f3'
  surface-container: '#eeeeee'
  surface-container-high: '#e8e8e8'
  surface-container-highest: '#e2e2e2'
  on-surface: '#1a1c1c'
  on-surface-variant: '#574236'
  inverse-surface: '#2f3131'
  inverse-on-surface: '#f1f1f1'
  outline: '#8b7264'
  outline-variant: '#dec1b0'
  surface-tint: '#984800'
  primary: '#984800'
  on-primary: '#ffffff'
  primary-container: '#fc8019'
  on-primary-container: '#5e2a00'
  inverse-primary: '#ffb689'
  secondary: '#615e5b'
  on-secondary: '#ffffff'
  secondary-container: '#e4dfdb'
  on-secondary-container: '#65625f'
  tertiary: '#1b6d01'
  on-tertiary: '#ffffff'
  tertiary-container: '#63b549'
  on-tertiary-container: '#0c4200'
  error: '#ba1a1a'
  on-error: '#ffffff'
  error-container: '#ffdad6'
  on-error-container: '#93000a'
  primary-fixed: '#ffdbc8'
  primary-fixed-dim: '#ffb689'
  on-primary-fixed: '#311300'
  on-primary-fixed-variant: '#733500'
  secondary-fixed: '#e7e1de'
  secondary-fixed-dim: '#cbc5c2'
  on-secondary-fixed: '#1d1b19'
  on-secondary-fixed-variant: '#494644'
  tertiary-fixed: '#a1f882'
  tertiary-fixed-dim: '#86db69'
  on-tertiary-fixed: '#032100'
  on-tertiary-fixed-variant: '#115300'
  background: '#f9f9f9'
  on-background: '#1a1c1c'
  surface-variant: '#e2e2e2'
typography:
  display-lg:
    fontFamily: Playfair Display
    fontSize: 48px
    fontWeight: '700'
    lineHeight: 56px
    letterSpacing: -0.02em
  headline-lg:
    fontFamily: Playfair Display
    fontSize: 32px
    fontWeight: '700'
    lineHeight: 40px
  headline-lg-mobile:
    fontFamily: Playfair Display
    fontSize: 28px
    fontWeight: '700'
    lineHeight: 34px
  headline-md:
    fontFamily: Playfair Display
    fontSize: 24px
    fontWeight: '600'
    lineHeight: 32px
  body-lg:
    fontFamily: Inter
    fontSize: 18px
    fontWeight: '400'
    lineHeight: 28px
  body-md:
    fontFamily: Inter
    fontSize: 16px
    fontWeight: '400'
    lineHeight: 24px
  label-lg:
    fontFamily: Inter
    fontSize: 14px
    fontWeight: '600'
    lineHeight: 20px
    letterSpacing: 0.01em
  label-sm:
    fontFamily: Inter
    fontSize: 12px
    fontWeight: '500'
    lineHeight: 16px
rounded:
  sm: 0.5rem
  DEFAULT: 1rem
  md: 1.5rem
  lg: 2rem
  xl: 3rem
  full: 9999px
spacing:
  base: 8px
  xs: 4px
  sm: 12px
  md: 24px
  lg: 40px
  xl: 64px
  container-max: 1200px
  gutter: 20px
---

## Brand & Style

The design system is engineered to bridge the gap between high-utility AI interfaces and the sensory-rich world of food commerce. It targets a premium demographic that values convenience, curation, and culinary aesthetics. The emotional response is one of "effortless indulgence"—the UI should feel like a digital concierge that understands personal taste and handles the logistics of dining with sophisticated ease.

The style is a hybrid of **Minimalism** and **Glassmorphism**, leveraging the clean, information-dense layouts of modern AI platforms with the tactile, premium physical metaphors of a luxury digital wallet. 

- **Intelligence:** Evoked through generous white space and structured typographic hierarchy.
- **Warmth:** Achieved through a cream-based neutral palette and organic, oversized corner radii.
- **Premium:** Conveyed through high-contrast serif headings and subtle, layered transparency.

## Colors

The color palette is anchored in appetite-stimulating tones and high-clarity neutrals.

- **Primary (Swiggy Orange):** Used exclusively for high-intent actions, primary buttons, and brand indicators. It is the heat of the design.
- **Secondary (Light Cream):** The foundation of the UI. This warm off-white creates a softer, more "organic" feel than pure white, reducing eye strain and feeling more "kitchen-natural."
- **Tertiary (Accent Green):** Specifically reserved for vegetarian indicators, success states, and "Healthy Choice" callouts.
- **Neutral (Warm Grey):** Used for structural backgrounds, subtle borders, and secondary surfaces to create depth without harsh contrast.

## Typography

This design system utilizes a high-contrast typographic pairing to balance editorial elegance with functional utility.

- **Headlines:** Use **Playfair Display**. This serif typeface provides a literary, premium feel reminiscent of high-end menus and culinary magazines. It should be used for dish names, restaurant titles, and AI-generated headers.
- **Body & UI:** Use **Inter**. This neutral, systematic sans-serif ensures maximum legibility for nutritional data, prices, and conversational text. 
- **Formatting:** Use tight letter-spacing for large serif displays to maintain a sophisticated "tight" editorial look. Body text should maintain standard tracking for optimal readability.

## Layout & Spacing

The layout follows a **Fluid Grid** model with generous "breathing room" to ensure the food imagery remains the hero. 

- **Desktop:** 12-column grid with 24px gutters and 64px side margins.
- **Mobile:** 4-column grid with 16px gutters and 20px side margins.
- **Rhythm:** Spacing follows an 8px base unit. Use `lg` (40px) or `xl` (64px) spacing between major sections to prevent the UI from feeling cluttered. AI conversational bubbles should have a max-width of 85% of the container to maintain a clear chat-like structure.

## Elevation & Depth

Depth is used to distinguish between the "AI layer" and the "Physical Food layer."

- **Glassmorphism:** AI response bubbles and floating navigation bars use a background blur (12px to 20px) with a semi-transparent white fill (`rgba(255, 255, 255, 0.7)`). This creates a sense of the intelligence "floating" over the food content.
- **Ambient Shadows:** Physical cards (food, restaurants) use very soft, diffused shadows with a slight warm tint (#201000 at 5% opacity). Shadows should have a large blur radius (30px+) and low spread to mimic natural, soft lighting.
- **Tonal Layering:** The primary background is `Secondary (Cream)`, while active input areas or highlighted containers use pure White to "pop" forward.

## Shapes

The shape language is extremely organic and "soft," mimicking the rounded edges of a high-end physical wallet or a polished ceramic plate.

- **Primary Radius:** 24px (used for cards, conversational bubbles, and large containers).
- **Secondary Radius:** 16px (used for input fields and smaller nested elements).
- **Interactive Elements:** Buttons and floating action chips use a fully "Pill" shape (999px) to invite touch and denote interactivity.
- **Images:** Food photography should always be masked with the primary 24px radius or, in specific gallery views, a perfect circle.

## Components

- **Conversational Bubbles:** AI bubbles use the glassmorphic style with a subtle 1px white border. User bubbles are solid `Primary (Orange)` with white text for high contrast. Both use a 24px radius, with the "tail" corner being slightly sharper (8px) to indicate direction.
- **Food Cards:** Large-scale imagery is mandatory. Cards should have minimal text overlays—titles in `Playfair Display` at the bottom, price in a floating pill-shaped chip at the top-right.
- **Floating Action Chips:** Small, pill-shaped buttons (`Inter`, weight 600) that float at the bottom of the AI interface to suggest next steps (e.g., "Add to cart," "Show similar," "Vegan options").
- **Input Fields:** Search and AI prompts should be large (56px+ height), pill-shaped, and use a subtle `Warm Grey` background that turns pure white with a soft orange glow on focus.
- **Success States:** Use a soft wash of `Accent Green` with 10% opacity for backgrounds of successful order or "Veg" filtered cards.