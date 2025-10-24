import yagmail
import os
import sys

try:
    # Carga las variables de entorno (deben estar en CircleCI)
    receiver = os.environ['RECIPIENT_EMAIL']
    sender_user = os.environ['EMAIL_HOST_USER']
    sender_pass = os.environ['EMAIL_HOST_PASSWORD']
    
    # Variables de entorno de CircleCI
    job_name = os.environ.get('CIRCLE_PROJECT_REPONAME', 'JOB_NAME')
    build_num = os.environ.get('CIRCLE_BUILD_NUM', 'BUILD_NUMBER')
    build_url = os.environ.get('CIRCLE_BUILD_URL', 'BUILD_URL')
    
    mail_type = sys.argv[1] # 'success', 'failure', 'unstable'

    yag = yagmail.SMTP(sender_user, sender_pass)
    attachments = []
    subject = ""
    body = []

    if mail_type == 'success':
        subject = f"ÉXITO: Pipeline '{job_name}' - Build #{build_num} Completado"
        body = [
            f"<h1>Estado del Pipeline: EXITOSO</h1>",
            f"<p>El pipeline para el proyecto <b>{job_name}</b> ha finalizado correctamente.</p>",
            f"<p><b>Build:</b> <a href=\"{build_url}\">{build_num}</a></p>"
        ]
    elif mail_type == 'failure':
        subject = f"FALLO: Pipeline '{job_name}' - Build #{build_num} Falló"
        body = [
            f"<h1>Estado del Pipeline: FALLIDO</h1>",
            f"<p>El pipeline para el proyecto <b>{job_name}</b> ha fallado.</p>",
            f"<p><b>Build:</b> <a href=\"{build_url}\">{build_num}</a></p>",
            f"<p>Revisa el log en CircleCI para identificar la causa del error.</p>"
        ]
    
    elif mail_type == 'unstable':
        subject = f"ADVERTENCIA: Pipeline '{job_name}' - Build #{build_num} Inestable"
        body = [
            f"<h1>Estado del Pipeline: INESTABLE (Fallo de Calidad)</h1>",
            f"<p>El pipeline para el proyecto <b>{job_name}</b> ha finalizado con advertencias de calidad de código.</p>",
            f"<p><b>Build:</b> <a href=\"{build_url}\">{build_num}</a></p>",
            "<hr><h2>Reporte de Calidad de Código (Flake8):</h2>"
        ]
        # Adjunta el reporte de flake8
        if os.path.exists('flake8-report.txt'):
            attachments.append('flake8-report.txt')
            try:
                with open('flake8-report.txt', 'r') as f:
                    report_content = f.read()
                body.append(f"<pre>{report_content}</pre>")
            except Exception as e:
                body.append(f"<pre>No se pudo leer el reporte: {e}</pre>")
        else:
            body.append("<pre>No se encontró el reporte de Flake8.</pre>")

    # Enviar el correo
    yag.send(to=receiver, subject=subject, contents=body, attachments=attachments)
    print(f"Email '{mail_type}' enviado a {receiver}.")

except Exception as e:
    print(f"Error crítico al enviar email: {e}")
    # No fallar el build si el email falla, solo imprimir el error
    pass