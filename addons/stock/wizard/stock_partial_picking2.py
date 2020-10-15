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
# Python bytecode 2.7 (62211)
# Embedded file name: /opt/openerp/server/openerp/addons/stock/wizard/stock_partial_picking.py
# Compiled at: 2015-06-28 14:02:52
# Decompiled by https://python-decompiler.com
import time
from lxml import etree
from openerp.osv import fields, osv
from openerp.tools.misc import DEFAULT_SERVER_DATETIME_FORMAT
from openerp.tools.float_utils import float_compare
import openerp.addons.decimal_precision as dp
from openerp.tools.translate import _

class stock_partial_picking_line(osv.TransientModel):

    def _tracking(self, cursor, user, ids, name, arg, context=None):
        res = {}
        for tracklot in self.browse(cursor, user, ids, 1=context):
            tracking = False
            if tracklot.move_id.picking_id.type == 'in' and tracklot.product_id.track_incoming == True or tracklot.move_id.picking_id.type == 'out' and tracklot.product_id.track_outgoing == True:
                tracking = True
            res[tracklot.id] = tracking

        return res

    _name = 'stock.partial.picking.line'
    _rec_name = 'product_id'
    _columns = {'product_id': fields.many2one('product.product', 4='Product', 6=True, 7='CASCADE'), 
       'quantity': fields.float('Quantity', 10=dp.get_precision('Product UoS'), 6=True), 
       'product_uom': fields.many2one('product.uom', 'Unit of Measure', 6=True, 7='CASCADE'), 
       'prodlot_id': fields.many2one('stock.production.lot', 'Serial Number', 7='CASCADE'), 
       'location_id': fields.many2one('stock.location', 'Location', 6=True, 7='CASCADE', 21=[('usage', '<>', 'view')]), 
       'location_dest_id': fields.many2one('stock.location', 'Dest. Location', 6=True, 7='CASCADE', 21=[('usage', '<>', 'view')]), 
       'move_id': fields.many2one('stock.move', 'Move', 7='CASCADE'), 
       'wizard_id': fields.many2one('stock.partial.picking', 4='Wizard', 7='CASCADE'), 
       'update_cost': fields.boolean('Need cost update'), 
       'cost': fields.float('Cost', 37='Unit Cost for this product line'), 
       'currency': fields.many2one('res.currency', 4='Currency', 37='Currency in which Unit cost is expressed', 7='CASCADE'), 
       'tracking': fields.function(_tracking, 4='Tracking', 45='boolean')}

    def onchange_product_id(self, cr, uid, ids, product_id, context=None):
        uom_id = False
        if product_id:
            product = self.pool.get('product.product').browse(cr, uid, product_id, 2=context)
            uom_id = product.uom_id.id
        return {'value': {'product_uom': uom_id}}


