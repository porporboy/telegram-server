"""
Telegram controller
"""
from telegram_models import TelegramUserAccount
from phone_util import sanitize_phone_number
import telegram_util
import logging

LOGGER = logging.getLogger(__name__)


class TelegramController(object):

    def get(self, request_params, response):
        """
        Endpoint called for retrieving the telegram contacts of the specified phone number. The phone number has
        to be logged in first for this endpoint to work.
        """
        phone_number = sanitize_phone_number(request_params.get('phone'))
        page = request_params.get('page')
        with TelegramUserAccount(phone_number, user_phone=phone_number) as telegram_user:
            if not telegram_user.is_user_authorized():
                LOGGER.error('Telegram user unauthorized.')
                raise Exception('Telegram user unauthorized.')
            else:
                LOGGER.info('Telegram user authorized, fetching contacts...')
                telegram_user.get_contacts(request_params.get('limit'), request_params.get('page'))
                LOGGER.info('Fetched telegram contacts: {}'.format({
                    'contacts': telegram_user.contacts,
                    'last_page': telegram_user.last_page
                }))

            return {
                'contacts': telegram_user.contacts,
                'last_page': telegram_user.last_page
            }

    def post(self, request_params, response):
        """
        This endpoint is called for initiating the authorization flow.
        @param request_params: should contain an 'type' paramter. 'onboard' is for
                the initialization of the flow, while 'code' is for verifying the authorization code.
        """
        phone_number = sanitize_phone_number(request_params.get('phone'))
        auth_type = request_params.get('type')
        result = {}
        with TelegramUserAccount(phone_number, user_phone=phone_number) as telegram_user:
            if not telegram_user.is_user_authorized():
                if auth_type == 'onboard':
                    LOGGER.info('Sending telegram verification code to {}'.format('+' + phone_number))
                    telegram_user.send_code_request(phone_number)
                    result = {"identifier": telegram_user.phone_code_hashes[phone_number]}
                    LOGGER.info(telegram_user.phone_code_hashes)
                elif auth_type == 'code':
                    code = request_params.get('code')
                    identifier = request_params.get('identifier')
                    telegram_user.phone_code_hashes.update({phone_number: identifier})
                    LOGGER.info('Authorizing telegram phone with hash {} and code {}'
                        .format(telegram_user.phone_code_hashes[phone_number], code))
                    telegram_user.authorize_code(code)
            else:
                response.status = 208

        return result
