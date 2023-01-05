# -*- coding: utf-8 -*-

from collections import defaultdict
from datetime import datetime
from itertools import groupby
from operator import itemgetter
from re import findall as regex_findall
from re import split as regex_split
from dateutil import relativedelta
from odoo import SUPERUSER_ID, _, api, fields, models
from odoo.exceptions import UserError
from odoo.osv import expression
from odoo.tools.float_utils import float_compare, float_is_zero, float_repr, float_round
from odoo.tools.misc import format_date, OrderedSet
from odoo.exceptions import AccessError, UserError


class AccountAccountInh(models.Model):
    _inherit = 'account.account'

    account_from = fields.Boolean(string='From')
    account_to = fields.Boolean(string='To')


class POSConfigInh(models.Model):
    _inherit = 'pos.config'

    is_non_ofc_pos = fields.Boolean(string='Non Official POS')


