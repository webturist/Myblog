import asyncio
from aiosmtpd.controller import Controller
import os
import time

async def handle_message(message):
    print(f'Message received from: {message.mail_from}')
    print(f'Message received for: {message.rcpt_tos}')
    print(f'Message data:\n{message.content.decode()}')

class MailHandler:
    def __init__(self, handler, enable_SMTPUTF8=True):
        self.handler = handler
        self.enable_SMTPUTF8 = enable_SMTPUTF8

    async def handle_DATA(self, server, session, envelope):
        filename = os.path.join("sendmail", f"mail_{int(time.time())}.eml")
        with open(filename, "w") as f:
            f.write(envelope.content.decode())
        return '250 Message accepted for delivery'

class MailServer:
    def __init__(self, handler, hostname='localhost', port=1050):
        self.handler = handler
        self.hostname = hostname
        self.port = port
        self.controller = None

    async def start(self):
        self.controller = Controller(self.handler, hostname=self.hostname, port=self.port)
        self.controller.start()

        print(f"Starting mail server on {self.hostname}:{self.port}...")
        try:
            while True:
                await asyncio.sleep(86400)  # Run the server indefinitely
        except KeyboardInterrupt:
            print("Stopping mail server...")
            await self.controller.stop()

    async def stop(self):
        print('Stopping mail server...')
        await self.controller.stop()

if __name__ == '__main__':
    mail_handler = MailHandler(handle_message)
    mail_server = MailServer(mail_handler)
    asyncio.run(mail_server.start())


