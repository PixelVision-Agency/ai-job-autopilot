"""Example CV content: a fictional candidate, so the template renders out of the box.

Nothing here is real. `content_base.py` uses this file only when `profile/cv_content.py`
(your own content, gitignored) does not exist. Copy this file to `profile/cv_content.py`
and replace every value with your own; keep the names and structure.

The designed CV joins each job's sentences into a paragraph; the ATS resume shows them as
bullets. A per-application module (cv/main_<company>_<role>.py) imports * from content_base
and overrides only what the role needs - see template.py for the skeleton.
"""

MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

NAME = "Alex Example"
HEADLINE = "Product Engineer · React, Design Systems & AI"

CONTACT = {
    "location": "Example City, Country",
    "availability": "Open to remote work",  # optional: leave the key out when you have nothing to say
    "phone": "+00 000 000 000",
    "email": "alex@example.com",
    "website": "example.com",
    "linkedin": "linkedin.com/in/alex-example",
    "github": "github.com/alex-example",
}

PROFILE = (
    "Product engineer with 9 years of experience designing and building web and mobile products, "
    "from Figma to production. Known for turning messy requirements into simple interfaces, building "
    "them in React and TypeScript, and adding AI features where they save people real work. Has worked "
    "in an agency, as a freelancer and inside a product team, owning features from the first sketch to "
    "the release. Skilled in UI/UX design, design systems, front-end development and LLM integration."
)

# Order matters: the designed CV renders these top to bottom in the sidebar.
SKILLS = [
    ("Artificial Intelligence", ["LLM APIs", "AI Feature Design", "Prompt Engineering", "Model Evaluation", "AI-Assisted Development"]),
    ("Automation", ["Workflow Automation", "API Integration", "Webhooks", "n8n", "Zapier"]),
    ("Design", ["UI/UX Design", "Design Systems", "Wireframing & Prototyping", "Usability Testing", "Accessible Design (WCAG)"]),
    (
        "Development",
        ["Web & Mobile App Development", "TypeScript", "JavaScript", "React", "Next.js", "Vue.js", "Nuxt", "React Native", "Node.js", "Tailwind"],
    ),
    (
        "Product & Business",
        ["Product Discovery", "Requirements & Scoping", "Estimation & Planning", "Client Communication", "Cross-Functional Collaboration"],
    ),
    ("Tools", ["Figma", "Storybook", "Linear", "Claude Code", "Cursor"]),
]

# The ATS CV shows a short two-column list instead of the categories above.
ATS_SKILLS_LEFT = [
    "Product Discovery & Scoping",
    "UI/UX Design & Prototyping",
    "Design Systems (Figma, Storybook)",
    "Usability Testing",
    "Accessible Design (WCAG)",
    "Client Communication",
    "Cross-Functional Collaboration",
]
ATS_SKILLS_RIGHT = [
    "React & TypeScript",
    "Next.js, Vue.js, Nuxt",
    "React Native & Expo",
    "Node.js & API Integration",
    "LLM APIs & Prompt Engineering",
    "Workflow Automation (n8n, Zapier)",
    "AI-Assisted Development (Claude Code, Cursor)",
]

LANGUAGES = [("English", "Native"), ("German", "Intermediate (B1)")]

# Contact details are shared only on request, with the referee's permission.
REFERENCES = [
    {"name": "Sam Referee", "role": "Engineering Manager, Example Co"},
    {"name": "Jordan Sample", "role": "Creative Director, Example Agency"},
]
REFERENCES_NOTE = "Contact details available upon request."

# Dates. start/end are optional and accept every form below, so an unknown month never has to
# be invented:
#   (2021, 3)  month and year  -> "03/2021" (ATS), "Mar 2021" (designed)
#   (2021,)    year only; 2021 and (2021, None) mean the same
#   leave "start" out (or None) when the whole date is unknown; with an "end" only, the entry
#   shows just that year
# An "end" of None (or no "end") means Present. "company" is optional too: leave it out when the
# employer is unknown or private and the role (plus location) is shown on its own; never put the
# string "None" or a placeholder there. The same date rules apply to EDUCATION.
JOBS = [
    {
        "company": "Example Co",
        "role": "Senior Product Engineer",
        "start": (2022, 5),
        "end": None,
        "location": "Example City, Country",
        "remote": True,
        "sentences": [
            "Lead UI design for a customer-support platform whose AI drafts replies that support agents review, edit and send.",
            "Build the front end in React and TypeScript across the shared inbox, the reply composer and the analytics views.",
            "Designed and built the AI reply composer, from the suggestion panel and tone controls to the feedback that "
            "shows the team which drafts agents rewrote before sending.",
            "Set up the component library in Storybook, matched to the Figma design tokens and used by a team of eight "
            "engineers, and moved the product to one accessible colour system.",
        ],
    },
    {
        "company": "Freelance",
        "role": "Freelance Front-end Developer",
        "start": (2019, 4),
        "end": (2022, 4),
        "location": None,
        "remote": True,
        "sentences": [
            "Designed and built websites and web apps for small businesses and agencies, from wireframes in Figma to "
            "production in React, Next.js and Vue.",
            "Delivered booking systems, client portals and online shops, including Stripe checkout and subscription billing.",
            "Ran each project from first call to handover, handling scoping, estimates, timelines and client "
            "communication, with typical engagements of two to four months.",
            "Built n8n automations with LLM APIs that sorted inbound leads and drafted first-pass project proposals.",
        ],
    },
    {
        "company": "Example Agency",
        "role": "Web Designer & Developer",
        "start": (2017, 9),
        "end": (2019, 3),
        "location": "Example City, Country",
        "remote": False,
        "sentences": [
            "Designed and built responsive marketing sites and campaign pages for the agency's retail and hospitality clients.",
            "Turned the agency's page designs into reusable templates, so new client sites launched in days rather than weeks.",
            "Moved the agency's sites onto one shared set of components and documented how to use them.",
            "Wrote the agency's front-end coding guidelines and reviewed other developers' pull requests.",
        ],
    },
    {
        "company": "Example Studio",
        "role": "Design Intern",
        "start": (2016, 6),
        "end": (2016, 8),
        "location": "Example City, Country",
        "remote": False,
        "sentences": ["Designed social media graphics and helped redesign the studio's own website during a summer internship."],
    },
]

