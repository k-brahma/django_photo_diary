from django.core.mail.backends import console


class ReadableSubjectEmailBackend(console.EmailBackend):
    def write_message(self, message):
        from email.header import decode_header
        subject = message.message().get('Subject')
        decoded_tuple = decode_header(subject)
        # => [('Django', None)] # MIMEヘッダエンコーディングなし
        # => [(b'\xe3\x82\xb8\xe3\x83\xa3\xe3\x83\xb3\xe3\x82\xb4', 'utf-8')]
        if decoded_tuple[0][1] is not None:
            readable_subject = decoded_tuple[0][0].decode(
                decoded_tuple[0][1])
        self.stream.write(f'\nSubject {readable_subject}\n')
        super().write_message(message)
