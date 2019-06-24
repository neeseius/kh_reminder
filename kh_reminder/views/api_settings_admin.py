from pyramid.view import view_config
from kh_reminder.models import Administrator
from kh_reminder.lib.dbsession import Session
from kh_reminder.lib.notifications import Notify


@view_config(route_name='admin_contact', renderer='json')#, permission='edit')
def admin_contact(request):
    admin = Session.DBSession.query(Administrator).one()

    if request.method == "POST":
        response = {}
        verify_email = False
        email = request.json_body.get("email")
        email_password = request.json_body.get("email_password")
        email_smtp = request.json_body.get("email_smtp")
        phone = request.json_body.get("phone")

        if email and email != admin.email:
            verify_email = True
            admin.email = email

        if email_password and email_password != admin.email_password:
            verify_email = True
            admin.email_password = email_password

        if email_smtp and email_smtp != admin.email_smtp:
            verify_email = True
            admin.email_smtp = email_smtp

        if phone and phone != admin.phone:
            admin.phone = phone

        if verify_email:
            try:
                Notify.send_test_email(admin)
                admin.can_email = 1
                response["can_email"] = 1
            except Exception as e:
                admin.can_email = 0
                response["can_email"] = 0
                print(e)

        Session.DBSession.commit()

        return response

    else:
        return {
            "admin_email": admin.email,
            "admin_email_smtp": admin.email_smtp,
            "admin_can_email": admin.can_email,
            "admin_phone": admin.phone
        }