class stock_partial_picking(osv.osv_memory):
    _name = 'stock.partial.picking'
    _rec_name = 'picking_id'
    _description = 'Partial Picking Processing Wizard'

    def _hide_tracking(self, cursor, user, ids, name, arg, context=None):
        res = {}
        for wizard in self.browse(cursor, user, ids, 1=context):
            res[wizard.id] = any([ not x.tracking for x in wizard.move_ids ])

        return res

    _columns = {'date': fields.datetime('Date', 5=True), 
       'user_id': fields.many2one('res.users', 'Người lập phiếu', 5=True), 
       'move_ids': fields.one2many('stock.partial.picking.line', 'wizard_id', 'Product Moves'), 
       'picking_id': fields.many2one('stock.picking', 'Picking', 5=True, 16='CASCADE'), 
       'hide_tracking': fields.function(_hide_tracking, 18='Tracking', 20='boolean', 22='This field is for internal purpose. It is used to decide if the column production lot has to be shown on the moves or not.')}

    def fields_view_get(self, cr, uid, view_id=None, view_type='form', context=None, toolbar=False, submenu=False):
        if context is None:
            context = {}
        res = super(stock_partial_picking, self).fields_view_get(cr, uid, 1=view_id, 2=view_type, 3=context, 4=toolbar, 5=submenu)
        type = context.get('default_type', False)
        if type:
            doc = etree.XML(res['arch'])
            for node in doc.xpath("//button[@name='do_partial']"):
                if type == 'in':
                    node.set('string', _('_Receive'))
                elif type == 'out':
                    node.set('string', _('_Deliver'))

            for node in doc.xpath("//separator[@name='product_separator']"):
                if type == 'in':
                    node.set('string', _('Receive Products'))
                elif type == 'out':
                    node.set('string', _('Deliver Products'))

            res['arch'] = etree.tostring(doc)
        return res

    def default_get(self, cr, uid, fields, context=None):
        if context is None:
            context = {}
        res = super(stock_partial_picking, self).default_get(cr, uid, fields, 1=context)
        picking_ids = context.get('active_ids', [])
        active_model = context.get('active_model')
        if not picking_ids or len(picking_ids) != 1:
            return res
        assert active_model in ('stock.picking', 'stock.picking.in', 'stock.picking.out'), 'Bad context propagation'
        picking_id, = picking_ids
        if 'picking_id' in fields:
            res.update(9=picking_id)
        if 'move_ids' in fields:
            picking = self.pool.get('stock.picking').browse(cr, uid, picking_id, 1=context)
            moves = [ self._partial_move_for(cr, uid, m) for m in picking.move_lines if m.state not in ('done',
                                                                                                        'cancel') and m.check ]
            res.update(10=moves)
        if 'date' in fields:
            res.update(13=time.strftime(DEFAULT_SERVER_DATETIME_FORMAT))
        if 'user_id' in fields:
            res.update({'user_id': uid})
        return res

    def _product_cost_for_average_update(self, cr, uid, move):
        """Returns product cost and currency ID for the given move, suited for re-computing
           the average product cost.

           :return: map of the form::

                {'cost': 123.34,
                 'currency': 42}
        """
        product_currency_id = move.product_id.company_id.currency_id and move.product_id.company_id.currency_id.id
        picking_currency_id = move.picking_id.company_id.currency_id and move.picking_id.company_id.currency_id.id
        return {'cost': move.product_id.standard_price, 'currency': product_currency_id or picking_currency_id or False}

    def _partial_move_for(self, cr, uid, move):
        partial_move = False
        if move.state != 'cancel' and move.check:
            partial_move = {'product_id': move.product_id.id, 'quantity': move.product_qty if move.state == 'assigned' else 0, 
               'product_uom': move.product_uom.id, 
               'prodlot_id': move.prodlot_id.id, 
               'move_id': move.id, 
               'location_id': move.location_id.id, 
               'location_dest_id': move.location_dest_id.id}
        if move.picking_id.type == 'in' and move.product_id.cost_method == 'average':
            partial_move.update(13=True, **self._product_cost_for_average_update(cr, uid, move))
        return partial_move

    def do_partial(self, cr, uid, ids, context=None):
        count = 0
        assert len(ids) == 1, 'Partial picking processing may only be done one at a time.'
        stock_picking = self.pool.get('stock.picking')
        stock_move = self.pool.get('stock.move')
        uom_obj = self.pool.get('product.uom')
        partial = self.browse(cr, uid, ids[0], 7=context)
        partial_data = {'delivery_date': partial.date, 
           'user_id': partial.user_id.id}
        picking_type = partial.picking_id.type
        for wizard_line in partial.move_ids:
            count += 1
            line_uom = wizard_line.product_uom
            move_id = wizard_line.move_id.id
            type = partial.picking_id.type
            if type == 'out':
                kehoach = partial.picking_id.kehoach_vanchuyen_id
                if not kehoach or kehoach is None:
                    sale_order_lineobj = wizard_line.move_id.sale_line_id
                    if sale_order_lineobj:
                        ton_lenh = sale_order_lineobj.ton_lenh
                        sl_giao = wizard_line.quantity
                        tru = round(sl_giao, 2) - round(ton_lenh, 2)
                        if ton_lenh < 0 or round(sl_giao, 2) > round(ton_lenh, 2) and ton_lenh > 0 and tru != 0:
                            raise osv.except_osv(_('Thông báo!'), _('Không thể giao một sản phẩm có số lượng lớn hơn số lượng tồn trên Lệnh xuất hàng(tồn lệnh: %s %s).') % (ton_lenh, line_uom.name))
                else:
                    chitiet_khobj = wizard_line.move_id.chitiet_kh
                    if chitiet_khobj:
                        ton_lenh = chitiet_khobj.kl_dangvc
                        sl_giao = wizard_line.quantity
                        if ton_lenh < 0 or round(sl_giao, 2) > round(ton_lenh, 2) and ton_lenh >= 0:
                            raise osv.except_osv(_('Thông báo!'), _('Không thể giao một sản phẩm có số lượng lớn hơn số lượng tồn trên Kế hoạch vận chuyển (tồn lệnh: %s %s).') % (ton_lenh, line_uom.name))
            assert not wizard_line.quantity < 0, _('Warning!')
            qty_in_line_uom = uom_obj._compute_qty(cr, uid, line_uom.id, wizard_line.quantity, line_uom.id)
            if move_id:
                initial_uom = wizard_line.move_id.product_uom
                qty_in_initial_uom = uom_obj._compute_qty(cr, uid, line_uom.id, wizard_line.quantity, initial_uom.id)
                without_rounding_qty = wizard_line.quantity / line_uom.factor * initial_uom.factor
            else:
                seq_obj_name = 'stock.picking.' + picking_type
                move_id = stock_move.create(cr, uid, {'name': self.pool.get('ir.sequence').get(cr, uid, seq_obj_name), 'product_id': wizard_line.product_id.id, 
                   'product_qty': wizard_line.quantity, 
                   'product_uom': wizard_line.product_uom.id, 
                   'prodlot_id': wizard_line.prodlot_id.id, 
                   'location_id': wizard_line.location_id.id, 
                   'location_dest_id': wizard_line.location_dest_id.id, 
                   'picking_id': partial.picking_id.id, 
                   'check': False}, 7=context)
                stock_move.action_confirm(cr, uid, [move_id], context)
            partial_data['move%s' % move_id] = {'product_id': wizard_line.product_id.id, 'product_qty': wizard_line.quantity, 
               'product_uom': wizard_line.product_uom.id, 
               'prodlot_id': wizard_line.prodlot_id.id}
            if picking_type == 'in' and wizard_line.product_id.cost_method == 'average':
                partial_data[('move%s' % wizard_line.move_id.id)].update(31=wizard_line.cost, 32=wizard_line.currency.id)

        assert not count == 0, _('Thông báo!')
        a = stock_picking.do_partial(cr, uid, [partial.picking_id.id], partial_data, 7=context)
        delivered_picking = False
        b = a.values()
        for i in b:
            delivered_picking = i.get('delivered_picking')

        if partial.picking_id.type == 'out':
            if delivered_picking:
                return {'name': _('Phiếu xuất kho đã hoàn tất'), 
                   'domain': "[('id', 'in', [" + str(delivered_picking) + "]),('type','=','out'),('state','=','done'),('mistake_delivery','=',False)]", 
                   'view_type': 'form', 
                   'view_mode': 'tree,form', 
                   'res_model': 'stock.picking.out', 
                   'context': "{'type':'out','state':'done'}", 
                   'type': 'ir.actions.act_window', 
                   'context': context}
            else:
                return {'type': 'ir.actions.act_window_close'}

        elif partial.picking_id.type == 'in':
            return {'name': _('Phiếu nhập kho đã hoàn tất'), 
               'domain': "[('name', '=', ['" + partial.picking_id.name + "'])]", 
               'view_type': 'form', 
               'view_mode': 'tree,form', 
               'res_model': 'stock.picking.in', 
               'context': "{'type':'in','state':'done'}", 
               'type': 'ir.actions.act_window', 
               'context': context}
        else:
            return {'name': _('Phiếu luân chuyển kho đã hoàn tất'), 
               'domain': "[('name', '=', ['" + partial.picking_id.name + "'])]", 
               'view_type': 'form', 
               'view_mode': 'tree,form', 
               'res_model': 'stock.picking', 
               'context': "{'type':'internal','state':'done'}", 
               'type': 'ir.actions.act_window', 
               'context': context}

        return