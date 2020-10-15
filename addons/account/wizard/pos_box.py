# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from openerp.osv import fields, osv
import openerp.addons.decimal_precision as dp
from openerp.tools.translate import _

class CashBox(osv.osv_memory):
    _register = False
    _columns = {'name': fields.char('Reason', size=64, required=True),
     'amount': fields.float('Amount', digits_compute=dp.get_precision('Account'), required=True)}

    def run(self, cr, uid, ids, context = None):
        if not context:
            context = dict()
        active_model = context.get('active_model', False) or False
        active_ids = context.get('active_ids', []) or []
        records = self.pool.get(active_model).browse(cr, uid, active_ids, context=context)
        return self._run(cr, uid, ids, records, context=context)

    def _run(self, cr, uid, ids, records, context = None):
        for box in self.browse(cr, uid, ids, context=context):
            for record in records:
                if not record.journal_id:
                    raise osv.except_osv(_('Error!'), _("Please check that the field 'Journal' is set on the Bank Statement"))
                if not record.journal_id.internal_account_id:
                    raise osv.except_osv(_('Error!'), _("Please check that the field 'Internal Transfers Account' is set on the payment method '%s'.") % (record.journal_id.name,))
                self._create_bank_statement_line(cr, uid, box, record, context=context)

        return {}

    def _create_bank_statement_line(self, cr, uid, box, record, context = None):
        values = self._compute_values_for_statement_line(cr, uid, box, record, context=context)
        return self.pool.get('account.bank.statement.line').create(cr, uid, values, context=context)


class CashBoxIn(CashBox):
    _name = 'cash.box.in'
    _columns = CashBox._columns.copy()
    _columns.update({'ref': fields.char('Reference', size=32)})

    def _compute_values_for_statement_line(self, cr, uid, box, record, context = None):
        return {'statement_id': record.id,
         'journal_id': record.journal_id.id,
         'account_id': record.journal_id.internal_account_id.id,
         'amount': box.amount or 0.0,
         'ref': '%s' % (box.ref or ''),
         'name': box.name}


CashBoxIn()

class CashBoxOut(CashBox):
    _name = 'cash.box.out'

    def _compute_values_for_statement_line(self, cr, uid, box, record, context = None):
        amount = box.amount or 0.0
        return {'statement_id': record.id,
         'journal_id': record.journal_id.id,
         'account_id': record.journal_id.internal_account_id.id,
         'amount': -amount if amount > 0.0 else amount,
         'name': box.name}


CashBoxOut()