# -*- coding: utf-8 -*-
from plone.restapi.deserializer import json_body
from plone.restapi.interfaces import IPloneRestapiLayer
from plone.restapi.services import Service
from plone.restapi.types.utils import serializeSchema
from plone.restapi.types.utils import update_field
from plone.restapi.types.utils import update_fieldset
from zExceptions import BadRequest
from zope.component import queryMultiAdapter
from zope.interface import alsoProvides
from zope.interface import implementer
from zope.interface import noLongerProvides
from zope.publisher.interfaces import IPublishTraverse
import plone.protect.interfaces


@implementer(IPublishTraverse)
class TypesUpdate(Service):
    def __init__(self, context, request):
        super(TypesUpdate, self).__init__(context, request)
        self.params = []

    def publishTraverse(self, request, name):
        # Treat any path segments after /@types as parameters
        self.params.append(name)
        return self

    def reply(self):
        if not self.params:
            raise BadRequest("Missing parameter typename")

        # Disable CSRF protection
        if "IDisableCSRFProtection" in dir(plone.protect.interfaces):
            alsoProvides(
                self.request,
                plone.protect.interfaces.IDisableCSRFProtection
            )

        # Make sure we get the right dexterity-types adapter
        if IPloneRestapiLayer.providedBy(self.request):
            noLongerProvides(self.request, IPloneRestapiLayer)

        data = json_body(self.request)
        if len(self.params) == 1:
            name = self.params.pop(0)
        elif len(self.params) == 2:
            name = self.params.pop(0)
            fname = self.params.pop(0)
            if "fields" in data:
                return self.reply_for_fieldset(name, fname, data)
            return self.reply_for_field(name, fname, data)
        else:
            raise BadRequest("Too many parameters")

        context = queryMultiAdapter(
            (self.context, self.request), name="dexterity-types"
        )

        # Get content type SchemaContext
        context = context.publishTraverse(self.request, name)

        # Update Fieldset properties
        fieldsets = data.get("fieldsets", [])
        for fieldset in fieldsets:
            fname = fieldset.get("id")
            self.reply_for_fieldset(name, fname, fieldset)

        # Update Field properties
        properties = data.get("properties", {})
        for key, value in properties.items():
            self.reply_for_field(name, key, value)
        return self.reply_no_content()

    def reply_for_fieldset(self, name, fieldset_name, data):
        context = queryMultiAdapter(
            (self.context, self.request), name="dexterity-types"
        )

        # Get content type SchemaContext
        context = context.publishTraverse(self.request, name)

        data["id"] = fieldset_name
        update_fieldset(context, self.request, data)

        serializeSchema(context.schema)
        return self.reply_no_content()

    def reply_for_field(self, name, field_name, data):
        context = queryMultiAdapter(
            (self.context, self.request), name="dexterity-types"
        )

        # Get content type SchemaContext
        context = context.publishTraverse(self.request, name)

        data["id"] = field_name
        update_field(context, self.request, data)

        serializeSchema(context.schema)
        return self.reply_no_content()
