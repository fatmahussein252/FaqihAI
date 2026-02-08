from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional

@dataclass
class Thread:
    thread_id: int
    question: str
    rag_response: Optional[str] = None
    follow_ups: List[str] = field(default_factory=list)

@dataclass
class DialogueState:
    """Immutable state container for dialogue"""
    question_threads: List[Thread] = field(default_factory=list)
    is_mazhab_clear: bool = False
    category: str = "Unknown"
    retries: int = 0
    mazhab_switched: bool = False
    
    def add_thread(self, question: str) -> 'DialogueState':
        """Return new state with added thread"""
        new_thread = Thread(
            thread_id=len(self.question_threads) + 1,
            question=question
        )
        return DialogueState(
            question_threads=self.question_threads + [new_thread],
            is_mazhab_clear=self.is_mazhab_clear,
            category=self.category,
            retries=0,  # Reset retries on new question
            mazhab_switched=self.mazhab_switched
        )
    
    def update_mazhab(self, category: str) -> 'DialogueState':
        """Return new state with updated mazhab"""
        return DialogueState(
            question_threads=self.question_threads,
            is_mazhab_clear=True,
            category=category,
            retries=0,  # Reset retries when mazhab is clear
            mazhab_switched=False
        )