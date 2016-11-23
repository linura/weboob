# -*- coding: utf-8 -*-

# Copyright(C) 2010-2011 Julien Veyssier
#
# This file is part of weboob.
#
# weboob is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# weboob is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with weboob. If not, see <http://www.gnu.org/licenses/>.


try:
    from urlparse import urlparse
except ImportError:
    from urllib.parse import urlparse

from datetime import datetime
from dateutil.relativedelta import relativedelta

from weboob.tools.compat import basestring
from weboob.tools.capabilities.bank.transactions import FrenchTransaction
from weboob.browser.browsers import LoginBrowser, need_login
from weboob.browser.profiles import Wget
from weboob.browser.url import URL
from weboob.browser.pages import FormNotFound
from weboob.exceptions import BrowserIncorrectPassword
from weboob.capabilities.bank import Account

from .pages import LoginPage, LoginErrorPage, AccountsPage, UserSpacePage, \
                   OperationsPage, CardPage, ComingPage, NoOperationsPage, \
                   ChangePasswordPage, VerifCodePage,       \
                   EmptyPage, PorPage, IbanPage, NewHomePage, RedirectPage, \
                   LIAccountsPage, CardsActivityPage, CardsListPage,       \
                   CardsOpePage, NewAccountsPage, InternalTransferPage, \
                   ExternalTransferPage


__all__ = ['CreditMutuelBrowser']


