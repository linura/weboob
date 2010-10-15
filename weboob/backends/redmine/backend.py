# -*- coding: utf-8 -*-

# Copyright(C) 2010  Romain Bignon
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3 of the License.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.


from weboob.capabilities.content import ICapContent, Content
from weboob.tools.backend import BaseBackend

from .browser import RedmineBrowser


__all__ = ['RedmineBackend']


class RedmineBackend(BaseBackend, ICapContent):
    NAME = 'redmine'
    MAINTAINER = 'Romain Bignon'
    EMAIL = 'romain@peerfuse.org'
    VERSION = '0.3'
    DESCRIPTION = 'The Redmine project management web application'
    LICENSE = 'GPLv3'
    CONFIG = {'url':      BaseBackend.ConfigField(description='URL of the Redmine'),
              'username': BaseBackend.ConfigField(description='Login'),
              'password': BaseBackend.ConfigField(description='Password', is_masked=True),
             }
    BROWSER = RedmineBrowser

    def create_default_browser(self):
        return self.create_browser(self.config['url'], self.config['username'], self.config['password'])

    def get_content(self, id):
        if isinstance(id, basestring):
            try:
                project, _type, page = id.split('/', 2)
            except ValueError:
                return None
            content = Content(id)
        else:
            content = id
            id = content.id

        with self.browser:
            data = self.browser.get_wiki_source(project, page)

        content.content = data
        return content

    def push_content(self, content):
        pass
