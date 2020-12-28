from django.conf import settings

def send_email(email, password):

    from django.core.mail import EmailMultiAlternatives

    subject = '来自Speaker Recognition系统找回密码的邮件'

    text_content = '''感谢注册Speaker Recognition系统，本系统主要是提供说话人识别的功能，在这里，您可以有的录制您的语音，我们会为您保密！\
                    如果你看到这条消息，说明你的邮箱服务器不提供HTML链接功能，请联系管理员！'''

    html_content = '''
                    <p>感谢注册Speaker Recognition系统，本系统主要是提供说话人识别的功能，\
                    在这里，您可以录制您的语音，您可以随心录制，我们会为您保密！</p>
                    <p>您的注册密码为{},很高兴为您服务，如还有其他问题请联系管理员！</p>
                    '''.format( password)

    msg = EmailMultiAlternatives(subject, text_content, settings.EMAIL_HOST_USER, [email])
    msg.attach_alternative(html_content, "text/html")
    msg.send()