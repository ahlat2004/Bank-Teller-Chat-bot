"""
Phase 4 Tests: Enhanced Entity Extraction
Tests implicit amount handling, negation detection, and domain-aware patterns
"""

import pytest
import sys
import os

# Add paths for imports
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
app_dir = os.path.join(project_root, 'backend', 'app')
backend_dir = os.path.join(project_root, 'backend')

sys.path.insert(0, app_dir)
sys.path.insert(0, backend_dir)
sys.path.insert(0, project_root)

from app.core.enhanced_entity_extractor import (
    EnhancedBankingEntityExtractor,
    NegationScope,
    enhance_extraction_results
)


class TestImplicitAmountExtraction:
    """Test implicit amount extraction (Flaw #9)"""
    
    def setup_method(self):
        self.extractor = EnhancedBankingEntityExtractor()
    
    def test_extract_all_money(self):
        """Test 'send all my money' pattern"""
        result = self.extractor.extract_implicit_amounts("Send all my money to Ahmed")
        assert result == 'all'
    
    def test_extract_all_transfer(self):
        """Test 'transfer all' pattern"""
        result = self.extractor.extract_implicit_amounts("Transfer all from my account")
        assert result == 'all'
    
    def test_extract_remaining(self):
        """Test 'remaining' pattern"""
        result = self.extractor.extract_implicit_amounts("Send the remaining amount")
        assert result == 'remaining'
    
    def test_extract_everything(self):
        """Test 'everything' pattern"""
        result = self.extractor.extract_implicit_amounts("Transfer everything to savings")
        assert result == 'all'
    
    def test_extract_entire_balance(self):
        """Test 'entire balance' pattern"""
        result = self.extractor.extract_implicit_amounts("Send the entire balance")
        assert result == 'all'
    
    def test_extract_maximum(self):
        """Test 'max' pattern"""
        result = self.extractor.extract_implicit_amounts("Transfer max amount")
        assert result == 'max'
    
    def test_extract_half(self):
        """Test 'half' pattern"""
        result = self.extractor.extract_implicit_amounts("Send half of my balance")
        assert result == 'half'
    
    def test_no_implicit_amount(self):
        """Test message with explicit amount"""
        result = self.extractor.extract_implicit_amounts("Send 5000 to Ahmed")
        assert result is None
    
    def test_resolve_all_to_explicit(self):
        """Test converting 'all' to explicit amount"""
        amount = self.extractor.resolve_implicit_to_explicit('all', 10000)
        assert amount == 10000
    
    def test_resolve_half_to_explicit(self):
        """Test converting 'half' to explicit amount"""
        amount = self.extractor.resolve_implicit_to_explicit('half', 10000)
        assert amount == 5000


class TestNegationDetection:
    """Test negation detection (Flaw #10)"""
    
    def setup_method(self):
        self.extractor = EnhancedBankingEntityExtractor()
    
    def test_detect_dont_use_savings(self):
        """Test 'don't use savings' negation"""
        has_neg, scope, entity = self.extractor.detect_negation("Send money, don't use savings")
        assert has_neg is True
        assert scope == NegationScope.ACCOUNT_TYPE
        assert entity == 'savings'
    
    def test_detect_not_from_checking(self):
        """Test 'not from checking' negation"""
        has_neg, scope, entity = self.extractor.detect_negation("Transfer, not from checking account")
        assert has_neg is True
        assert scope == NegationScope.ACCOUNT_TYPE
        assert entity == 'checking'
    
    def test_detect_exclude_account(self):
        """Test 'exclude' negation"""
        has_neg, scope, entity = self.extractor.detect_negation("Exclude salary account")
        assert has_neg is True
        assert scope == NegationScope.ACCOUNT_TYPE
        assert entity == 'salary'
    
    def test_no_negation(self):
        """Test message without negation"""
        has_neg, scope, entity = self.extractor.detect_negation("Send 5000 to Ahmed")
        assert has_neg is False
        assert scope is None
        assert entity is None
    
    def test_explain_negation(self):
        """Test negation explanation"""
        explanation = self.extractor.explain_negation({
            'present': True,
            'scope': 'account_type',
            'entity': 'savings'
        })
        assert 'savings' in explanation.lower()
    
    def test_validate_negation_for_transfer(self):
        """Test negation validation for transfer intent"""
        negation = {'present': True, 'scope': 'account_type', 'entity': 'savings'}
        is_valid, msg = self.extractor.validate_negation_compatibility('transfer_money', negation)
        assert is_valid is True
    
    def test_validate_negation_for_account_creation(self):
        """Test negation validation for create_account intent"""
        negation = {'present': True, 'scope': 'account_type', 'entity': 'savings'}
        is_valid, msg = self.extractor.validate_negation_compatibility('create_account', negation)
        assert is_valid is False


class TestAccountTypeInference:
    """Test account type inference"""
    
    def setup_method(self):
        self.extractor = EnhancedBankingEntityExtractor()
    
    def test_infer_salary_account(self):
        """Test 'salary account' inference"""
        result = self.extractor.infer_account_type("Send from my salary account")
        assert result == 'salary'
    
    def test_infer_savings_account(self):
        """Test 'savings' inference"""
        result = self.extractor.infer_account_type("Use my savings")
        assert result == 'savings'
    
    def test_infer_current_account(self):
        """Test 'current account' inference"""
        result = self.extractor.infer_account_type("Pay from current account")
        assert result == 'current'
    
    def test_infer_checking_account(self):
        """Test 'checking' inference (synonym for current)"""
        result = self.extractor.infer_account_type("From my checking")
        assert result == 'current'
    
    def test_no_account_type_mentioned(self):
        """Test message without account type"""
        result = self.extractor.infer_account_type("Send 5000 to Ahmed")
        assert result is None


