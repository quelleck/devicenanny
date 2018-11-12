#
# Slack Messages
# Hudl
#
# Created by Ethan Seyl 2016
#

import logging
from slacker import Slacker

from flask import current_app


class NannySlacker:
    def __init__(self):
        self.channel = current_app.config['slack_channel']
        self.team_channel = current_app.config['slack_team_channel']
        self.slack = Slacker(current_app.config['SLACK_API_KEY'])

    def help_message(self, device_name):
        """
        Sends a message to the device checkout slack channel that a device was taken
        without being checked out.
        :param device_name: Name of device taken
        """
        text = "`{}` was taken without being checked out! Please remember to enter your name" \
               " when taking a device.".format(device_name)
        self.slack.chat.post_message(
            self.channel,
            attachments=[{
                "pretext": "Missing Device",
                "fallback": "Message from DeviceNanny",
                "text": text
            }])
        logging.debug("[help_message] Help message sent.")

    def user_reminder(self, slack_id, time_difference, device_name):
        """
        Sends a checkout expired reminder.
        :param slack_id: ID of user who checked out device
        :param time_difference: Time since device was checked out
        :param device_name: Name of expired device
        """
        try:
            text = "It's been *{}* since you checked out `{}`. Please renew your checkout online or return it " \
                   "to the device lab.".format(time_difference, device_name)

            self.slack.chat.post_message(
                slack_id,
                attachments=[{
                    "pretext": "Checkout Reminder",
                    "fallback": "Message from DeviceNanny",
                    "text": text
                }])
            logging.debug("[user_reminder] Reminder sent.")
        except Exception as e:
            logging.warning("[user_reminder] Incorrect Slack ID. {}".format(e))

    def check_out_notice(self, user_info, device):
        """
        Sends a slack message confirming a device was checked out.
        :param user_info: First Name, Last Name, slack_id, location of user who checked out device
        :param device: Device taken
        """
        try:
            current_app.logger.debug('[check_out_notice] User Info: {} Device: {}'.format(user_info, device))
            user_text = "You checked out `{}`. Checkout will expire after {} hours. Remember to plug the " \
                        "device back in when you return it to the lab. You can extend your checkout from " \
                        "the DeviceNanny web page.".format(device, current_app.config['checkout_expires'])

            channel_text = "*{} {}* just checked out `{}`".format(user_info['first_name'], user_info['last_name'],
                                                                  device)

            self.slack.chat.post_message(
                user_info['slack_id'],
                attachments=[{
                    "pretext": "Device Checked Out",
                    "fallback": "Message from DeviceNanny",
                    "text": user_text
                }])
            self.slack.chat.post_message(
                self.channel,
                attachments=[{
                    "pretext": "Device Checked Out",
                    "fallback": "Message from DeviceNanny",
                    "text": channel_text
                }])
            logging.debug("[check_out_notice] Checkout message sent.")
        except Exception as e:
            current_app.logger.debug("[check_out_notice] Check out notice NOT sent. {} CHANNEL: {}".format(e, self.channel))

    def check_in_notice(self, user_info, device):
        """
        Sends a slack message confirming a device was checked in.
        :param user_info: First Name, Last Name, slack_id, location of user who checked in device
        :param device: Device returned
        """
        try:
            user_text = "You checked in `{}`. Thanks!".format(device)
            channel_text = "*{} {}* just checked in `{}`".format(user_info['first_name'], user_info['last_name'],
                                                                 device)

            if user_info["first_name"] != "Missing":
                current_app.logger.debug("[check_in_notice] slack_id from user_info: {}".format(user_info['slack_id']))
                self.slack.chat.post_message(
                    user_info['slack_id'],
                    attachments=[{
                        "pretext": "Device Checked In",
                        "fallback": "Message from DeviceNanny",
                        "text": user_text
                    }])
                self.slack.chat.post_message(
                    self.channel,
                    attachments=[{
                        "pretext": "Device Checked In",
                        "fallback": "Message from DeviceNanny",
                        "text": channel_text
                    }])
                current_app.logger.debug("[check_in_notice] {} {} just checked in {}"
                                         .format(user_info['first_name'], user_info['LastName'], device))
            elif user_info["first_name"] == "Missing":
                self.slack.chat.post_message(
                    self.channel,
                    attachments=[{
                        "pretext": "Device Checked In",
                        "fallback": "Message from DeviceNanny",
                        "text": "Missing device {} has been returned to the lab.".format(device)
                    }])
        except Exception as e:
            current_app.logger.debug("[check_in_notice] Check in message not sent. {}".format(e))

    def post_to_channel(self, device_id, time_difference, first_name, last_name):
        """
        Sends a slack message to the device checkout channel with an update for an expired checkout.
        :param device_id: Device ID of device taken
        :param time_difference: Time since device was checked out
        :param first_name: First name of user with expired checkout
        :param last_name: Last name of user with expired checkout
        """
        text = '`{}` was checked out *{}* ago by *{} {}*'.format(device_id, time_difference, first_name, last_name)
        self.slack.chat.post_message(
            self.channel,
            attachments=[{
                "pretext": "Expired Checkout",
                "fallback": "Message from DeviceNanny",
                "text": text
            }])
        logging.debug("[post_to_channel] Posted to channel.")

    def nanny_check_in(self, device_name):
        """
        Sends slack message to the device checkout channel. Sent when the Nanny discovers a
        connected device that wasn't checked in.
        :param device_name: Name of device checked in
        """
        text = "`{}` was checked in by the Nanny.".format(device_name)
        self.slack.chat.post_message(
            self.channel,
            attachments=[{
                "pretext": "Missing Device Checked In",
                "fallback": "Message from DeviceNanny",
                "text": text
            }])
        logging.debug("[nanny_check_in] Nanny check-in message sent.")

    def missing_device_message(self, device_name, time_difference):
        """
        Send a message to the location channel about a device that's been missing from the lab
        for more than the set checkout time.
        :param device_name:
        :param time_difference:
        :return:
        """
        text = "`{}` has been missing from the device lab for `{}`. If you have it, please return the device to " \
               "the lab and check it out under your name.".format(device_name, time_difference)
        self.slack.chat.post_message(
            self.team_channel,
            attachments=[{
                "pretext": "Missing Device",
                "fallback": "Message from DeviceNanny",
                "text": text
            }])
        logging.info(
            "[missing_device_message] Slack reminder sent to team channel for {}".
            format(device_name))
