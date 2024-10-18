import unittest
from unittest.mock import Mock
from verification.verification_processor.content_alignment import verify_messages
from verification.verification_processor.models import SettlementRequest

class TestVerifyMessages(unittest.TestCase):

    def setUp(self):
        # Create a mock SettlementRequest
        self.request = Mock(spec=SettlementRequest)
        self.request.bank_account_number = "123456789"
        self.request.bank_account_name = "JohnDoe"
        self.request.amount = "THB700000"
        self.request.bank_name = "ABCBank"

    def test_all_fields_match(self):
        # Test case where all fields match exactly
        ga_message = """
        Account Number: 123456789
        Account Name: John Doe
        Amount :  THB 700,000
        Bank: ABC Bank
        """
        result, index = verify_messages(ga_message, self.request)
        self.assertTrue(result)
        self.assertEqual(index, 0)  # All should match starting from line 0

    def test_partial_match(self):
        # Test case where only some fields match
        ga_message = """
        Account Number: 123456789
        Account Name: Jane Doe
        Amount :  THB 700,000
        Bank: XYZ Bank
        """
        result, index = verify_messages(ga_message, self.request)
        self.assertFalse(result)  # Mismatch in account name and bank name

    def test_no_match(self):
        # Test case where no fields match
        ga_message = """
        Account Number: 987654321
        Account Name: Jane Smith
        Amount :  THB 100,000
        Bank: XYZ Bank
        """
        result, index = verify_messages(ga_message, self.request)
        self.assertFalse(result)

    def test_mixed_characters_match(self):
        # Test case with different characters/spacing but valid data
        ga_message = """
        Account No.: 123-456-  789
        Account Name :  John    Doe
        Amount : THB700,000
        Bank Name: ABC-Bank
        """
        result, index = verify_messages(ga_message, self.request)
        self.assertTrue(result)

    def test_out_of_order_match(self):
        # Test case where fields are out of order but should still match
        ga_message = """
        Bank: ABC Bank
        Account Name: John Doe
        Account Number: 123456789
        Amount: THB 700,000
        """
        result, index = verify_messages(ga_message, self.request)
        self.assertTrue(result)
        
    def test_long_message(self):
        ga_message = """
        Bank: ABC Bank
        Account Name: John Doe
        Account Number: 123456789
        Amount: THB 700,0000
        
        Bank: ABC Bank
        Account Name: John Doe
        Account Number: 123456789
        Amount: THB 700,0000
        
        
        Bank: ABC Bank
        Account Name: John Doe
        Account Number: 123456789
        Amount: THB 700,000
        """
        
        result, index = verify_messages(ga_message, self.request)
        self.assertTrue(result)
        self.assertEqual(index, 8)
    
    def test_no_match_long_message(self):
        
        ga_message = """
        Bank: ABC Bank
        Account Name: John Doee
        Account Number: 123456789
        Amount: THB 700,0000
        
        Bank: ABC Bankk
        Account Name: John Doe
        Account Number: 123456789
        Amount: THB 700,0000
        
        
        Bank: ABC Bank
        Account NameJohn Doe
        Account Number: 123456789
        Amount: THB 700,000
        """
        
        result, index = verify_messages(ga_message, self.request)
        self.assertFalse(result)
        self.assertEqual(index, 8)

if __name__ == "__main__":
    unittest.main()
