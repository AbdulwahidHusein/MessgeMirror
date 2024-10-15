"""
sample message: Merchant name M98

Amount :  THB 360,000
Bank :   SCB
Bank account name :   Daka Run
Bank account number :    860-231526-5
"""

def handle(message: dict, source_group_id: int) -> str:
    return "verified"