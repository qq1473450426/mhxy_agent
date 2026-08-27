from mhxy_agent.execution.mentor import MentorPlanner
from mhxy_agent.execution.models import ActionKind, Observation
from mhxy_agent.execution.mock import MockExecutor
from mhxy_agent.execution.safety import validate_action


def test_mentor_first_action_is_interaction():
    action = MentorPlanner().next_action(Observation(scene="city"))
    assert action.kind is ActionKind.INTERACT
    assert action.target == "师门使者"


def test_mock_observe_execute_verify_cycle():
    executor = MockExecutor()
    before = executor.observe()
    action = MentorPlanner().next_action(before)
    allowed, _ = validate_action(action)
    assert allowed
    result = executor.execute(action)
    assert result.success
    after = executor.observe()
    assert after.scene == "school_task"


def test_invalid_move_is_rejected():
    from mhxy_agent.execution.models import Action
    action = Action(ActionKind.MOVE, "无目标移动")
    allowed, message = validate_action(action)
    assert not allowed
    assert "目标" in message
