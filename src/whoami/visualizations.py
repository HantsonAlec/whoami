import plotly.graph_objects as go
from datetime import datetime
from typing import List, Dict, Any


class SkillsVisualization:
    SKILLS_DATA = {
        "Programming Languages": {
            "Python": 5,
            "Ruby on Rails": 3,
            "SQL": 4,
        },
        "AI/ML": {
            "Large Language Models": 5,
            "Computer Vision": 4,
            "NER": 4,
            "OCR": 4,
            "ML/DL Frameworks": 4,
            "Spacy": 4,
        },
        "Cloud & DevOps": {
            "AWS": 4,
            "Azure": 4,
            "Docker": 4,
            "Kubernetes": 3,
            "Terraform": 4,
            "Jenkins": 3,
            "Dagster": 4,
        },
        "Web & APIs": {
            "FastAPI": 5,
            "REST APIs": 4,
            "Web Development": 4,
        },
        "Data": {
            "PostgreSQL": 4,
            "Redis": 3,
            "ETL Pipelines": 4,
            "Data Science": 4,
            "Big Data": 3,
        },
        "Tools & Other": {
            "Git": 5,
            "Pulsar": 3,
            "Azure Cognitive Services": 4,
            "Azure AI Document Intelligence": 4,
        },
    }

    @classmethod
    def get_skill_categories(cls) -> Dict[str, List[str]]:
        """Get all skills organized by category."""
        return {category: list(skills.keys()) for category, skills in cls.SKILLS_DATA.items()}


