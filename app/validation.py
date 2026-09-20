from app.schemas import LeadInput


def normalize_lead(lead: LeadInput) -> LeadInput:
    """Return a validated copy; input validators trim text before length checks."""
    return LeadInput.model_validate(lead.model_dump())
