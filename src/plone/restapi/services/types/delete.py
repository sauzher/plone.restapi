# -*- coding: utf-8 -*-
import plone.protect.interfaces
from plone.restapi.services import Service
from plone.restapi.interfaces import IPloneRestapiLayer
from zope.interface import alsoProvides
from zope.interface import implementer
from zope.interface import noLongerProvides
from zope.component import queryMultiAdapter
from zope.publisher.interfaces import IPublishTraverse
from zExceptions import BadRequest


@implementer(IPublishTraverse)
class TypesDelete(Service):
    """ Deletes a field/fieldset from content type
    """
    def __init__(self, context, request):
        super(TypesDelete, self).__init__(context, request)
        self.params = []

    def publishTraverse(self, request, name):
        # Treat any path segments after /@types as parameters
        self.params.append(name)
        return self

    def reply(self):
        if not self.params:
            raise BadRequest("Missing parameter typename")
        if len(self.params) < 2:
            raise BadRequest("Missing parameter fieldname")
        if len(self.params) > 2:
            raise BadRequest("Too many parameters")

        # Disable CSRF protection
        if "IDisableCSRFProtection" in dir(plone.protect.interfaces):
            alsoProvides(
                self.request,
                plone.protect.interfaces.IDisableCSRFProtection
            )

        # Make sure we don't get the right dexterity-types adapter
        if IPloneRestapiLayer.providedBy(self.request):
            noLongerProvides(self.request, IPloneRestapiLayer)

        context = queryMultiAdapter(
            (self.context, self.request), name="dexterity-types"
        )

        # Get content type SchemaContext
        name = self.params.pop(0)
        context = context.publishTraverse(self.request, name)

        name = self.params.pop(0)
        try:
            context = context.publishTraverse(self.request, name)
        except Exception:
            # Removing a fieldset
            self.request.form['name'] = name
            delete = queryMultiAdapter((context, self.request),
                                       name="delete-fieldset")
        else:
            # Removing a field
            delete = queryMultiAdapter((context, self.request),
                                       name="delete")

        delete()

        return self.reply_no_content()
