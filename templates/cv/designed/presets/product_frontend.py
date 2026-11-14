"""Product / front-end engineering roles. Closest to the master content.

Engineering leads, design is the differentiator that follows it. This is the preset for the
large middle of the market: "Frontend Engineer", "Software Engineer (Frontend)", "Product
Engineer", "Full-Stack Engineer" with a front-end lean.

Use for: Frontend Engineer, Front-End Developer, Product Engineer, Software Engineer
(Frontend), UI Engineer, Web Developer.
"""

from content_base import *  # noqa: F401,F403
from ._shared import reorder, skills

HEADLINE = "Front-end Product Engineer · React, TypeScript & Design Systems"

PROFILE = (
    "Product engineer with 9 years building web and mobile products, from Figma to production. "
    "At Example Co I build the front end of a customer-support platform in React and TypeScript, "
    "across the shared inbox, the AI reply composer and the analytics views, and I set up the "
    "component library the team builds with. I work across React, Next.js, Vue, Nuxt, React Native "
    "and Node.js, and I add LLM features where they save people real work, at work and in two side "
    "projects of my own. Because I design as well as build, a requirement reaches a shipped "
    "interface without a handoff in the middle."
)

SKILLS = skills("Development", "Design", "Artificial Intelligence", "Product & Business", "Tools")

ATS_SKILLS_LEFT = [
    "Front-end Development",
    "React & TypeScript",
    "Next.js, Vue.js, Nuxt",
    "React Native & Expo",
    "HTML, CSS, Tailwind",
    "Node.js & API Integration",
    "Accessible Front-end (WCAG)",
]
ATS_SKILLS_RIGHT = [
    "Design Systems & Component Libraries",
    "UI/UX Design (Figma)",
    "Storybook",
    "LLM APIs & Prompt Engineering",
    "Workflow Automation",
    "Requirements & Scoping",
    "Cross-Functional Collaboration",
]

# Pure reorder, by index into content_base.
JOBS = reorder(
    {"Example Co": [1, 2, 3, 0]},
    Freelance=[0, 1, 3, 2],
)
