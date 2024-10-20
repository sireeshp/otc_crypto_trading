from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Request, status

from src.models.AuthModel import (
    LoginModel,
    VerifyOtpModel,
    SendOtpModel,
    User,
    Transaction,
    CryptoWallet,
    KycData,
    TwoFactorRequest,
)
from src.models.EmailModel import EmailModel
from src.services.auth_service import (
    authenticate_email,
    authenticate_otp,
    send_otp,
    add_user,
    enable_two_factor,
    disable_two_factor,
    get_user_by_id,
    update_kyc_data,
    add_transaction,
    add_crypto_wallet,
)
from src.services.email_service import send_email
from src.utils.config import Config
from src.utils.mongo_utils import get_db

router = APIRouter()


@router.post("/register", status_code=status.HTTP_200_OK)
async def register(
    request: Request,
    user: User,
    background_tasks: BackgroundTasks,
    db=Depends(get_db),
):
    try:
        await add_user(user, db=db)
        send_register_email(request, background_tasks, user)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.post("/login", status_code=status.HTTP_200_OK)
async def login(
    request: Request,
    login_model: LoginModel,
    background_tasks: BackgroundTasks,
    db=Depends(get_db),
):
    """
    Handles user login by authenticating either via email and password or OTP.

    This asynchronous function processes login requests,
    validating the provided credentials and determining
    the authentication method based on the format of the username.
    If successful, it sends a login email and returns the user information.

    Args:
        request (Request): The HTTP request object.
        login_model (LoginModel): The model containing user login details.
        background_tasks (BackgroundTasks): Background tasks to be executed after the response is sent.
        db: The database dependency for user authentication.

    Returns:
        User: The authenticated user object.

    Raises:
        HTTPException: If the username or password is missing,
        or if an error occurs during authentication.
    """

    try:
        if login_model.user_name is None:
            raise HTTPException(status_code=400, detail="User name is required")

        is_email = "@" in login_model.user_name
        if login_model.password is None:
            error_message = "Password is required" if is_email else "OTP is required"
            raise HTTPException(status_code=400, detail=error_message)

        if is_email:
            user = await authenticate_email(
                login_model.user_name, login_model.password, db
            )
        else:
            user = await authenticate_otp(
                login_model.user_name, login_model.password, db
            )
        send_login_email(request, background_tasks, user)
        return user
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.post("/verify_otp", status_code=status.HTTP_200_OK)
async def verify_otp(verify_otp_model: VerifyOtpModel, db=Depends(get_db)):
    """
    Verifies a One-Time Password (OTP) provided by the user for authentication.

    This asynchronous function checks if the user's contact information
    and OTP code are provided, and then attempts to authenticate
    the user using the provided credentials. It raises errors if the required information
    is missing and returns the result of the authentication process.

    Args:
        verify_otp_model (VerifyOtpModel): The model containing
        the user's contact information and OTP code.
        db: The database dependency for user authentication.

    Returns:
        User: The authenticated user object if
        the OTP verification is successful.

    Raises:
        HTTPException: If the user name or OTP code is not provided,
        or if an error occurs during the authentication process.
    """

    try:
        if verify_otp_model.user_name is None:
            raise HTTPException(
                status_code=400, detail="Email or Phone number is required"
            )

        if verify_otp_model.code is None:
            raise HTTPException(status_code=400, detail="OTP is required")
        return await authenticate_otp(verify_otp_model.user_name, verify_otp_model.code, db)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.post("/send-otp", status_code=status.HTTP_200_OK)
async def send_otp(send_otp_model: SendOtpModel, db=Depends(get_db)):
    """
    Initiates the process of sending a One-Time Password (OTP) to the user.

    This asynchronous function validates the user's contact
    information and calls the OTP sending function if the information
    is provided. It ensures that either an email or
    phone number is specified, returning an error if not.

    Args:
        send_otp_model (SendOtpModel): The model containing the user's contact information.
        db: The database dependency for managing user data.

    Returns:
        dict: The result of the OTP sending process.

    Raises:
        HTTPException: If the user name is not provided or if an error occurs during the OTP sending process.
    """

    try:
        if send_otp_model.user_name is None:
            return HTTPException(
                status_code=400, detail="Email or Phone number is required"
            )

        return await send_otp(send_otp_model.user_name, db)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.post("/enable-2fa")
async def enable_two_factor_auth(request: TwoFactorRequest, db=Depends(get_db)):
    """
    Enables two-factor authentication (2FA) for a specified user.

    This asynchronous function processes a request to enable
    2FA for a user identified by their user ID and the chosen
    authentication method. It calls the appropriate service to
    perform the action and returns a confirmation message along with the user details.

    Args:
        request (TwoFactorRequest): The request model containing
        the user ID and the desired authentication method.
        db: The database dependency for managing user data.

    Returns:
        dict: A message confirming that two-factor authentication
        has been enabled, along with the user details.

    Raises:
        HTTPException: If there is a value error during the enabling process.
    """

    try:
        result = await enable_two_factor(
            user_id=request.user_id, method=request.method, db=db
        )
        return {"message": "Two-factor authentication enabled", "user": result}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.post("/disable-2fa")
async def disable_two_factor_auth(user_id: str, db=Depends(get_db)):
    """
    Disables two-factor authentication (2FA) for a specified user.

    This asynchronous function processes a request to disable 2FA
    for a user identified by their user ID. It calls the appropriate service
    to perform the action and returns a confirmation message along with the user details.

    Args:
        user_id (str): The ID of the user for whom to disable two-factor authentication.
        db: The database dependency for managing user data.

    Returns:
        dict: A message confirming that two-factor authentication
        has been disabled, along with the user details.

    Raises:
        HTTPException: If there is a value error during the disabling process.
    """

    try:
        result = await disable_two_factor(user_id=user_id, db=db)
        return {"message": "Two-factor authentication disabled", "user": result}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.get("/user/{user_id}")
