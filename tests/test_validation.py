import pytest
from pydantic import ValidationError

from app.schemas import LeadInput
from app.validation import normalize_lead


def test_normalization_and_idempotence(lead_data):
    lead = LeadInput(**(lead_data | dict(name="  Sarah Miller  ", email=" SARAH@EXAMPLE.COM ",
                                       company=" Acme ", service=" AI ", timeline=" soon ",
                                       source=" form ", message="  Need automation.  ")))
    result = normalize_lead(lead)
    assert result.model_dump() == dict(name="Sarah Miller", email="sarah@example.com",
                                     company="Acme", service="AI", timeline="soon", source="form",
                                     message="Need automation.", budget=None, company_size=None)
    assert normalize_lead(result) == result
    assert result is not lead


@pytest.mark.parametrize("change", [
    {"name": ""}, {"name": "   "}, {"message": "    "}, {"message": "  hi  "},
    {"message": "x" * 8001}, {"email": "not-email"}, {"budget": -1},
    {"budget": True}, {"budget": 1.5}, {"budget": "500"},
    {"company_size": 0}, {"company_size": False}, {"company_size": 1.2},
    {"name": None}, {"unexpected": "field"},
])
def test_invalid_input(lead_data, change):
    with pytest.raises(ValidationError):
        LeadInput(**(lead_data | change))


def test_zero_budget_and_optional_fields(lead_data):
    result = LeadInput(**lead_data, budget=0)
    assert result.budget == 0
    assert result.company_size is None
    assert result.source == "website"
