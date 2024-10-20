import re
from clicksend_client import (
    SmsMessage,
    SmsMessageCollection,
    Configuration,
    SMSApi,
    ApiClient,
)
from typing import List, Dict
from src.utils.config import Config
from src.utils.logger import setup_logger

logger = setup_logger("sms_service", "logs/sms_service.log")
# Configure ClickSend API
configuration = Configuration()
configuration.username = Config.CLICK_SEND_USER_NAME
configuration.password = Config.CLICK_SEND_PASSWORD
api_instance = SMSApi(ApiClient(configuration))


def validate_phone_number(phone_number: str) -> bool:
    phone_number_pattern = r"^\+?[1-9]\d{1,14}$"
    return re.match(phone_number_pattern, phone_number)


async def send_sms_message_collection(collection: List[Dict[str, str]]):
    try:
        # Prepare SMS messages for the API
        sms_collection = [
            SmsMessage(source="sdk", body=msg["message"], to=msg["to_phone_number"])
            for msg in collection
        ]
        sms_messages = SmsMessageCollection(messages=sms_collection)

        # Make asynchronous request using ClickSend's API
        response_thread = api_instance.sms_send_post(sms_messages, async_req=True)
        response = response_thread.get()

        # Log the success response
        logger.info(f"SMS sent successfully: {response}")
        return response

    except Exception as e:
        # Log the exception for debugging
        logger.error(f"Failed to send SMS messages: {str(e)}")
        raise ValueError(f"Error in sending SMS: {str(e)}") from e


async def send_sms(to_phone_number: str, message: str):
    try:
        if validate_phone_number(to_phone_number):
            # Prepare and send the SMS message
            return await send_sms_message_collection(
                [{"message": message, "to_phone_number": to_phone_number}]
            )
        logger.warning(f"Invalid phone number format: {to_phone_number}")
        raise ValueError("Invalid phone number format")

    except Exception as e:
        logger.error(f"Failed to send SMS to {to_phone_number}: {str(e)}")
        raise


# Example usage
if __name__ == "__main__":
    # Example of how this could be used
    import asyncio

    try:
        asyncio.run(send_sms("+447774398018", "Your OTP code is 123456"))
    except Exception as e:
        logger.error(f"SMS sending failed: {e}")
