# -*- coding: utf-8 -*-
from Acquisition import aq_inner
from plone.restapi.services import Service
from Products.CMFCore.utils import getToolByName


class RolesGet(Service):

    def reply(self):
        pmemb = getToolByName(aq_inner(self.context), 'portal_membership')
        roles = [r for r in pmemb.getPortalRoles() if r != 'Owner']
        return [
            {
                '@type': 'role',
                '@id': '{}/@roles/{}'.format(self.context.absolute_url(), r),
                'id': r,
            }
            for r in roles
        ]
