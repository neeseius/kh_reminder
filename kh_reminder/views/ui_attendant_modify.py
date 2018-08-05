from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound
from kh_reminder.models import Attendant, Assignment, DBSession

@view_config(route_name='attendant_modify', renderer='../templates/ui_attendant_modify.jinja2', permission='edit')
def attendant_modify(request):
    # Arriving at this page to add or modify an attendant
    if not request.POST:
        came_from = '/' + '/'.join(request.referrer.split('?')[0].split('/')[3:])
        attendant = None
        attendant_exists = False
        
        # Coming from the attendants page or schedule page
        if 'attendant_id' in request.params:
            attendant_exists = True
            attendant_id = int(request.params.get('attendant_id'))
            attendant = DBSession.query(Attendant).filter(Attendant.id == attendant_id).first()

        # Coming from the schedule page highlighted red
        elif 'assignment_id' in request.params:
            assignment_id = request.params.get("assignment_id")
            assignment = DBSession.query(Assignment).filter(Assignment.id == assignment_id).first()
            fullname = assignment.attendant
            firstname, lastname = fullname.split()[0:2]
            
            if len(fullname.split()) == 3:
                suffix = fullname.split()[2]
                lastname += ' ' + suffix
            
            attendant = Attendant(fname=firstname, lname=lastname)

        return {'came_from': came_from,
                'attendant': attendant,
                'exists': attendant_exists,
                'path': request.path_info}

    # Adding or modifying attendant after clicking submit
    else:
        came_from = request.params.get('came_from', '/attendants')
        attendant_id = request.params.get('id')
        firstname = request.params.get('fname')
        lastname = request.params.get('lname')
        email = request.params.get('email')
        phone = request.params.get('phone')
        send_email = 1 if request.params.get('send_email') == 'on' else 0
        send_text = 1 if request.params.get('send_text') == 'on' else 0

        if attendant_id and attendant_id.isnumeric():
            attendant_id = int(attendant_id)
            attendant = DBSession.query(Attendant).filter(Attendant.id == attendant_id).first()

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
                    fname=firstname,
                    lname=lastname,
                    email=email,
                    phone=phone,
                    send_email=send_email,
                    send_sms=send_text)

            DBSession.add(attendant)

        DBSession.commit()
        return HTTPFound(location=came_from)
