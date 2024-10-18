import unittest


from verification.verification_processor.check_similarity import SettlementRequest, approximate_match

class TestApproximateMatch(unittest.TestCase):
    def setUp(self):
        self.request = SettlementRequest(
            merchant_name="ABCStore",
            amount="100.00",
            bank_name="XYZBank",
            bank_account_name="Account Holder",
            bank_account_number="673-724-7715"
        )

    def test_exact_match(self):
        search_text = "Merchant Name: ABCStore, Amount: 100.00, Bank: XYZBank"
        self.assertTrue(approximate_match(search_text, self.request, threshold=80))

    def test_partial_match(self):
        search_text = "Merchant Name: ABC Store, Amount: 100.00, Bank: XYZ Bank"
        self.assertTrue(approximate_match(search_text, self.request, threshold=80))

    def test_not_enough_matches(self):
        search_text = "Merchant Name: Unknown Store, Amount: 50"
        self.assertFalse(approximate_match(search_text, self.request, threshold=80))

    def test_special_characters(self):
        search_text = "Merchant Name: ABCStore, Amount: 100.00$"
        self.assertFalse(approximate_match(search_text, self.request, threshold=80))

    def test_case_insensitivity(self):
        search_text = "merchant name: abCstore, Amount: 100.00, bank: xyzbank"
        self.assertTrue(approximate_match(search_text, self.request, threshold=80))

    def test_too_spaces(self):
        search_text = "Merchant Name: A B C Store, Amount: 100.00, bank: XYZ Bank"
        self.assertFalse(approximate_match(search_text, self.request, threshold=80))

    def test_empty_fields(self):
        empty_request = SettlementRequest()
        search_text = "Merchant Name: random"
        self.assertFalse(approximate_match(search_text, empty_request, threshold=80))

    def test_more_than_three_matches(self):
        search_text = """
        Merchant Name: ABCStore
        Amount: 100.00
        Bank: XYZBank
        Account Holder: Account Holder
        Account Number: 673-724-7715
        """
        self.assertTrue(approximate_match(search_text, self.request, threshold=80))

if __name__ == "__main__":
    unittest.main()
