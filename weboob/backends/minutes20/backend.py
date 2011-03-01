# -*- coding: utf-8 -*-

# Copyright(C) 2011  Julien Hebert
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
"backend for http://20minutes.fr"

from weboob.capabilities.messages import ICapMessages
from .browser import Newspaper20minutesBrowser
from .GenericBackend import GenericNewspaperBackend

class Newspaper20minutesBackend(GenericNewspaperBackend, ICapMessages):
    "Newspaper20minutesBackend class"
    MAINTAINER = 'Julien Hebert'
    EMAIL = 'juke@free.fr'
    VERSION = '0.6.1'
    LICENSE = 'GPLv3'
    STORAGE = {'seen': {}}
    NAME = 'minutes20'
    DESCRIPTION = u'20minutes French news  website'
    BROWSER = Newspaper20minutesBrowser
    RSS_FEED = 'http://www.20minutes.fr/rss/20minutes.xml'

