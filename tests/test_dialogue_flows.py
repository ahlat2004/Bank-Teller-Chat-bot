"""
Unit Tests for Dialogue Flows
Tests multi-turn conversations, slot filling, and confirmations
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.app.ml.dialogue.dialogue_manager import DialogueManager
from backend.app.ml.dialogue.dialogue_state import DialogueState, ConversationStatus
from backend.app.ml.dialogue.context_manager import ContextManager


class DialogueFlowTester:
    """Test suite for dialogue flows"""
    
    def __init__(self):
        self.dm = DialogueManager()
        self.total_tests = 0
        self.passed_tests = 0
    
    def assert_true(self, condition: bool, test_name: str):
        """Assert that condition is True"""
        self.total_tests += 1
        
        if condition:
            self.passed_tests += 1
            print(f"  ✅ {test_name}")
            return True
        else:
            print(f"  ❌ {test_name}")
            return False
    
    def assert_contains(self, text: str, substring: str, test_name: str):
        """Assert that text contains substring"""
        self.total_tests += 1
        
        if substring.lower() in text.lower():
            self.passed_tests += 1
            print(f"  ✅ {test_name}")
            return True
        else:
            print(f"  ❌ {test_name}")
            print(f"     Expected '{substring}' in '{text}'")
            return False
    
    def test_complete_transfer_flow(self):
        """Test complete money transfer flow"""
        print("\n💸 Test: Complete Money Transfer Flow")
        print("-" * 70)
        
        state = DialogueState(user_id=1, session_id="test_transfer_1")
        
        # User provides all information at once
        response, state = self.dm.process_turn(
            state,
            "Transfer PKR 5000 to Ali Khan from my savings account",
            "transfer_money",
            0.95,
            {'amount': 5000.0, 'payee': 'Ali Khan', 'account_number': 'PK12ABCD1234'}
        )
        
        self.assert_true(state.is_complete(), "All slots filled")
        self.assert_contains(response, "confirm", "Asks for confirmation")
        self.assert_true(state.confirmation_pending, "Confirmation is pending")
        
        # User confirms
        response, state = self.dm.process_turn(
            state,
            "yes",
            "",
            0.0,
            {}
        )
        
        self.assert_contains(response, "success", "Shows success message")
        self.assert_true(state.status == ConversationStatus.COMPLETED, "Status is completed")
    
    def test_multi_turn_transfer(self):
        """Test multi-turn transfer with missing information"""
        print("\n🔄 Test: Multi-turn Transfer")
        print("-" * 70)
        
        state = DialogueState(user_id=1, session_id="test_transfer_2")
        
        # Turn 1: User provides amount and payee only
        response, state = self.dm.process_turn(
            state,
            "Transfer 10000 to Sarah",
            "transfer_money",
            0.92,
            {'amount': 10000.0, 'payee': 'Sarah'}
        )
        
        self.assert_contains(response, "account", "Asks for missing account")
        self.assert_true(len(state.missing_slots) == 1, "One slot missing")
        
        # Turn 2: User provides account
        response, state = self.dm.process_turn(
            state,
            "Use account PK12ABCD1234567890123456",
            "transfer_money",
            0.90,
            {'account_number': 'PK12ABCD1234567890123456'}
        )
        
        self.assert_true(state.is_complete(), "All slots now filled")
        self.assert_contains(response, "confirm", "Asks for confirmation")
    
    def test_bill_payment_flow(self):
        """Test bill payment flow"""
        print("\n🧾 Test: Bill Payment Flow")
        print("-" * 70)
        
        state = DialogueState(user_id=1, session_id="test_bill_1")
        
        # User provides bill type only
        response, state = self.dm.process_turn(
            state,
            "Pay my electricity bill",
            "bill_payment",
            0.88,
            {'bill_type': 'electricity'}
        )
        
        self.assert_contains(response, "amount", "Asks for amount")
        self.assert_true('amount' in state.missing_slots, "Amount is missing")
        
        # User provides amount
        response, state = self.dm.process_turn(
            state,
            "3500 rupees",
            "bill_payment",
            0.85,
            {'amount': 3500.0}
        )
        
        self.assert_true(state.is_complete(), "All slots filled")
        self.assert_contains(response, "confirm", "Asks for confirmation")
    
    def test_check_balance_simple(self):
        """Test simple balance check"""
        print("\n💰 Test: Check Balance (Simple)")
        print("-" * 70)
        
        state = DialogueState(user_id=1, session_id="test_balance_1")
        
        # User checks balance with account
        response, state = self.dm.process_turn(
            state,
            "Check balance for PK12ABCD1234567890123456",
            "check_balance",
            0.97,
            {'account_number': 'PK12ABCD1234567890123456'}
        )
        
        self.assert_true(state.is_complete(), "All slots filled")
        self.assert_contains(response, "balance", "Shows balance")
    
    def test_context_resolution(self):
        """Test context-based entity resolution"""
        print("\n🔗 Test: Context Resolution")
        print("-" * 70)
        
        state = DialogueState(user_id=1, session_id="test_context_1")
        
        # First transfer
        response1, state = self.dm.process_turn(
            state,
            "Transfer 5000 to Ali",
            "transfer_money",
            0.93,
            {'amount': 5000.0, 'payee': 'Ali'}
        )
        
        # Provide account
        response2, state = self.dm.process_turn(
            state,
            "From account PK12ABCD1234567890123456",
            "transfer_money",
            0.90,
            {'account_number': 'PK12ABCD1234567890123456'}
        )
        
        # Confirm
        response3, state = self.dm.process_turn(
            state,
            "yes",
            "",
            0.0,
            {}
        )
        
        self.assert_true(state.status == ConversationStatus.COMPLETED, "First transfer completed")
        
        # New transfer with reference to previous amount
        state_new = DialogueState(user_id=1, session_id="test_context_2")
        state_new.context = state.context
        
        # This should resolve "same amount" from context
        response4, state_new = self.dm.process_turn(
            state_new,
            "Send the same amount to Sarah",
            "transfer_money",
            0.91,
            {'payee': 'Sarah'}
        )
        
        # The context manager should have the previous amount
        self.assert_true(
            self.dm.context_manager.has_context_for('amount'),
            "Amount exists in context"
        )
    
    def test_confirmation_yes(self):
        """Test confirmation - yes response"""
        print("\n✅ Test: Confirmation (Yes)")
        print("-" * 70)
        
        state = DialogueState(user_id=1, session_id="test_confirm_yes")
        
        # Set up pending confirmation
        state.set_intent("transfer_money", 0.95)
        state.set_required_slots(['amount', 'payee', 'source_account'])
        state.fill_slot('amount', 5000.0)
        state.fill_slot('payee', 'Ali')
        state.fill_slot('source_account', 'PK12ABCD1234')
        
        state.set_confirmation_pending({
            'intent': 'transfer_money',
            'slots': state.filled_slots.copy()
        })
        
        # User confirms
        response, state = self.dm.process_turn(
            state,
            "yes, proceed",
            "",
            0.0,
            {}
        )
        
        self.assert_contains(response, "success", "Shows success message")
        self.assert_true(state.status == ConversationStatus.COMPLETED, "Action completed")
    
    def test_confirmation_no(self):
        """Test confirmation - no response"""
        print("\n❌ Test: Confirmation (No)")
        print("-" * 70)
        
        state = DialogueState(user_id=1, session_id="test_confirm_no")
        
        # Set up pending confirmation
        state.set_intent("transfer_money", 0.95)
        state.set_required_slots(['amount', 'payee', 'source_account'])
        state.fill_slot('amount', 5000.0)
        state.fill_slot('payee', 'Ali')
        state.fill_slot('source_account', 'PK12ABCD1234')
        
        state.set_confirmation_pending({
            'intent': 'transfer_money',
            'slots': state.filled_slots.copy()
        })
        
        # User cancels
        response, state = self.dm.process_turn(
            state,
            "no, cancel that",
            "",
            0.0,
            {}
        )
        
        self.assert_contains(response, "cancel", "Shows cancellation message")
        self.assert_true(state.status == ConversationStatus.CANCELLED, "Action cancelled")
    
    def test_low_confidence_handling(self):
        """Test low confidence intent handling"""
        print("\n⚠️  Test: Low Confidence Handling")
        print("-" * 70)
        
        state = DialogueState(user_id=1, session_id="test_low_conf")
        
        # First low confidence
        response1, state = self.dm.process_turn(
            state,
            "I want to do something",
            "unknown",
            0.3,
            {}
        )
        
        self.assert_contains(response1, "understand", "Shows fallback response")
        
        # Second low confidence - should offer help
        response2, state = self.dm.process_turn(
            state,
            "Something with money",
            "unknown",
            0.25,
            {}
        )
        
        self.assert_contains(response2, "help", "Offers help menu")
    
    def test_slot_filling_order(self):
        """Test that slots are filled in order"""
        print("\n📋 Test: Slot Filling Order")
        print("-" * 70)
        
        state = DialogueState(user_id=1, session_id="test_order")
        
        # Set up transfer intent
        state.set_intent("transfer_money", 0.95)
        state.set_required_slots(['amount', 'payee', 'source_account'])
        
        # Fill amount first
        state.fill_slot('amount', 5000.0)
        
        self.assert_true('amount' not in state.missing_slots, "Amount filled")
        self.assert_true(len(state.missing_slots) == 2, "Two slots still missing")
        
        # Fill payee
        state.fill_slot('payee', 'Ali')
        
        self.assert_true('payee' not in state.missing_slots, "Payee filled")
        self.assert_true(len(state.missing_slots) == 1, "One slot still missing")
        
        # Fill account
        state.fill_slot('source_account', 'PK12ABCD1234')
        
        self.assert_true(state.is_complete(), "All slots filled")
        self.assert_true(len(state.missing_slots) == 0, "No missing slots")
    
    def run_all_tests(self):
        """Run all test suites"""
        print("=" * 70)
        print(" " * 15 + "DIALOGUE FLOW TEST SUITE")
        print("=" * 70)
        
        # Run all tests
        self.test_complete_transfer_flow()
        self.test_multi_turn_transfer()
        self.test_bill_payment_flow()
        self.test_check_balance_simple()
        self.test_context_resolution()
        self.test_confirmation_yes()
        self.test_confirmation_no()
        self.test_low_confidence_handling()
        self.test_slot_filling_order()
        
        # Print summary
        print("\n" + "=" * 70)
        print(" " * 25 + "TEST SUMMARY")
        print("=" * 70)
        
        accuracy = (self.passed_tests / self.total_tests * 100) if self.total_tests > 0 else 0
        
        print(f"\n  Total Tests:     {self.total_tests}")
        print(f"  Passed:          {self.passed_tests}")
        print(f"  Failed:          {self.total_tests - self.passed_tests}")
        print(f"  Success Rate:    {accuracy:.1f}%")
        
        success = accuracy >= 90.0
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"\n  Target:          90% success rate")
        print(f"  Status:          {status}")
        
        print("\n" + "=" * 70)
        
        return success


def main():
    """Run dialogue flow tests"""
    tester = DialogueFlowTester()
    success = tester.run_all_tests()
    
    if success:
        print("✅ All dialogue flow tests passed!")
        return 0
    else:
        print("⚠️  Some tests failed. Review and fix issues.")
        return 1


if __name__ == "__main__":
    exit(main())