class TestBillerInference:
    """Test biller type inference for bill payments"""
    
    def setup_method(self):
        self.extractor = EnhancedBankingEntityExtractor()
    
    def test_infer_electricity_biller(self):
        """Test electricity biller inference"""
        result = self.extractor.infer_biller("Pay my electric bill")
        assert result == 'electricity'
    
    def test_infer_water_biller(self):
        """Test water biller inference"""
        result = self.extractor.infer_biller("Pay water bill")
        assert result == 'water'
    
    def test_infer_phone_biller(self):
        """Test phone biller inference"""
        result = self.extractor.infer_biller("Pay my mobile bill")
        assert result == 'phone'
    
    def test_infer_internet_biller(self):
        """Test internet biller inference"""
        result = self.extractor.infer_biller("Pay internet bill")
        assert result == 'internet'
    
    def test_infer_education_biller(self):
        """Test education/tuition biller inference"""
        result = self.extractor.infer_biller("Pay school fees")
        assert result == 'education'
    
    def test_no_biller_mentioned(self):
        """Test message without biller"""
        result = self.extractor.infer_biller("Make a payment")
        assert result is None


class TestContextAwareExtraction:
    """Test context-aware entity extraction"""
    
    def setup_method(self):
        self.extractor = EnhancedBankingEntityExtractor()
    
    def test_extract_for_transfer_intent(self):
        """Test extraction with transfer intent context"""
        entities = self.extractor.extract_context_aware_entities(
            "Send all from savings",
            intent='transfer_money'
        )
        assert 'implicit_amount' in entities
        assert entities['implicit_amount'] == 'all'
        assert 'account_type' in entities
        assert entities['account_type'] == 'savings'
    
    def test_extract_for_bill_payment(self):
        """Test extraction with bill_payment intent context"""
        entities = self.extractor.extract_context_aware_entities(
            "Pay electricity bill from savings",
            intent='bill_payment'
        )
        assert 'biller' in entities
        assert entities['biller'] == 'electricity'
        assert 'account_type' in entities
    
    def test_extract_with_negation_context(self):
        """Test extraction with negation in context"""
        entities = self.extractor.extract_context_aware_entities(
            "Don't use salary account to send money",
            intent='transfer_money'
        )
        assert 'negation' in entities
        assert entities['negation']['present'] is True
    
    def test_complex_message_extraction(self):
        """Test complex message with multiple entities"""
        entities = self.extractor.extract_context_aware_entities(
            "Send all from savings, don't use salary account",
            intent='transfer_money'
        )
        assert 'implicit_amount' in entities
        assert 'account_type' in entities
        assert 'negation' in entities


class TestAmountWithNegation:
    """Test amount extraction with negation handling"""
    
    def setup_method(self):
        self.extractor = EnhancedBankingEntityExtractor()
    
    def test_amount_with_negation(self):
        """Test amount extraction when negation is present"""
        result = self.extractor.extract_amount_with_negation(
            "Don't send all, not from salary"
        )
        assert result['has_negation'] is True
        assert result['implicit_amount'] == 'all'
    
    def test_implicit_amount_no_negation(self):
        """Test implicit amount without negation"""
        result = self.extractor.extract_amount_with_negation(
            "Send all my money"
        )
        assert result['implicit_amount'] == 'all'
        assert result['has_negation'] is False


class TestEnhanceExtractionResults:
    """Test integration helper function"""
    
    def test_enhance_base_extraction(self):
        """Test merging base and enhanced extraction"""
        base = {'phone': '03001234567'}
        result = enhance_extraction_results(
            base,
            "Send all from savings to Ahmed"
        )
        assert 'phone' in result
        assert 'implicit_amount' in result
        assert 'account_type' in result
    
    def test_enhanced_overrides_base(self):
        """Test that enhanced extraction takes precedence"""
        base = {'account_type': 'current'}
        result = enhance_extraction_results(
            base,
            "Use savings account"
        )
        # Enhanced should override
        assert result['account_type'] == 'savings'


class TestIntegrationWithState:
    """Test integration with state machine context"""
    
    def setup_method(self):
        self.extractor = EnhancedBankingEntityExtractor()
    
    def test_negation_resolves_account_ambiguity(self):
        """Test negation resolves which account to use"""
        # User says "don't use savings" for transfer
        # System should use other account (salary or current)
        has_neg, scope, entity = self.extractor.detect_negation(
            "Transfer to Ahmed, don't use savings"
        )
        assert has_neg is True
        assert entity == 'savings'
        
        # System can now exclude savings from account selection
        is_valid, msg = self.extractor.validate_negation_compatibility('transfer_money', {
            'present': True,
            'scope': 'account_type',
            'entity': entity
        })
        assert is_valid is True
    
    def test_implicit_amount_with_account_selection(self):
        """Test implicit amount works with account type"""
        entities = self.extractor.extract_context_aware_entities(
            "Send all my savings to Ahmed"
        )
        assert entities['implicit_amount'] == 'all'
        assert entities['account_type'] == 'savings'
        
        # System can now: use 'all' from 'savings' account
        amount = self.extractor.resolve_implicit_to_explicit('all', 5000)
        assert amount == 5000


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
