from website import create_app
from extensions import mail
import os

gmail_pass = "nxnt zopk aiai iqvp"

if __name__ == '__main__':
    app = create_app()
    app.config['MAIL_SERVER']='smtp.gmail.com'
    app.config['MAIL_PORT'] = 465
    app.config['MAIL_USERNAME'] = 'BookcaseDatabase@gmail.com'
    app.config['MAIL_PASSWORD'] = gmail_pass
    app.config['MAIL_USE_TLS'] = False
    app.config['MAIL_USE_SSL'] = True
    mail.init_app(app)
    app.run(host="0.0.0.0", port=5000)


