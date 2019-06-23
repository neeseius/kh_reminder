from pyramid.view import view_config
from pyramid.response import Response
from kh_reminder.models import Signature
from kh_reminder.lib.dbsession import Session


@view_config(route_name='signature', renderer='string', permission='edit')
def signature(request):
    sig = Session.DBSession.query(Signature).one()
    if request.method == "POST":
        sig.message = request.json_body.get("message")
        Session.DBSession.commit()
        return Response(status=204)

    return sig.message