async def get_user(user_id: str, db=Depends(get_db)):
    """
    Retrieves user information based on the provided user ID.

    This asynchronous function fetches the details of a user
    identified by their user ID from the database.
    It returns the user information if found,
    or raises an error if the user ID is invalid.

    Args:
        user_id (str): The ID of the user to retrieve.
        db: The database dependency for accessing user data.

    Returns:
        dict: A dictionary containing the user information.

    Raises:
        HTTPException: If there is a value error during the retrieval process.
    """

    try:
        user = await get_user_by_id(user_id, db)
        return {"user": user}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.put("/user/{user_id}/kyc")
async def update_user_kyc(user_id: str, kyc_data: KycData, db=Depends(get_db)):
    """
    Updates the Know Your Customer (KYC) data for a specified user.

    This asynchronous function processes a request to update
    the KYC information for a user identified by their user ID.
    It calls the appropriate service to perform the update and
    returns a confirmation message along with the updated user details.

    Args:
        user_id (str): The ID of the user whose KYC data is to be updated.
        kyc_data (KycData): The new KYC data to be applied to the user.
        db: The database dependency for managing user data.

    Returns:
        dict: A message confirming that the KYC data has been
        updated successfully, along with the updated user details.

    Raises:
        HTTPException: If there is a value error during the update process.
    """

    try:
        updated_user = await update_kyc_data(user_id=user_id, kyc_data=kyc_data, db=db)
        return {"message": "KYC data updated successfully", "user": updated_user}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.post("/user/{user_id}/transaction")
async def add_user_transaction(
    user_id: str, transaction: Transaction, db=Depends(get_db)
):
    """
    Adds a transaction for a specified user.

    This asynchronous function processes a request to add
    a transaction for a user identified by their user ID.
    It calls the appropriate service to perform the addition
    and returns a confirmation message along with the updated user details.

    Args:
        user_id (str): The ID of the user for whom the transaction is being added.
        transaction (Transaction): The transaction data to be added for the user.
        db: The database dependency for managing user data.

    Returns:
        dict: A message confirming that the transaction has
        been added successfully, along with the updated user details.

    Raises:
        HTTPException: If there is a value error during the transaction addition process.
    """

    try:
        updated_user = await add_transaction(
            user_id=user_id, transaction_data=transaction, db=db
        )
        return {"message": "Transaction added successfully", "user": updated_user}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.post("/user/{user_id}/wallet")
async def add_user_wallet(user_id: str, wallet: CryptoWallet, db=Depends(get_db)):
    """
    Adds a cryptocurrency wallet for a specified user.

    This asynchronous function processes a request to add
    a crypto wallet for a user identified by their user ID.
    It calls the appropriate service to perform the addition
    and returns a confirmation message along with the updated user details.

    Args:
        user_id (str): The ID of the user for whom the wallet is being added.
        wallet (CryptoWallet): The cryptocurrency wallet data to be added for the user.
        db: The database dependency for managing user data.

    Returns:
        dict: A message confirming that the crypto wallet
        has been added successfully, along with the updated user details.

    Raises:
        HTTPException: If there is a value error during the wallet addition process.
    """

    try:
        updated_user = await add_crypto_wallet(
            user_id=user_id, wallet_data=wallet, db=db
        )
        return {"message": "Crypto wallet added successfully", "user": updated_user}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


def send_login_email(request, background_tasks, user):
    if user and user.email:
        ip_address = request.client.host
        email = EmailModel(
            from_email=user.email,
            template_id=Config.LOGIN_EMAIL_TEMPLATE_ID,
            subject=f"{Config.BRAND_NAME} - Login Confirmation",
            plain_text_content=(
                f"Dear {user.name},\n\n"
                f"You have successfully logged in to your {Config.BRAND_NAME} account from IP address: {ip_address}.\n\n"
                "If this wasn't you, please contact our support team immediately.\n\n"
                "Best regards,\n"
                f"The {Config.BRAND_NAME} Team"
            ),
            html_content=(
                f"<p>Dear {user.name},</p>"
                f"<p>You have successfully logged in to your <strong>{Config.BRAND_NAME}</strong> account from IP address: <strong>{ip_address}</strong>.</p>"
                f"<p>If this wasn't you, please contact our support team immediately.</p>"
                f"<p>Best regards,<br/>The <strong>{Config.BRAND_NAME}</strong> Team</p>"
            ),
        )
        background_tasks.add_task(send_email, email)


def send_register_email(request, background_tasks, user):
    if user and user.email:
        ip_address = request.client.host
        email = EmailModel(
            from_email=user.email,
            template_id=Config.REGISTRATION_EMAIL_TEMPLATE_ID,
            subject=f"{Config.BRAND_NAME} Registration Confirmation",
            plain_text_content=(
                f"Dear {user.name},\n\n"
                f"You have successfully registered to {Config.BRAND_NAME} from IP address: {ip_address}.\n\n"
                "If this wasn't you, please contact our support team immediately.\n\n"
                "Best regards,\n"
                f"The {Config.BRAND_NAME} Team"
            ),
            html_content=(
                f"<p>Dear {user.name},</p>"
                f"<p>You have successfully registered to <strong>{Config.BRAND_NAME}</strong> from IP address: <strong>{ip_address}</strong>.</p>"
                f"<p>If this wasn't you, please contact our support team immediately.</p>"
                f"<p>Best regards,<br/>The <strong>{Config.BRAND_NAME}</strong> Team</p>"
            ),
        )
        background_tasks.add_task(send_email, email)
