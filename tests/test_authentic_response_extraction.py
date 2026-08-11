from cognition.response_style_router import ConversationStyle, analyze_conversation_style
from interface.authentic_response_engine import create_authentic_response_engine
from interface.personality_profile import create_default_profile


def test_response_style_router_detects_problem_solving():
    assert analyze_conversation_style("Can you help debug this error?") == ConversationStyle.PROBLEM_SOLVING


def test_personality_profile_preserves_local_identity_flags():
    profile = create_default_profile("Jay")
    data = profile.as_dict()
    assert data["jays_clever"] is True
    assert data["corporate_ai"] is False
    assert data["generic_assistant"] is False


def test_authentic_response_engine_returns_payload(tmp_path):
    engine = create_authentic_response_engine()
    engine.context_file = tmp_path / "context.json"
    payload = engine.generate_response("Hey Clever, what's up?")
    assert payload["text"]
    assert payload["conversation_style"] == "casual_check_in"
    assert payload["personal_connection"] == "exclusive_cognitive_partner"
