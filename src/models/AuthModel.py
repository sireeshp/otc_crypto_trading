from datetime import date, datetime
from typing import Annotated, List, Literal, Optional, Union

from pydantic import BaseModel, EmailStr, Field, HttpUrl, field_validator

from src.models.FeesModel import Fees

# Define PhoneNumberStr using the E.164 phone number format
PhoneNumberStr = Annotated[
    str,
    Field(pattern=r"^\+?[1-9]\d{1,14}$", description="Phone number in E.164 format"),
]  # E.164 phone format


class TwoFactorRequest(BaseModel):
    user_id: str
    method: Optional[Literal["sms", "authenticator", "email"]] = Field(
        default="sms",
        description="The method for two-factor authentication. Options: 'sms', 'authenticator', or 'email'.",
    )


class LoginModel(BaseModel):
    # userName can be an email or a phone number
    user_name: Union[EmailStr, PhoneNumberStr]
    password: str

    # Validator to strip whitespaces and convert email/username to lowercase
    @field_validator("user_name", mode="before")
    def normalize_user_name(cls, value):
        return (value.strip().lower()) if isinstance(value, str) else value

    # Validator to strip whitespaces from password
    @field_validator("password", mode="before")
    def strip_password_whitespace(cls, value):
        return value.strip()


class SendOtpModel(BaseModel):
    user_name: Union[EmailStr, PhoneNumberStr]


class VerifyOtpModel(BaseModel):
    # userName can be an email or a phone number
    user_name: Union[EmailStr, PhoneNumberStr]
    code: str

    # Validator to strip whitespaces and convert email/username to lowercase
    @field_validator("user_name", mode="before")
    def normalize_user_name(cls, value):
        return (value.strip().lower()) if isinstance(value, str) else value


# Define Crypto Wallet Model
class CryptoWallet(BaseModel):
    wallet_address: str
    wallet_type: str = Field(
        ..., description="Type of wallet (e.g., hot, cold, exchange)"
    )
    balance: float = Field(..., description="Current balance in the wallet")
    currency: str = Field(..., description="Currency type (e.g., BTC, ETH, USDT)")


# Define Transaction Model
class Transaction(BaseModel):
    transaction_id: str
    transaction_type: str = Field(
        ..., description="Transaction type (e.g., buy, sell, deposit, withdrawal)"
    )
    transaction_amount: float = Field(
        ..., description="Amount involved in the transaction"
    )
    currency: str = Field(..., description="Currency for the transaction")
    transaction_date: datetime
    status: str = Field(
        ..., description="Status of the transaction (e.g., pending, completed, failed)"
    )


# Define Address Model
class Address(BaseModel):
    street: str
    city: str
    state: str
    postal_code: str
    country: str


# Define KYC Document Model
class KycDocument(BaseModel):
    document_type: Literal[
        "passport", "driver_license", "national_id", "business_license"
    ]
    document_number: str = Field(..., description="Document number")
    issue_date: Optional[date] = Field(None, description="Date of issue")
    expiry_date: Optional[date] = Field(None, description="Date of expiry")
    country_of_issue: Optional[str]
    document_url: Optional[HttpUrl] = Field(
        ..., description="URL to the document image or file"
    )


# Define KYC Data Model
class KycData(BaseModel):
    first_name: str
    last_name: str
    date_of_birth: date
    nationality: str
    government_id_type: str = Field(
        ..., description="Type of government-issued ID (e.g., Passport, National ID)"
    )
    government_id_number: str = Field(..., description="Government-issued ID number")
    tax_id: Optional[str] = Field(
        None, description="Optional Tax Identification Number"
    )
    residential_address: Address
    documents: List[KycDocument] = Field(
        ..., description="List of uploaded KYC documents"
    )
    kyc_status: str = Field(
        ..., description="KYC approval status (e.g., pending, approved, rejected)"
    )
    aml_status: str = Field(..., description="AML compliance status")
    kyc_review_date: Optional[date] = Field(
        None, description="Date of the last KYC review"
    )
    aml_review_date: Optional[date] = Field(
        None, description="Date of the last AML review"
    )


