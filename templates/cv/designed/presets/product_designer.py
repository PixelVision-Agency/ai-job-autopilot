"""Product / UI-UX designer roles. Design-led; the code is supporting evidence.

So: the summary leads with design, the design-process language that is genuinely true
(wireframing, prototyping, user testing and feedback, design systems) is pulled to the front,
each job leads with the design decision rather than the stack, and the two ATS columns are
split design | technical so a recruiter can see the separation in one glance.

Use for: Product Designer, UI/UX Designer, Senior Product Designer, Digital Product Designer,
Design Systems Designer.
"""

from content_base import *  # noqa: F401,F403
from ._shared import reorder, skills

HEADLINE = "Product Designer · UI/UX, Design Systems & AI Features"

# The portfolio link is not repeated here: it already sits in the header line of both CVs,
# and a sentence about it costs a line.
PROFILE = (
    "Product designer with 9 years designing interfaces for web and mobile, from wireframes and "
    "prototypes through usability testing to a shipped product. At Example Co I lead the UI design "
    "for a customer-support platform whose AI drafts replies, including the composer where agents "
    "review those drafts and the design tokens the whole product shares. I design AI features "
    "specifically: what a suggestion should look like, how much of it to show, and what happens when "
    "the model is wrong. Because I also build the front end, my designs arrive as working interfaces "
    "rather than handoffs."
)

# Design leads the sidebar. Development stays - it is the differentiator - but second.
SKILLS = skills("Design", "Artificial Intelligence", "Product & Business", "Development", "Tools")

# Left column is design, right column is technical: the separation the review asked for.
ATS_SKILLS_LEFT = [
    "UI/UX Design",
    "Design Systems",
    "Wireframing & Prototyping",
    "Usability Testing",
    "Accessible Design (WCAG)",
    "Product Discovery",
    "Requirements & Scoping",
]
ATS_SKILLS_RIGHT = [
    "Figma & Storybook",
    "Designing AI & LLM Features",
    "Design-to-Code / Figma to Production",
    "HTML, CSS, JavaScript, TypeScript",
    "React, Next.js, Vue.js",
    "React Native & Expo",
    "Client Communication",
]

JOBS = reorder(
    {
        # Lead with design leadership, then the feature, then the design system (which carries
        # the team size). The stack sentence stays, rephrased so it reads as design reaching
        # production.
        "Example Co": [
            0,
            2,
            3,
            "Build the front end in React and TypeScript across the shared inbox, reply composer "
            "and analytics views, so the designs ship as built.",
        ],
        # Design framing, and without the closing code-review line, which points the wrong way
        # for a design-led CV.
        "Example Agency": [
            "Designed responsive marketing sites and campaign pages for retail and hospitality "
            "clients, and built them too.",
            1,
            2,
        ],
    },
    Freelance=[
        "Designed websites and web apps for small businesses and agencies, from wireframes and "
        "prototypes in Figma to the built product.",
        "Designed complete products end to end, from booking systems and client portals to online "
        "shops with subscription billing.",
        "Built the front end myself in React, Next.js and Vue, which kept the shipped interface "
        "faithful to the design.",
        2,
    ],
)
