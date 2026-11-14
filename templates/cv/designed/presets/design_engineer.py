"""Design engineer / UX engineer / design technologist: design AND code, equally.

The rarest and strongest positioning - most candidates are one or the other. Lead with the
pairing itself, then prove both halves on the same feature.

Use for: Design Engineer, UX Engineer, Design Technologist, Front-End Designer, Creative
Technologist, Product Engineer at a design-led company.
"""

from content_base import *  # noqa: F401,F403
from ._shared import reorder, skills

HEADLINE = "Design Engineer · UI/UX, Design Systems & React"

PROFILE = (
    "Design engineer with 9 years designing interfaces and shipping the front-end code behind them, "
    "from Figma to production. At Example Co I lead the UI design for a customer-support platform "
    "and build it in React, including the AI reply composer agents use all day and the Storybook "
    "component library matched to our Figma tokens. I work across React, TypeScript, Next.js and "
    "React Native, and I treat accessibility and design tokens as part of the build, not a review "
    "step. I do my best work owning a product surface end to end, design decisions and shipped "
    "code in the same pair of hands."
)

SKILLS = skills("Design", "Development", "Artificial Intelligence", "Product & Business", "Tools")

ATS_SKILLS_LEFT = [
    "UI/UX Design",
    "Design Systems in Code",
    "Figma to Production Front-end",
    "Wireframing & Prototyping",
    "Accessible Design (WCAG)",
    "Usability Testing",
]
ATS_SKILLS_RIGHT = [
    "React & TypeScript",
    "Next.js, Vue.js, Nuxt",
    "HTML, CSS, Tailwind",
    "Storybook",
    "LLM APIs",
    "AI-Assisted Development (Claude Code)",
]

# Pure reorder, by index into content_base: lead with the feature designed AND built,
# then the design leadership, the design system, and the stack last.
JOBS = reorder({"Example Co": [2, 0, 3, 1]})