class CreditMutuelBrowser(LoginBrowser):
    PROFILE = Wget()
    TIMEOUT = 30
    BASEURL = 'https://www.creditmutuel.fr'

    login =       URL('/groupe/fr/index.html',
                      '/(?P<subbank>.*)fr/$',
                      '/(?P<subbank>.*)fr/banques/accueil.html',
                      '/(?P<subbank>.*)fr/banques/particuliers/index.html',
                      LoginPage)
    login_error = URL('/(?P<subbank>.*)fr/identification/default.cgi',      LoginErrorPage)
    accounts =    URL('/(?P<subbank>.*)fr/banque/situation_financiere.cgi',
                      '/(?P<subbank>.*)fr/banque/situation_financiere.html',
                      AccountsPage)
    user_space =  URL('/(?P<subbank>.*)fr/banque/espace_personnel.aspx',
                      '/(?P<subbank>.*)fr/banque/accueil.cgi',
                      '/(?P<subbank>.*)fr/banque/DELG_Gestion',
                      '/(?P<subbank>.*)fr/banque/paci_engine/static_content_manager.aspx',
                      UserSpacePage)
    card =        URL('/(?P<subbank>.*)fr/banque/operations_carte.cgi.*',
                      '/(?P<subbank>.*)fr/banque/mouvements.html\?webid=.*cardmonth=\d+$',
                      CardPage)
    operations =  URL('/(?P<subbank>.*)fr/banque/mouvements.cgi.*',
                      '/(?P<subbank>.*)fr/banque/mouvements.html.*',
                      '/(?P<subbank>.*)fr/banque/nr/nr_devbooster.aspx.*',
                      OperationsPage)
    coming =      URL('/(?P<subbank>.*)fr/banque/mvts_instance.cgi.*',      ComingPage)
    noop =        URL('/(?P<subbank>.*)fr/banque/CR/arrivee.asp.*',         NoOperationsPage)
    info =        URL('/(?P<subbank>.*)fr/banque/BAD.*',                    EmptyPage)
    change_pass = URL('/(?P<subbank>.*)fr/validation/change_password.cgi',
                      '/fr/services/change_password.html', ChangePasswordPage)
    verify_pass = URL('/(?P<subbank>.*)fr/validation/verif_code.cgi.*',     VerifCodePage)
    new_home =    URL('/fr/banque/pageaccueil.html',
                      '/(?P<subbank>.*)fr/banque/DELG_Gestion.*',
                      '/mabanque/fr/banque/pageaccueil.html',
                      '/(?P<subbank>.*)fr/banque/paci_engine/static_content_manager.aspx',
                      '/fr/banque/welcome_pack.html', NewHomePage)
    empty =       URL('/(?P<subbank>.*)fr/banques/index.html',
                      '/(?P<subbank>.*)fr/banque/paci_beware_of_phishing.*',
                      '/(?P<subbank>.*)fr/validation/(?!change_password|verif_code).*',
                      EmptyPage)
    por =         URL('/(?P<subbank>.*)fr/banque/POR_ValoToute.aspx',
                      '/(?P<subbank>.*)fr/banque/POR_SyntheseLst.aspx',
                      PorPage)
    li =          URL('/(?P<subbank>.*)fr/assurances/profilass.aspx\?domaine=epargne',
                      '/(?P<subbank>.*)fr/assurances/(consultation/)?WI_ASSAVI', LIAccountsPage)
    iban =        URL('/(?P<subbank>.*)fr/banque/rib.cgi', IbanPage)

    new_accounts = URL('/(?P<subbank>.*)fr/banque/comptes-et-contrats.html', NewAccountsPage)
    new_operations = URL('/(?P<subbank>.*)fr/banque/mouvements.cgi',
                         '/fr/banque/nr/nr_devbooster.aspx.*',
                         '/(?P<subbank>.*)fr/banque/RE/aiguille.asp',
                         '/fr/banque/mouvements.html', OperationsPage)
    new_por = URL('/(?P<subbank>.*)fr/banque/POR_ValoToute.aspx',
                  '/(?P<subbank>.*)fr/banque/POR_SyntheseLst.aspx', PorPage)
    new_iban = URL('/(?P<subbank>.*)fr/banque/rib.cgi', IbanPage)

    redirect = URL('/(?P<subbank>.*)fr/banque/paci_engine/static_content_manager.aspx', RedirectPage)

    cards_activity = URL('/(?P<subbank>.*)fr/banque/pro/ENC_liste_tiers.aspx', CardsActivityPage)
    cards_list = URL('/(?P<subbank>.*)fr/banque/pro/ENC_liste_ctr.*', CardsListPage)
    cards_ope = URL('/(?P<subbank>.*)fr/banque/pro/ENC_liste_oper', CardsOpePage)

    internal_transfer = URL('/(?P<subbank>.*)fr/banque/virements/vplw_vi.html', InternalTransferPage)
    external_transfer = URL('/(?P<subbank>.*)fr/banque/virements/vplw_vee.html', ExternalTransferPage)

    currentSubBank = None
    is_new_website = False

    __states__ = ['currentSubBank']

    def do_login(self):
        # Clear cookies.
        self.do_logout()

        self.login.go()

        if not self.page.logged:
            self.page.login(self.username, self.password)

            if not self.page.logged or self.login_error.is_here():
                raise BrowserIncorrectPassword()

        self.getCurrentSubBank()

    @need_login
    def get_accounts_list(self):
        if not hasattr(self, 'accounts_list'):
            self.fleet_pages = {}
            if self.currentSubBank is None:
                self.getCurrentSubBank()
            self.accounts_list = []
            if not self.is_new_website:
                for a in self.accounts.stay_or_go(subbank=self.currentSubBank).iter_accounts():
                    self.accounts_list.append(a)
                for company in self.page.company_fleet():
                    self.location(company)
                    for a in self.page.iter_cards():
                        self.accounts_list.append(a)
                self.iban.go(subbank=self.currentSubBank).fill_iban(self.accounts_list)
                self.por.go(subbank=self.currentSubBank).add_por_accounts(self.accounts_list)
                for acc in self.li.go(subbank=self.currentSubBank).iter_li_accounts():
                    self.accounts_list.append(acc)
            else:
                for a in self.new_accounts.stay_or_go(subbank=self.currentSubBank).iter_accounts():
                    self.accounts_list.append(a)
                self.new_iban.go(subbank=self.currentSubBank).fill_iban(self.accounts_list)
                self.new_por.go(subbank=self.currentSubBank).add_por_accounts(self.accounts_list)
            for id, pages_list in self.fleet_pages.iteritems():
                for page in pages_list:
                    for a in page.get_cards(accounts=self.accounts_list):
                        if a not in self.accounts_list:
                            self.accounts_list.append(a)
        return self.accounts_list

    def get_account(self, id):
        assert isinstance(id, basestring)

        for a in self.get_accounts_list():
            if a.id == id:
                return a

    def getCurrentSubBank(self):
        # the account list and history urls depend on the sub bank of the user
        paths = urlparse(self.url).path.lstrip('/').split('/')
        self.currentSubBank = paths[0] + "/" if paths[0] != "fr" else ""

    def list_operations(self, page_url):
        if page_url.startswith('/') or page_url.startswith('https') or page_url.startswith('?'):
            self.location(page_url)
        else:
            self.location('%s/%sfr/banque/%s' % (self.BASEURL, self.currentSubBank, page_url))

        # getting about 6 months history on new website
        if self.is_new_website and self.page:
            try:
                for x in range(0, 2):
                    form = self.page.get_form(id="I1:fm", submit='//input[@name="_FID_DoActivateSearch"]')
                    if x == 1:
                        form.update({
                            [k for k in form.keys() if "DateStart" in k][0]: (datetime.now() - relativedelta(months=7)).strftime('%d/%m/%Y'),
                            [k for k in form.keys() if "DateEnd" in k][0]: datetime.now().strftime('%d/%m/%Y')
                        })
                        [form.pop(k, None) for k in form.keys() if "_FID_Do" in k and "DoSearch" not in k]
                    form.submit()
            except (IndexError, FormNotFound):
                pass

        while self.page:
            try:
                form = self.page.get_form('//*[@id="I1:fm"]', submit='//input[@name="_FID_DoLoadMoreTransactions"]')
                [form.pop(k, None) for k in form.keys() if "_FID_Do" in k and "LoadMore" not in k]
                form.submit()
            except (IndexError, FormNotFound):
                break

        if self.li.is_here():
            return self.page.iter_history()

        if not self.operations.is_here():
            return iter([])

        return self.pagination(lambda: self.page.get_history())

    def get_history(self, account):
        transactions = []
        if not account._link_id:
            return iter([])
        # need to refresh the months select
        if account._link_id.startswith('pro'):
            self.location(account._pre_link)
        for tr in self.list_operations(account._link_id):
            transactions.append(tr)

        coming_link = self.page.get_coming_link() if self.operations.is_here() else None
        if coming_link is not None:
            for tr in self.list_operations(coming_link):
                transactions.append(tr)

        differed_date = None
        for card_link in account._card_links:
            for tr in self.list_operations(card_link):
                if not differed_date or tr._differed_date < differed_date:
                    differed_date = tr._differed_date
                if tr.date > datetime.now():
                    tr._is_coming = True
                transactions.append(tr)

        if differed_date is not None:
            # set deleted for card_summary
            for tr in transactions:
                tr.deleted = tr.type == FrenchTransaction.TYPE_CARD_SUMMARY and differed_date.month <= tr.date.month

        transactions.sort(key=lambda tr: tr.rdate, reverse=True)
        return transactions

    def get_investment(self, account):
        if account._is_inv:
            if account.type == Account.TYPE_MARKET:
                if not self.is_new_website:
                    self.por.go(subbank=self.currentSubBank)
                else:
                    self.new_por.go(subbank=self.currentSubBank)
                self.page.send_form(account)
            elif account.type == Account.TYPE_LIFE_INSURANCE:
                if not account._link_inv:
                    return iter([])
                self.location(account._link_inv)
            return self.page.iter_investment()
        return iter([])

    def iter_recipients(self, origin_account):
        # access the transfer page
        self.internal_transfer.go(subbank=self.currentSubBank)
        if self.page.can_transfer(origin_account.id):
            for recipient in self.page.iter_recipients(origin_account=origin_account):
                yield recipient
        self.external_transfer.go(subbank=self.currentSubBank)
        if self.page.can_transfer(origin_account.id):
            origin_account._external_recipients = set()
            if self.page.has_transfer_categories():
                for category in self.page.iter_categories():
                    self.page.go_on_category(category['index'])
                    self.page.IS_PRO_PAGE = True
                    for recipient in self.page.iter_recipients(origin_account=origin_account, category=category['name']):
                        yield recipient
            else:
                for recipient in self.page.iter_recipients(origin_account=origin_account):
                    yield recipient

    def init_transfer(self, account, to, amount, reason=None):
        if to.category != u'Interne':
            self.external_transfer.go(subbank=self.currentSubBank)
        else:
            self.internal_transfer.go(subbank=self.currentSubBank)

        if self.external_transfer.is_here() and self.page.has_transfer_categories():
            for category in self.page.iter_categories():
                if category['name'] == to.category:
                    self.page.go_on_category(category['index'])
                    break
            self.page.IS_PRO_PAGE = True
            self.page.RECIPIENT_STRING = 'data_input_indiceBen'
        self.page.prepare_transfer(account, to, amount, reason)
        return self.page.handle_response(account, to, amount, reason)

    def execute_transfer(self, transfer, **params):
        form = self.page.get_form(id='P:F', submit='//input[@type="submit" and contains(@value, "Confirmer")]')
        # For the moment, don't ask the user if he confirms the duplicate.
        form['Bool:data_input_confirmationDoublon'] = 'true'
        form.submit()
        return self.page.create_transfer(transfer)