# Define Legal Compliance Model
class LegalCompliance(BaseModel):
    terms_agreed_date: datetime = Field(
        ..., description="Date when the user agreed to the terms"
    )
    ip_address: str = Field(
        ..., description="IP address from where the terms were agreed"
    )
    last_login_ip: Optional[str] = Field(
        None, description="Last login IP address of the user"
    )
    consent_to_marketing: bool = Field(
        ..., description="Has the user consented to marketing emails?"
    )
    terms_version: str = Field(
        ..., description="Version of the terms and conditions the user agreed to"
    )
    accepted_privacy_policy: bool = Field(
        ..., description="Has the user accepted the privacy policy?"
    )
    gdpr_compliance: bool = Field(..., description="Has the user agreed to GDPR terms?")
    aml_compliance: bool = Field(..., description="Is the user AML compliant?")


class Role(BaseModel):
    role_name: Literal["admin", "trader", "compliance_officer", "analyst", "manager"]
    permissions: List[str]


# Define User Model
class User(BaseModel):
    id: Optional[str] = Field(default=None)
    name: str
    email: EmailStr
    phone_number: PhoneNumberStr
    user_type: Optional[
        Literal["individual", "business_entity", "financial_institution"]
    ] = Field(default=["individual"], description="Type of the user")
    password: str = Field(
        ...,
        description="Password must be at least 8 characters long, with at least 1 capital letter and 1 special character",
        min_length=8,
    )
    # Legal compliance
    legal_compliance: LegalCompliance = Field(
        ..., description="Legal compliance information for the user"
    )
    about: Optional[str] = None
    avatar_url: Optional[HttpUrl] = None
    # KYC data
    kyc_data: Optional[KycData] = Field(None, description="KYC data for the user")

    # Crypto wallets
    crypto_wallets: Optional[List[CryptoWallet]] = Field(
        default=[], description="List of associated cryptocurrency wallets"
    )

    # Transaction history
    transaction_history: Optional[List[Transaction]] = Field(
        default=[], description="User transaction history"
    )

    # User tier and trading limits
    user_tier: Optional[Literal["basic", "pro", "vip"]] = Field(
        default="basic",
        description="Account tier (e.g., basic, pro, VIP)",
    )
    trading_limits: Optional[float] = Field(
        default=0.0, description="User's trading limits"
    )
    fees: Optional[Fees] = Field(None, description="Fees associated with the user")
    # Security settings
    two_factor_enabled: bool = Field(default=False, description="Is 2FA enabled?")
    two_factor_method: Optional[str] = Field(
        default=None, description="2FA method (sms, authenticator, email)"
    )
    login_attempts: Optional[int] = Field(
        default=0, description="Number of failed login attempts"
    )
    last_login: Optional[datetime] = Field(
        None, description="Date and time of the last login"
    )

    ai_trading_enabled: bool = Field(
        default=False, description="Is AI/Algo trading enabled for the user?"
    )
    trading_products: List[
        Literal["crypto", "forex", "stocks", "commodities", "otc"]
    ] = Field(default=["crypto"], description="Trading products allowed for the user")

    roles: Optional[List["Role"]] = Field(
        default=[], description="Roles assigned to the user"
    )
    data_store_preference: Literal["private_server", "blockchain", "internal"] = Field(
        default=["internal"], description="User's preferred data storage option"
    )

    @field_validator("email", mode="before")
    def normalize_email(cls, value):
        return value.strip().lower()

    @field_validator("password", mode="before")
    def strip_password_whitespace(cls, value):
        return value.strip() or ValueError("Password cannot be empty or whitespace.")

    @field_validator("password")
    def validate_password(cls, value):
        if not any(char.isupper() for char in value):
            raise ValueError("Password must contain at least 1 capital letter")
        if all(char not in '!@#$%^&*(),.?":{}|<>' for char in value):
            raise ValueError("Password must contain at least 1 special character")
        return value
