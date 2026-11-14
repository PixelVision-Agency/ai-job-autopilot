"""AI engineer / AI product roles: building products on top of LLM APIs.

Not ML research. This preset is for postings that want someone **implementing AI** - shipping
LLM features into a product, wiring up agentic workflows, automating work that used to be
manual - not someone training models. If a posting requires a PhD, publications, or training
from scratch, it is the wrong posting, not the wrong preset.

It covers two shapes of the same capability, because the evidence is the same either way:

  - **AI product engineering** - building the AI features of someone's product
  - **AI solutions / integration** - implementing AI inside a business: automations,
    integrations, internal tooling. This is the shape most contract work takes, and the
    freelance AI-automation line plus n8n/Zapier is what backs it.

Use for: AI Engineer, AI Product Engineer, Applied AI Engineer, AI Solutions Engineer,
Forward Deployed Engineer, Automation Engineer, Full-Stack Engineer on an AI product.
"""

from content_base import *  # noqa: F401,F403
from ._shared import reorder, skills

HEADLINE = "AI Product Engineer · LLM Features, Automation & Front-end"

PROFILE = (
    "Product engineer with 9 years shipping web and mobile products, now building AI into them. "
    "At Example Co I designed and built the AI reply composer of a customer-support platform: the "
    "suggestion panel, the tone controls, and the feedback that shows which drafts agents rewrote. "
    "I have shipped two LLM side projects of my own, comparing three models on real email threads "
    "before choosing one, and I built n8n automations that took lead sorting and first-draft "
    "proposals off a freelance workload. I build the interface as well as the integration, so an AI "
    "feature arrives as something people can actually use."
)

SKILLS = skills("Artificial Intelligence", "Automation", "Development", "Design", "Tools")

ATS_SKILLS_LEFT = [
    "LLM APIs & Integration",
    "Prompt Engineering",
    "Model Evaluation",
    "AI Feature Design",
    "AI-Assisted Development (Claude Code, Cursor)",
    "Workflow Automation (n8n, Zapier)",
    "API Integration & Webhooks",
]
ATS_SKILLS_RIGHT = [
    "React & TypeScript",
    "Next.js, Vue.js, Nuxt",
    "React Native & Expo",
    "Node.js",
    "UI/UX Design & Design Systems",
    "Product Discovery",
    "Requirements & Scoping",
]

JOBS = reorder(
    {"Example Co": [
        2,
        1,
        "Lead UI design for the platform, and set up the Storybook component library matched to "
        "the Figma design tokens.",
    ]},
    Freelance=[3, 0, 1, 2],
)
