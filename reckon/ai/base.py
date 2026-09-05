from abc import ABC, abstractmethod
from typing import Dict, List, Optional


class AIProvider(ABC):
    """
    The only contract the rest of the app knows about.

    Swapping providers is a settings change, never a code change. Every method
    returns plain Python types so nothing downstream depends on a vendor SDK.
    """

    name = "base"

    @abstractmethod
    def challenge(self, decision: Dict) -> Dict:
        """Argue against a decision.

        Returns ``counterarguments``, ``blind_spots``, ``failure_conditions``
        (lists of strings) and ``sharpest_question``.
        """

    @abstractmethod
    def advise(
        self,
        question: str,
        topic: str,
        profile: Dict,
        track_record: Dict,
        assessment: Optional[Dict],
        history: List[Dict],
    ) -> Dict:
        """Answer a question about a decision the person is weighing.

        ``assessment`` holds arithmetic already computed from their profile — it
        is passed in rather than derived here, so no provider ever invents a
        number. Returns ``answer``, ``numbers``, ``considerations``,
        ``watch_outs`` and ``suggested_decision``.
        """
