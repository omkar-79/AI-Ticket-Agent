import pytest
from ai_ticket_agent.sub_agents.follow_up.agent import analyze_feedback_with_llm

def test_analyze_feedback_with_llm_close(monkeypatch):
    # Mock follow_up_agent to return 'close' when called
    monkeypatch.setattr(
        "ai_ticket_agent.sub_agents.follow_up.agent.follow_up_agent",
        lambda prompt: "close"
    )
    result = analyze_feedback_with_llm("dummy_ticket_id", "Thank you, the issue is resolved.")
    assert result == "close"

def test_analyze_feedback_with_llm_reopen(monkeypatch):
    # Mock follow_up_agent to return 'reopen' when called
    monkeypatch.setattr(
        "ai_ticket_agent.sub_agents.follow_up.agent.follow_up_agent",
        lambda prompt: "reopen"
    )
    result = analyze_feedback_with_llm("dummy_ticket_id", "This did not fix my problem.")
    assert result == "reopen" 