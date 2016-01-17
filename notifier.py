import settings
import logging as log


def notify():
    if settings.registration_id:
        send_gcm_notification("IR Sensor", "Alarm!")
    if settings.pwd:
        send_email("IR Sensor", "Alarm!")


def send_email(subject, body):
    import smtplib

    user = settings.user
    pwd = settings.pwd
    to = settings.recipient if type(settings.recipient) is list else [settings.recipient]
    message = """\From: %s\nTo: %s\nSubject: %s\n\n%s
    """ % (user, ", ".join(to), subject, body)
    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.ehlo()
        server.starttls()
        server.login(user, pwd)
        server.sendmail(user, to, message)
        server.close()
        log.debug('Sent the mail')
    except:
        log.error("Failed to send mail")


def send_gcm_notification(title, message):
    import gcm

    gcmx = gcm.GCM(settings.gcm_api)
    response = gcmx.json_request(registration_ids=[settings.registration_id], data={"title": title, "message": message})

    if response and 'success' in response:
        log.info('Successfully sent notification')
    if 'errors' in response:
        log.error("Failed to send notification")
