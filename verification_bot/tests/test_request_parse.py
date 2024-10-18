import unittest
from verification.verification_processor.parse_request import (
    contains_settlement_request,
    get_bank_account_number_from_request,
    get_bank_name_from_request,
    get_amount_from_request,
    get_bank_account_name_from_request,
    get_merchant_name_from_request,
    get_settlement_request_model,
    flexible_string_search
)

class TestSettlementRequestParsing(unittest.TestCase):

    def test_contains_settlement_request(self):
        # Positive case
        self.assertTrue(contains_settlement_request("Settlement Request:\nAmount: $500"))
        self.assertTrue(contains_settlement_request("SETTLEMENT REQUEST\nBank: XYZ"))
        
        # Negative case
        self.assertFalse(contains_settlement_request("Request for money\nAmount: $500"))
        self.assertFalse(contains_settlement_request("This is not a settlement"))

    def test_get_bank_account_number_from_request(self):
        message = "Bank account number: 123-456-789"
        self.assertEqual(get_bank_account_number_from_request(message), "123456789")
        
        message = "account number: 987-654-321"
        self.assertEqual(get_bank_account_number_from_request(message), "987654321")
        
        message = "No account number here"
        self.assertEqual(get_bank_account_number_from_request(message), "")

    def test_get_bank_name_from_request(self):
        message = "Bank: National Bank"
        self.assertEqual(get_bank_name_from_request(message), "NationalBank")
        
        message = "bank name: Standard Chartered"
        self.assertEqual(get_bank_name_from_request(message), "StandardChartered")
        
        # message = "No bank mentioned"
        # self.assertEqual(get_bank_name_from_request(message), "")

    def test_get_amount_from_request(self):
        message = "Amount: USD 1,000.00"
        self.assertEqual(get_amount_from_request(message), "USD1000.00")
        
        message = "balance: 500"
        self.assertEqual(get_amount_from_request(message), "500")
        
        # message = "No amount mentioned"
        # self.assertEqual(get_amount_from_request(message), "")

    def test_get_bank_account_name_from_request(self):
        message = "Account name: John Doe"
        self.assertEqual(get_bank_account_name_from_request(message), "JohnDoe")
        
        message = "bank-account-name: Jane Smith"
        self.assertEqual(get_bank_account_name_from_request(message), "JaneSmith")
        
        # message = "No account name provided"
        # self.assertEqual(get_bank_account_name_from_request(message), "")

    def test_get_merchant_name_from_request(self):
        message = "Merchant name: ABC Stores"
        self.assertEqual(get_merchant_name_from_request(message), "ABCStores")
        
        message = "merchant-name: XYZ Corp"
        self.assertEqual(get_merchant_name_from_request(message), "XYZCorp")
        
        # message = "No merchant name"
        # self.assertEqual(get_merchant_name_from_request(message), "")

    def test_flexible_string_search(self):
        haystack = "This is an example bank account number: 123-456-789."
        needle = "123456789"
        self.assertTrue(flexible_string_search(haystack, needle))
        
        haystack = "Account: ABC-1234"
        needle = "ABC1234"
        self.assertTrue(flexible_string_search(haystack, needle))
        
        haystack = "No match here"
        needle = "98765"
        self.assertFalse(flexible_string_search(haystack, needle))

    def test_get_settlement_request_model(self):
        message = """
        Settlement Request:
        Merchant Name: XYZ Company
        Amount: USD 1000.00
        Bank: Chase Bank
        Bank Account Name: John Doe
        Bank Account Number: 123-456-789
        """
        request = get_settlement_request_model(message)
        
        self.assertEqual(request.merchant_name, "XYZCompany")
        self.assertEqual(request.amount, "USD1000.00")
        self.assertEqual(request.bank_name, "ChaseBank")
        self.assertEqual(request.bank_account_name, "JohnDoe")
        self.assertEqual(request.bank_account_number, "123456789")


if __name__ == '__main__':
    unittest.main()
