import unittest
from verification.verification_processor.content_alignment import check_strict_ends_with

class TestCheckStrictEndsWith(unittest.TestCase):
    
    def test_exact_match(self):
        # Test exact match
        self.assertTrue(check_strict_ends_with("THB 700000", "THB700000"))
    
    def test_match_with_special_characters(self):
        # Test with special characters in string_a
        self.assertTrue(check_strict_ends_with("Amount: THB 700,000", "THB700000"))
        self.assertTrue(check_strict_ends_with("Amount - THB 700,000", "THB700000"))
    
    def test_no_match(self):
        # Test cases where string_b doesn't match string_a
        self.assertFalse(check_strict_ends_with("Amount: THB 600,000", "THB700000"))
        self.assertFalse(check_strict_ends_with("Amount: USD 700,000", "THB700000"))
    
    def test_match_with_delimiters(self):
        # Test string_a ends with delimiters, but the rest matches
        self.assertTrue(check_strict_ends_with("Amount: THB 700,000", "THB700000"))
        self.assertTrue(check_strict_ends_with("Amount : THB 700,000", "THB700000"))
    
    def test_length_mismatch(self):
        # Test case where string_a is shorter than string_b
        self.assertFalse(check_strict_ends_with("THB 700", "THB700000"))
        
        
    
    def test_empty_string_b(self):
        # Test case where string_b is empty
        self.assertFalse(check_strict_ends_with("THB 700,000", ""))

    def test_empty_string_a(self):
        # Test case where string_a is empty
        self.assertFalse(check_strict_ends_with("", "THB700000"))
        
    def test_new_line(self):
        # Test case where string_a is empty
        self.assertFalse(check_strict_ends_with("THB 700,0\n00", "THB700000"))
        
        
        self.assertTrue(check_strict_ends_with("Bank account number :  tbh 735731-688-94", "tbh73573168894"))
        self.assertTrue(check_strict_ends_with("Bank account name :  ชนาพร ดวงดารา", "ชนาพรดวงดารา"))

if __name__ == '__main__':
    unittest.main()
