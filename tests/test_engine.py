import unittest

from mhxy_agent.engine import DEFAULT_TASKS, StrategyEngine
from mhxy_agent.models import GameProfile, Task

class EngineTests(unittest.TestCase):
    def setUp(self):
        self.engine = StrategyEngine()

    def test_level_nodes(self):
        self.assertEqual(self.engine.classify_level(69), "60-69")
        self.assertEqual(self.engine.next_node(69), 89)

    def test_task_profit(self):
        task = Task("t", 60, cash=100, success_rate=0.5, consumption=10)
        self.assertEqual(task.expected_cash, 50)
        self.assertEqual(task.expected_profit, 40)

    def test_state(self):
        profile = GameProfile(characters=[object(), object(), object(), object(), object()])
        self.assertEqual(profile.state, 10)

    def test_rank_tasks(self):
        chosen = self.engine.rank_tasks(DEFAULT_TASKS, 1)
        self.assertLessEqual(sum(t.minutes for t in chosen), 60)
        self.assertTrue(chosen)

if __name__ == "__main__":
    unittest.main()
