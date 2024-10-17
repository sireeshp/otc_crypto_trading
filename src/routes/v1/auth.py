from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Request, status

from src.models.AuthModel import LoginModel, VerifyOtpModel
from src.models.EmailModel import EmailModel
from src.services.auth_service import authenticate_email, authenticate_otp
from src.services.email_service import send_email
from src.utils.mongo_utils import get_db

router = APIRouter()


@router.post("/login", status_code=status.HTTP_200_OK)
async def login(
    request: Request,
    login_model: LoginModel,
    background_tasks: BackgroundTasks,
    db=Depends(get_db),
):
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


def send_login_email(request, background_tasks, user):
    if user and user.email:
        ip_address = request.client.host
        email = EmailModel(
            from_email=user.email,
            subject="Logged-in Confirmation",
            plain_text_content=f"You have logged in from IP: {ip_address}. If this wasn't you, please contact support.",
            html_content=f"<p>You have logged in from IP: {ip_address}. If this wasn't you, please contact support.</p>",
        )
        background_tasks.add_task(send_email, email)


@router.post("/verify_otp", status_code=status.HTTP_200_OK)
async def verify_otp(verify_model: VerifyOtpModel, db=Depends(get_db)):
    try:
        if verify_model.user_name is None:
            raise HTTPException(
                status_code=400, detail="Email or Phone Number is required"
            )

        if verify_model.code is None:
            raise HTTPException(status_code=400, detail="OTP is required")
        return await authenticate_otp(verify_model.user_name, verify_model.code, db)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e