class TimelineVisualization:
    """Create interactive career timeline."""

    TIMELINE_DATA = [
        {
            "type": "work",
            "title": "AI Consultant",
            "company": "Christelijke Mutualiteit",
            "start": "2025-01",
            "end": "Present",
            "description": "AI team developing virtual assistants and chatbots. Built internal assistant for email processing.",
            "technologies": ["Python", "FastAPI", "LLM", "Dagster", "Terraform", "AWS"],
            "color": "#4ECDC4",
        },
        {
            "type": "work",
            "title": "Consultant",
            "company": "Meemoo",
            "start": "2023-10",
            "end": "2024-12",
            "description": "Audio/video and image processing systems. Transcription & NER from research to production.",
            "technologies": ["Python", "FastAPI", "Computer Vision", "Pulsar", "Kubernetes"],
            "color": "#4ECDC4",
        },
        {
            "type": "work",
            "title": "AI Engineer",
            "company": "Sopra Steria",
            "start": "2023-09",
            "end": "Present",
            "description": "Internal AI projects including IDP research, speech-to-text, LLMs, and computer vision.",
            "technologies": ["Python", "Azure Cognitive Services", "LLM", "Azure AI Document Intelligence"],
            "color": "#4ECDC4",
        },
        {
            "type": "work",
            "title": "Backend Engineer",
            "company": "Docfield AI",
            "start": "2022-02",
            "end": "2023-08",
            "description": "Grew from intern to full-time. ML model development, API creation, cloud infrastructure.",
            "technologies": ["Python", "Ruby on Rails", "Spacy", "OCR", "NER"],
            "color": "#4ECDC4",
        },
        {
            "type": "education",
            "title": "Postgraduate IT Management",
            "company": "HOGENT",
            "start": "2022-09",
            "end": "2023-06",
            "description": "Project/Application management, Business Analysis, Requirements Engineering.",
            "technologies": ["Management", "Business Analysis"],
            "color": "#FF6B6B",
        },
        {
            "type": "education",
            "title": "Bachelor Multimedia & Communication Technology - AI Engineer",
            "company": "HOWEST",
            "start": "2019-09",
            "end": "2022-06",
            "description": "Magna cum laude. IoT, Cloud, Web development, ML & DL, big data, data science and MLOps.",
            "technologies": ["AI", "ML", "DL", "IoT", "Cloud", "MLOps"],
            "color": "#FF6B6B",
        },
    ]

    @classmethod
    def parse_date(cls, date_str: str) -> datetime:
        """Parse date string to datetime object."""
        if date_str.lower() == "present":
            return datetime.now()
        return datetime.strptime(date_str, "%Y-%m")

    @classmethod
    def create_timeline(cls) -> go.Figure:
        """
        Create an interactive Gantt-style timeline of career and education.
        """
        # Sort by start date
        sorted_timeline = sorted(cls.TIMELINE_DATA, key=lambda x: cls.parse_date(x["start"]))

        fig = go.Figure()

        for i, item in enumerate(sorted_timeline):
            start_date = cls.parse_date(item["start"])
            end_date = cls.parse_date(item["end"])

            # Create hover text
            hover_text = f"<b>{item['title']}</b><br>"
            hover_text += f"{item['company']}<br>"
            hover_text += f"{item['start']} - {item['end']}<br><br>"
            hover_text += f"{item['description']}<br><br>"
            hover_text += "<b>Technologies:</b><br>"
            hover_text += ", ".join(item["technologies"])

            # Add timeline bar
            fig.add_trace(
                go.Scatter(
                    x=[start_date, end_date],
                    y=[i, i],
                    mode="lines+markers",
                    name=f"{item['company']} - {item['title']}",
                    line=dict(color=item["color"], width=20),
                    marker=dict(size=12, color=item["color"], symbol="circle"),
                    hovertemplate=hover_text + "<extra></extra>",
                    showlegend=False,
                )
            )

            # Add text annotation
            mid_date = start_date + (end_date - start_date) / 2
            icon = "🎓" if item["type"] == "education" else "💼"

            fig.add_annotation(
                x=mid_date,
                y=i,
                text=f"{icon} {item['company']}",
                showarrow=False,
                font=dict(size=11, color="white", family="Arial Black"),
                bgcolor=item["color"],
                borderpad=4,
            )

        fig.update_layout(
            title={
                "text": "📅 Career & Education Timeline",
                "x": 0.5,
                "xanchor": "center",
                "font": {"size": 24, "color": "#2c3e50"},
            },
            xaxis=dict(title="", showgrid=True, gridcolor="rgba(200,200,200,0.3)"),
            yaxis=dict(
                title="",
                showticklabels=False,
                showgrid=False,
                zeroline=False,
            ),
            height=600,
            hovermode="closest",
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
        )

        return fig

    @classmethod
    def create_timeline_table(cls) -> List[Dict[str, Any]]:
        """
        Create a structured table view of the timeline.
        Returns data suitable for display in Streamlit dataframe.
        """
        table_data = []
        for item in sorted(cls.TIMELINE_DATA, key=lambda x: cls.parse_date(x["start"]), reverse=True):
            table_data.append(
                {
                    "Type": "🎓 Education" if item["type"] == "education" else "💼 Work",
                    "Period": f"{item['start']} - {item['end']}",
                    "Title": item["title"],
                    "Organization": item["company"],
                    "Key Technologies": ", ".join(item["technologies"][:5]),
                }
            )
        return table_data


def generate_question_suggestions(skill_or_event: str, context_type: str = "skill") -> List[str]:
    """
    Generate relevant question suggestions based on clicked skill or timeline event.

    Args:
        skill_or_event: The skill name or timeline event clicked
        context_type: Either 'skill' or 'experience'

    Returns:
        List of suggested questions
    """
    if context_type == "skill":
        return [
            f"What projects has Alec used {skill_or_event} in?",
            f"Tell me about Alec's experience with {skill_or_event}",
            f"What has Alec built using {skill_or_event}?",
        ]
    else:
        return [
            f"Tell me more about Alec's work at {skill_or_event}",
            f"What did Alec accomplish at {skill_or_event}?",
            f"What technologies did Alec use at {skill_or_event}?",
        ]