# Optional sections: an empty PROJECTS, REFERENCES (with an empty REFERENCES_NOTE) or
# CERTIFICATIONS list is simply not drawn - no empty heading in either CV.

# `card` is what the designed CV shows (title after the dash, description, stack); None = ATS only.
# An optional card["image"] names a file in the template's assets/ folder.
PROJECTS = [
    {
        "name": "Example App One",
        "descriptor": "Personal project - habit-tracking app for iOS and Android",
        "bullets": [
            "Designed and built a habit tracker in React Native and Expo with an LLM coach that writes a short weekly "
            "review from the user's own entries.",
            "Kept every entry on the device and sent the model only a summary, so the coach works without an account.",
        ],
        "card": {
            "title": "habit-tracking app",
            "description": "Habit tracker for iOS and Android with an LLM coach that writes a weekly review from the user's own entries.",
            "stack": ["React Native", "Expo", "LLM APIs"],
        },
    },
    {
        "name": "Example App Two",
        "descriptor": "Personal project - browser extension for long email threads",
        "bullets": [
            "Built a browser extension in TypeScript that summarises long email threads and lists the questions still open in them.",
            "Compared three models on 200 of my own threads before choosing one, weighing accuracy against cost per summary.",
        ],
        "card": {
            "title": "email-thread extension",
            "description": "Browser extension that summarises long email threads and lists the questions still open in them.",
            "stack": ["TypeScript", "Browser Extensions", "LLM APIs"],
        },
    },
    {
        "name": "Example Client Platform",
        "descriptor": "Client project - booking system for a chain of fitness studios",
        "bullets": [
            "Designed the member app and the staff dashboard for a chain of fitness studios that manages classes, "
            "bookings and memberships.",
            "Built the dashboard in Next.js and the member app in React Native, with a back-end developer on the client's side.",
        ],
        "card": None,
    },
    {
        "name": "Example Client Shop",
        "descriptor": "Client project - online shop with subscriptions for a coffee roaster",
        "bullets": [
            "Designed and built an online shop for a coffee roaster in Nuxt on top of the Shopify Storefront API.",
            "Added subscription orders with Stripe Billing, which became the client's main source of repeat sales.",
        ],
        "card": None,
    },
]

# school, degree, dates, location and sentences are all optional; leave out what is unknown
# (with no school, the degree is shown as the entry title).
EDUCATION = [
    {
        "school": "Example University",
        "degree": "BSc Media Technology",
        "start": (2014, 9),
        "end": (2017, 6),
        "location": "Example City, Country",
        "sentences": ["Studied interaction design, web development and user research."],
    },
    {
        "school": "Example College",
        "degree": "Foundation Diploma in Art & Design",
        "start": (2013, 9),
        "end": (2014, 6),
        "location": "Example City, Country",
        "sentences": ["Built a portfolio in illustration, typography and photography."],
    },
]

# Optional. name is required; issuer and year are optional. Shown compactly in the designed
# sidebar and after Education in the ATS resume; an empty list draws nothing.
# CERTIFICATIONS = [
#     {"name": "Example Cloud Practitioner", "issuer": "Example Cert Body", "year": 2022},
#     {"name": "Example Scrum Master"},
# ]
CERTIFICATIONS = []

# Document properties for the PDFs. Only skills the CV itself states - this is visible, standard
# metadata, not a place to stuff extra keywords.
METADATA = {
    "title": f"{NAME} - {HEADLINE}",
    "author": NAME,
    "subject": f"CV of {NAME}, product engineer working across UI/UX design, React front-end development and AI features",
    "keywords": ", ".join([
        "Product Engineer", "UI/UX Design", "Front-end Development", "Design Systems", "Figma", "Storybook",
        "React", "TypeScript", "Next.js", "Vue.js", "Nuxt", "React Native", "Node.js",
        "LLM APIs", "Workflow Automation", "Remote",
    ]),
}
