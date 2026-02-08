from typing import Dict, Any, List, Tuple
import json
import random
from dialogue.state import DialogueState
from config.system_prompts import SYSTEM_PROMPTS
from chains import ClassifiersChains, RAGChains, ConversationChain
from llms import Models
from utils.parsers import is_arabic_text

class DialogueManager:
    """
    Main dialogue manager that handles the complete conversation flow.
    Orchestrates classifiers, RAG chains, and state management.
    """
    def __init__(self):
        self.models = Models.create_llms()
        self.classifiers_chains = ConversationChain
        self.rag_chains = RAGChains
        self.conversation = ConversationChain
        
        # Initialize state and history for the conversation
        self.reset_state()
    
    
    
    def reset_state(self):
        """Reset dialogue state for new conversation"""
        self.state = DialogueState()
        self.global_history = []
    
    def _prepare_thread_history(self) -> List[Dict]:
        """Prepare thread history for classification"""
        return [
            {"thread_id": thread.thread_id, "question": thread.question}
            for thread in self.state.question_threads[-5:]  # Last 5 threads
        ]
    def _get_related_threads(self, related_thread_ids: list) -> List[str]:
        """Get related threads for the current question"""
        # This could be enhanced with semantic similarity
        return [thread.question for thread in self.state.question_threads if thread.thread_id in related_thread_ids]
    
    def handle_dialogue(self,user_input, state, global_history):
        global_history.append(("User", user_input))
        

        if not user_input.strip():
            response = random.choice(SYSTEM_PROMPTS["conditional_prompts"]["invalid"])
            global_history.append(("Sheikh", response))
            return response, None, state, global_history

        if not is_arabic_text(user_input):
            response = random.choice(SYSTEM_PROMPTS["conditional_prompts"]["non_arabic"])
            global_history.append(("Sheikh", response))
            return response, None, state, global_history

        filter_result = self.classifiers_chains.classify_intent(user_input=user_input)
        intent = filter_result.get("intent", "other")

        if intent == "social":
            response = self.conversation.predict(input=user_input)
            global_history.append(("Sheikh", response))
            return response, None, state, global_history

        parallel_results = self.classifiers_chains.classify_parallel(user_input=user_input)
        is_fiqh_related = parallel_results["fiqh"].get("is_fiqh_related", False)
        is_question_clear = parallel_results["fiqh"].get("is_question_clear", False)
        is_fatwa_type = parallel_results["fatwa"].get("is_fatwa_type", False)
        current_input_is_mazhab = parallel_results["mazhab"].get("is_mazhab_clear", False)
        current_input_category = parallel_results["mazhab"].get("category", "Unknown")

        processed_input = user_input
        if intent == "command" and is_fiqh_related:
            command_result = self.classifiers_chains.preprocess_command(user_input=user_input)
            if command_result.get("is_command", False):
                processed_input = command_result.get("reformulated_question", user_input)
                is_question_clear = True

        """rag_triggered = False
        formatter_result = None
        response = """""

        # Update mazhab if a new one is detected
        if current_input_is_mazhab:
            self.state = self.state.update_mazhab(current_input_category)

       

        if intent in ["question", "command"]:
            if is_fatwa_type:
                response = random.choice(SYSTEM_PROMPTS["conditional_prompts"]["fatwa_not_supported"])
                global_history.append(("Sheikh", response))
            elif not is_fiqh_related:
                response = random.choice(SYSTEM_PROMPTS["conditional_prompts"]["out_of_scope"])
                global_history.append(("Sheikh", response))
            elif not is_question_clear:
                response = random.choice(SYSTEM_PROMPTS["conditional_prompts"]["invalid"])
                global_history.append(("Sheikh", response))
            else:

                # START FROM HERE
                state["question_threads"].append({"thread_id": thread_id, "question": processed_input, "rag_response": None, "follow_ups": []})
                state["retries"] = 0

        # Check for pending questions when mazhab is clear
        if state["is_mazhab_clear"] and state["question_threads"]:
            rag_responses = []
            # Process all unanswered questions in question_threads
            for thread in state["question_threads"]:
                if not thread["rag_response"]:  # Process only unanswered questions
                    formatter_input = thread["question"]
                    formatter_result = rag_formatter.invoke({"input": formatter_input, "related_threads": json.dumps(related_threads)})
                    for question in [formatter_result["current_question"]] + formatter_result.get("related_questions", []):
                        rag_response = rag_agent.invoke({"category": state["category"], "question": question}).content
                        rag_responses.append(rag_response)
                    thread["rag_response"] = "\n\n".join(rag_responses[-len([formatter_result["current_question"]] + formatter_result.get("related_questions", [])):])
            if rag_responses:
                # NEW: Format RAG output using RAG_OUTPUT_FORMATTER
                chat_history = [{"sender": sender, "message": message} for sender, message in global_history]
                formatted_response = rag_output_formatter.invoke({
                    "rag_output": "\n\n".join(rag_responses),
                    "chat_history": json.dumps(chat_history)
                }).content
                response = formatted_response
                global_history.append(("RAG", response))
                rag_triggered = True
                formatter_memory.clear()
        elif state["question_threads"] and not state["is_mazhab_clear"]:
            state["retries"] += 1
            if state["retries"] >= 10:
                state["is_mazhab_clear"] = True
                state["category"] = "شافعي"
                state["mazhab_switched"] = True
                current_thread = state["question_threads"][-1]
                formatter_input = current_thread["question"]
                formatter_result = rag_formatter.invoke({"input": formatter_input, "related_threads": json.dumps(related_threads)})
                rag_responses = []
                for question in [formatter_result["current_question"]] + formatter_result.get("related_questions", []):
                    rag_response = rag_agent.invoke({"category": state["category"], "question": question}).content
                    rag_responses.append(rag_response)
                # NEW: Format RAG output using RAG_OUTPUT_FORMATTER
                chat_history = [{"sender": sender, "message": message} for sender, message in global_history]
                formatted_response = rag_output_formatter.invoke({
                    "rag_output": "\n\n".join(rag_responses),
                    "chat_history": json.dumps(chat_history)
                }).content
                response = formatted_response
                current_thread["rag_response"] = response
                global_history.append(("RAG", response))
                state["question_threads"][-1] = current_thread
                formatter_memory.clear()
                rag_triggered = True
            else:
                response = random.choice(conditional_prompts["missing_mazhab"])
                global_history.append(("Sheikh", response))

        if not rag_triggered and not response:
            if state["mazhab_switched"]:
                response = random.choice(conditional_prompts["mazhab_switched"])
                state["mazhab_switched"] = False
            elif current_input_is_mazhab and not state["question_threads"]:
                response = random.choice([
                    f"يا طالبي، شكرًا لاختيارك مذهب {state['category']}، فما الذي تريد أن نتعلمه سويًا؟",
                    f"أخي الحبيب، مذهب {state['category']} اختيار طيب، فما سؤالك الشرعي؟",
                    f"حبيبي، الآن وقد اخترت مذهب {state['category']}، فكيف أساعدك في طلب العلم؟"
                ])
            elif intent == "other":
                response = conversation.predict(input=user_input)
            else:
                response = random.choice([
                    "يا ولدي، أراك حريصًا على العلم، فما الذي تريد مناقشته في الفقه؟",
                    "أخي الطالب، قلبي معك في رحلة العلم، فما سؤالك الشرعي؟",
                    "حبيبي، نسأل الله أن ينفعك بالعلم، فكيف أساعدك اليوم؟"
                ]) if not state["is_mazhab_clear"] else conversation.predict(input=user_input)
            global_history.append(("Sheikh", response))

        return response, formatter_result, state, global_history