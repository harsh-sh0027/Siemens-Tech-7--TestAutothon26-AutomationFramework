"""Excel-backed challenge data loader for the Gajab workflow."""

from dataclasses import dataclass
from pathlib import Path
from typing import List

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


@dataclass(frozen=True)
class NegativeLoginData:
    """Negative dataset row for authentication scenarios."""

    case_name: str
    mobile_number: str
    otp: str
    expected_error_hint: str


class ChallengeDataLoader:
    """Read workflow data from the challenge Excel workbook."""

    @staticmethod
    def _default_challenge_data() -> ChallengeData:
        """Return safe defaults when workbook or sheet is not available."""
        return ChallengeData(
            mobile_number=ConfigLoader.test_mobile(),
            otp=ConfigLoader.test_otp(),
            pin=ConfigLoader.test_pin(),
            language=ConfigLoader.challenge_language(),
            category='Toys & Games',
            brand="SERA'S BASKET",
            min_price=427,
            max_price=727,
            product_name='Classic 15.7 Inch Soft Tip Dartboard Game Set',
            payment_method='Pay Online',
            bank_name='Any Bank',
            email_recipient=ConfigLoader.results_email(),
        )

    @staticmethod
    def load(sheet_name: str = 'challenge1') -> ChallengeData:
        """Load challenge data from Excel, with env overrides for sensitive values."""
        workbook_path = Path(ConfigLoader.challenge_data_path())
        if not workbook_path.exists():
            return ChallengeDataLoader._default_challenge_data()

        workbook = load_workbook(workbook_path, data_only=True)
        if sheet_name not in workbook.sheetnames:
            return ChallengeDataLoader._default_challenge_data()

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

    @staticmethod
    def load_negative_login_cases(sheet_name: str = 'negative_login') -> List[NegativeLoginData]:
        """Load negative login cases from workbook, with built-in fallback case."""
        workbook_path = Path(ConfigLoader.challenge_data_path())
        if not workbook_path.exists():
            return [
                NegativeLoginData(
                    case_name='invalid_otp_default',
                    mobile_number=ConfigLoader.test_mobile(),
                    otp='000000',
                    expected_error_hint='invalid otp',
                )
            ]

        workbook = load_workbook(workbook_path, data_only=True)
        if sheet_name not in workbook.sheetnames:
            return [
                NegativeLoginData(
                    case_name='invalid_otp_default',
                    mobile_number=ConfigLoader.test_mobile(),
                    otp='000000',
                    expected_error_hint='invalid otp',
                )
            ]

        sheet = workbook[sheet_name]
        rows: List[NegativeLoginData] = []
        for row in sheet.iter_rows(min_row=2, values_only=True):
            case_name = str(row[0] or '').strip()
            mobile = str(row[1] or ConfigLoader.test_mobile()).strip()
            otp = str(row[2] or '000000').strip()
            hint = str(row[3] or 'invalid otp').strip().lower()
            if not case_name:
                continue
            rows.append(
                NegativeLoginData(
                    case_name=case_name,
                    mobile_number=mobile,
                    otp=otp,
                    expected_error_hint=hint,
                )
            )

        if not rows:
            rows.append(
                NegativeLoginData(
                    case_name='invalid_otp_default',
                    mobile_number=ConfigLoader.test_mobile(),
                    otp='000000',
                    expected_error_hint='invalid otp',
                )
            )
        return rows