from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound
from kh_reminder.models import Attendant, DBSession

@view_config(route_name='attendant_modify', renderer='../templates/ui_attendant_modify.jinja2', permission='edit')
def attendant_modify(request):
    # Arriving at this page to add or modify an attendant
    if not request.POST:
        came_from = '/' + '/'.join(request.referrer.split('?')[0].split('/')[3:])
        attendant = None
        if 'id' in request.params:
            _id = int(request.params.get('id'))
            attendant = DBSession.query(Attendant).filter(Attendant.id == _id).first()
        elif 'fullname' in request.params:
            fullname = request.params.get('fullname')
            fname, lname = fullname.split()[0:2]
            if len(fullname.split()) == 3:
                suffix = fullname.split()[2]
                lname += ' ' + suffix
            attendant = Attendant(fname=fname, lname=lname)

        return {'came_from': came_from, 'attendant': attendant, 'path': request.path_info}

    # Adding or modifying attendant after clicking submit
    else:
        came_from = request.params.get('came_from', '/attendants')
        _id = request.params.get('id')
        firstname = request.params.get('fname')
        lastname = request.params.get('lname')
        email = request.params.get('email')
        phone = request.params.get('phone')
        send_email = 1 if request.params.get('send_email') == 'on' else 0
        send_text = 1 if request.params.get('send_text') == 'on' else 0

        if _id and _id.isnumeric():
            _id = int(_id)
            attendant = DBSession.query(Attendant).filter(Attendant.id == _id).first()

            if request.params.get('action') == 'delete':
                DBSession.delete(attendant)

            else:
                attendant.fname = firstname
                attendant.lname = lastname
                attendant.email = email
                attendant.phone = phone
                attendant.send_email = send_email
                attendant.send_sms = send_text

        else:
            attendant = Attendant(
                    fname = firstname,
                    lname = lastname,
                    email = email,
                    phone = phone,
                    send_email = send_email,
                    send_sms = send_text)

            DBSession.add(attendant)

        DBSession.commit()
        return HTTPFound(location=came_from)
