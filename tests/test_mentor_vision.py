from mhxy_agent.execution.mentor import MentorTargetDetector, MentorPlanner
from mhxy_agent.execution.models import Observation, ActionKind
from mhxy_agent.execution.vision import TextRegion, VisionResult


def test_detect_mentor_target_and_center():
    result = VisionResult(
        scene="city",
        text="师门使者",
        confidence=0.95,
        regions=(TextRegion("师门使者", 0.95, (100, 200, 80, 20)),),
    )
    assert MentorTargetDetector().find_target(result) == (140, 210, "师门使者", 0.95)


def test_planner_does_not_guess_coordinate_without_vision():
    action = MentorPlanner().next_action(Observation(scene="city"))
    assert action.kind is ActionKind.OBSERVE


def test_planner_creates_interaction_from_vision():
    result = VisionResult("city", "师门使者", 0.95, (TextRegion("师门使者", 0.95, (10, 20, 30, 10)),))
    action = MentorPlanner().next_action(Observation(scene="city"), result)
    assert action.kind is ActionKind.INTERACT
    assert action.target == "师门使者"
