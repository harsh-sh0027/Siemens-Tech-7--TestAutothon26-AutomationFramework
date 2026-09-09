"""Excel-backed challenge data loader for the Gajab workflow."""

from dataclasses import dataclass
from pathlib import Path

from openpyxl import load_workbook

from src.utils.config import ConfigLoader


@dataclass(frozen=True)
class ChallengeData:
    """Typed access to workflow inputs and expected artifacts."""

    mobile_number: str
    otp: str
    pin: str
    language: str
    category: str
    brand: str
    min_price: int
    max_price: int
    product_name: str
    payment_method: str
    bank_name: str
    email_recipient: str


class ChallengeDataLoader:
    """Read workflow data from the challenge Excel workbook."""

    @staticmethod
    def load(sheet_name: str = 'challenge1') -> ChallengeData:
        """Load challenge data from Excel, with env overrides for sensitive values."""
        workbook_path = Path(ConfigLoader.challenge_data_path())
        workbook = load_workbook(workbook_path, data_only=True)
        if sheet_name not in workbook.sheetnames:
            raise ValueError(f"Worksheet '{sheet_name}' not found in {workbook_path}")

        sheet = workbook[sheet_name]
        values = {}
        for key_cell, value_cell in sheet.iter_rows(min_row=2, max_col=2, values_only=True):
            if key_cell:
                values[str(key_cell).strip()] = value_cell

        return ChallengeData(
            mobile_number=str(values.get('mobile_number', ConfigLoader.test_mobile())),
            otp=str(values.get('otp', ConfigLoader.test_otp())),
            pin=str(values.get('pin', ConfigLoader.test_pin())),
            language=str(values.get('language', ConfigLoader.challenge_language())).strip().lower(),
            category=str(values.get('category', 'Toys & Games')),
            brand=str(values.get('brand', "SERA'S BASKET")),
            min_price=int(values.get('min_price', 427)),
            max_price=int(values.get('max_price', 727)),
            product_name=str(values.get('product_name', 'Classic 15.7 Inch Soft Tip Dartboard Game Set')),
            payment_method=str(values.get('payment_method', 'Pay Online')),
            bank_name=str(values.get('bank_name', 'Any Bank')),
            email_recipient=str(values.get('email_recipient', ConfigLoader.results_email())),
        )