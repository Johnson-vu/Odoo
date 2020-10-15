﻿# -*- coding: utf-8 -*-
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
# Embedded file name: /opt/openerp/server/openerp/addons/stock/stock.py
# Compiled at: 2018-12-03 14:44:26
# Decompiled by https://python-decompiler.com
from datetime import datetime
from dateutil.relativedelta import relativedelta
import time
from operator import itemgetter
from itertools import groupby
from openerp.osv import fields, osv, orm
from openerp.tools.translate import _
from openerp import netsvc
from openerp import tools
from openerp.tools import float_compare, DEFAULT_SERVER_DATETIME_FORMAT
import openerp.addons.decimal_precision as dp
_logger = logging.getLogger(__name__)

class sequence_custormize_pickingout(osv.osv):
    _name = 'sequence.custormize.pickingout'

    def get_names(self, cr, uid, code, table_name, type, so):
        import datetime
        today = datetime.datetime.now()
        year = today.year
        cr.execute("select id,number_next,number_increment,prefix,suffix,padding from ir_sequence where code='" + code + "' and active=True")
        res = cr.dictfetchone()
        if res:
            prefix = len(res['prefix']) + 1
            query_d = 'select max(substr(name, ' + str(prefix) + ', ' + str(res['padding']) + ')::int) as max  from ' + table_name + " where type='out' and  loai_xuatkho = '" + str(type) + "' and (right(name,6)!='return' or right(name,7)!='trở lại') and  (left(name,3)='PXK' or left(name,4)='XKNB') and EXTRACT(year FROM create_date)= " + str(year)
            cr.execute(query_d)
            p_order_number = cr.dictfetchone()
            if p_order_number:
                if p_order_number['max']:
                    purchace_order_name_replace = str(p_order_number['max'])
                    i = 1
                    while i <= len(purchace_order_name_replace):
                        number = int(purchace_order_name_replace[:i])
                        if number > 0:
                            p_oder_number = int(purchace_order_name_replace[i - 1:])
                            p_order_number = p_oder_number + so
                            return res['prefix'] + '%%0%sd' % res['padding'] % p_order_number + '/' + str(year)
                            break
                        i += 1

            return res['prefix'] + '%%0%sd' % res['padding'] % 1 + '/' + str(year)
        else:
            return res['prefix'] + '%%0%sd' % res['padding'] % 1 + '/' + str(year)

    def get_name(self, cr, uid, code, table_name, type):
        import datetime
        today = datetime.datetime.now()
        year = today.year
        cr.execute("select id,number_next,number_increment,prefix,suffix,padding from ir_sequence where code='" + code + "' and active=True")
        res = cr.dictfetchone()
        if res:
            prefix = len(res['prefix']) + 1
            query_d = 'select max(substr(name, ' + str(prefix) + ', ' + str(res['padding']) + ')::int) as max  from ' + table_name + " where type='out' and  loai_xuatkho = '" + str(type) + "' and (right(name,6)!='return' or right(name,7)!='trở lại') and  (left(name,3)='PXK' or left(name,4)='XKNB') and EXTRACT(year FROM create_date)= " + str(year)
            cr.execute(query_d)
            p_order_number = cr.dictfetchone()
            if p_order_number:
                if p_order_number['max']:
                    purchace_order_name_replace = str(p_order_number['max'])
                    i = 1
                    while i <= len(purchace_order_name_replace):
                        number = int(purchace_order_name_replace[:i])
                        if number > 0:
                            p_oder_number = int(purchace_order_name_replace[i - 1:])
                            p_order_number = p_oder_number + 1
                            return res['prefix'] + '%%0%sd' % res['padding'] % p_order_number + '/' + str(year)
                            break
                        i += 1

            return res['prefix'] + '%%0%sd' % res['padding'] % 1 + '/' + str(year)
        else:
            return res['prefix'] + '%%0%sd' % res['padding'] % 1 + '/' + str(year)


sequence_custormize_pickingout()

class stock_incoterms(osv.osv):
    _name = 'stock.incoterms'
    _description = 'Incoterms'
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _columns = {'name': fields.char('Name', 5=64, 7=True, 8='onchange', 10='Incoterms are series of sales terms.They are used to divide transaction costs and responsibilities between buyer and seller and reflect state-of-the-art transportation practices.'), 'code': fields.char('Code', 5=3, 7=True, 8='onchange', 10='Code for Incoterms'), 
       'active': fields.boolean('Active', 8='onchange', 10='By unchecking the active field, you may hide an INCOTERM without deleting it.')}
    _defaults = {'active': True}


stock_incoterms()

class stock_journal(osv.osv):
    _name = 'stock.journal'
    _description = 'Stock Journal'
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _columns = {'name': fields.char('Stock Journal', 4=32, 6=True, 7='onchange'), 'user_id': fields.many2one('res.users', 'Responsible', 7='onchange')}
    _defaults = {'user_id': lambda s, c, u, ctx: u}


stock_journal()

class stock_location(osv.osv):
    _name = 'stock.location'
    _description = 'Location'
    _parent_name = 'location_id'
    _parent_store = True
    _parent_order = 'posz,name'
    _order = 'code'
    _inherit = ['mail.thread', 'ir.needaction_mixin']

    def name_get(self, cr, uid, ids, context=None):
        result = []
        if not all(ids):
            return result
        for pl in self.browse(cr, uid, ids, 1=context):
            name = ''
            code = pl.code
            if code:
                name = '[' + code + '] - '
            name += pl.name
            result.append((pl.id, name))

        return result

    def name_search(self, cr, user, name='', args=None, operator='ilike', context=None, limit=100):
        if not args:
            args = []
        if name:
            ids = self.search(cr, user, [('name', '=', name)] + args, 3=limit, 4=context)
            if not ids:
                ids = self.search(cr, user, [('code', '=', name)] + args, 3=limit, 4=context)
            if not ids:
                ids = set()
                ids.update(self.search(cr, user, args + [('code', operator, name)], 3=limit, 4=context))
                if not limit or len(ids) < limit:
                    ids.update(self.search(cr, user, args + [('name', operator, name)], 3=limit and limit - len(ids) or False, 4=context))
                ids = list(ids)
            if not ids:
                import re
                ptrn = re.compile('(\\[(.*?)\\])')
                res = ptrn.search(name)
                if res:
                    ids = self.search(cr, user, [('code', '=', res.group(2))] + args, 3=limit, 4=context)
        else:
            ids = self.search(cr, user, args, 3=limit, 4=context)
        result = self.name_get(cr, user, ids, 4=context)
        return result

    def _complete_name(self, cr, uid, ids, name, args, context=None):
        """ Forms complete name of location from parent location to child location.
        @return: Dictionary of values
        """
        res = {}
        for m in self.browse(cr, uid, ids, 1=context):
            names = [
             m.name]
            parent = m.location_id
            while parent:
                names.append(parent.name)
                parent = parent.location_id

            res[m.id] = (' / ').join(reversed(names))

        return res

    def _get_sublocations(self, cr, uid, ids, context=None):
        """ return all sublocations of the given stock locations (included) """
        return self.search(cr, uid, [('id', 'child_of', ids)], 3=context)

    def _product_value(self, cr, uid, ids, field_names, arg, context=None):
        """Computes stock value (real and virtual) for a product, as well as stock qty (real and virtual).
        @param field_names: Name of field
        @return: Dictionary of values
        """
        prod_id = context and context.get('product_id', False)
        if not prod_id:
            return dict([ (i, {}.fromkeys(field_names, 0.0)) for i in ids ])
        product_product_obj = self.pool.get('product.product')
        cr.execute('select distinct product_id, location_id from stock_move where location_id in %s', (tuple(ids),))
        dict1 = cr.dictfetchall()
        cr.execute('select distinct product_id, location_dest_id as location_id from stock_move where location_dest_id in %s', (tuple(ids),))
        dict2 = cr.dictfetchall()
        res_products_by_location = sorted(dict1 + dict2, 6=itemgetter('location_id'))
        products_by_location = dict((k, [ v['product_id'] for v in itr ]) for k, itr in groupby(res_products_by_location, itemgetter('location_id')))
        result = dict([ (i, {}.fromkeys(field_names, 0.0)) for i in ids ])
        result.update(dict([ (i, {}.fromkeys(field_names, 0.0)) for i in list(set([ aaa['location_id'] for aaa in res_products_by_location ])) ]))
        currency_id = self.pool.get('res.users').browse(cr, uid, uid).company_id.currency_id.id
        currency_obj = self.pool.get('res.currency')
        currency = currency_obj.browse(cr, uid, currency_id, 11=context)
        for loc_id, product_ids in products_by_location.items():
            if prod_id:
                product_ids = [
                 prod_id]
            c = (context or {}).copy()
            c['location'] = loc_id
            for prod in product_product_obj.browse(cr, uid, product_ids, 11=c):
                for f in field_names:
                    if f == 'stock_real':
                        if loc_id not in result:
                            result[loc_id] = {}
                        result[loc_id][f] += prod.qty_available
                    elif f == 'stock_virtual':
                        result[loc_id][f] += prod.virtual_available
                    elif f == 'stock_real_value':
                        amount = prod.qty_available * prod.standard_price
                        amount = currency_obj.round(cr, uid, currency, amount)
                        result[loc_id][f] += amount
                    elif f == 'stock_virtual_value':
                        amount = prod.virtual_available * prod.standard_price
                        amount = currency_obj.round(cr, uid, currency, amount)
                        result[loc_id][f] += amount

        return result

    _columns = {'name': fields.char('Location Name', 16=1000, 18=True, 19='onchange'), 'code': fields.char('Mã địa điểm', 16=64, 19='onchange'), 
       'active': fields.boolean('Active', 19='onchange', 25='By unchecking the active field, you may hide a location without deleting it.'), 
       'usage': fields.selection([('supplier', 'Supplier Location'),
               ('view', 'View'),
               ('internal', 'Internal Location'),
               ('customer', 'Customer Location'),
               ('inventory', 'Inventory'),
               ('procurement', 'Procurement'),
               ('production', 'Production'),
               ('transit', 'Transit Location for Inter-Companies Transfers')], 'Location Type', 18=True, 25="* Supplier Location: Virtual location representing the source location for products coming from your suppliers\n                       \n* View: Virtual location used to create a hierarchical structures for your warehouse, aggregating its child locations ; can't directly contain products\n                       \n* Internal Location: Physical locations inside your own warehouses,\n                       \n* Customer Location: Virtual location representing the destination location for products sent to your customers\n                       \n* Inventory: Virtual location serving as counterpart for inventory operations used to correct stock levels (Physical inventories)\n                       \n* Procurement: Virtual location serving as temporary counterpart for procurement operations when the source (supplier or production) is not known yet. This location should be empty when the procurement scheduler has finished running.\n                       \n* Production: Virtual counterpart location for production operations: this location consumes the raw material and produces finished products\n                      ", 46=True), 
       'complete_name': fields.function(_complete_name, 48='char', 16=256, 19='onchange', 51='Location Name', 52={'stock.location': (_get_sublocations, ['name', 'location_id'], 10)}), 
       'stock_real': fields.function(_product_value, 48='float', 51='Real Stock', 57='stock', 19='onchange'), 
       'stock_virtual': fields.function(_product_value, 48='float', 51='Virtual Stock', 57='stock', 19='onchange'), 
       'location_id': fields.many2one('stock.location', 'Parent Location', 46=True, 63='cascade', 19='onchange'), 
       'child_ids': fields.one2many('stock.location', 'location_id', 'Contains', 19='onchange'), 
       'chained_journal_id': fields.many2one('stock.journal', 'Chaining Journal', 19='onchange', 25='Inventory Journal in which the chained move will be written, if the Chaining Type is not Transparent (no journal is used if left empty)'), 
       'chained_location_id': fields.many2one('stock.location', 'Chained Location If Fixed', 19='onchange'), 
       'chained_location_type': fields.selection([('none', 'None'), ('customer', 'Customer'), ('fixed', 'Fixed Location')], 'Chained Location Type', 18=True, 19='onchange', 25='Determines whether this location is chained to another location, i.e. any incoming product in this location \nshould next go to the chained location. The chained location is determined according to the type :\n* None: No chaining at all\n* Customer: The chained location will be taken from the Customer Location field on the Partner form of the Partner that is specified in the Picking list of the incoming products.\n* Fixed Location: The chained location is taken from the next field: Chained Location if Fixed.'), 
       'chained_auto_packing': fields.selection([('auto', 'Automatic Move'), ('manual', 'Manual Operation'), ('transparent', 'Automatic No Step Added')], 'Chaining Type', 19='onchange', 25="This is used only if you select a chained location type.\nThe 'Automatic Move' value will create a stock move after the current one that will be validated automatically. With 'Manual Operation', the stock move has to be validated by a worker. With 'Automatic No Step Added', the location is replaced in the original move."), 
       'chained_picking_type': fields.selection([('out', 'Sending Goods'), ('in', 'Getting Goods'), ('internal', 'Internal')], 'Shipping Type', 19='onchange', 25='Shipping Type of the Picking List that will contain the chained move (leave empty to automatically detect the type based on the source and destination locations).'), 
       'chained_company_id': fields.many2one('res.company', 'Chained Company', 19='onchange', 25='The company the Picking List containing the chained move will belong to (leave empty to use the default company determination rules'), 
       'chained_delay': fields.integer('Chaining Lead Time', 19='onchange', 25='Delay between original move and chained move in days'), 
       'partner_id': fields.many2one('res.partner', 'Người sở hữu của địa điểm', 19='onchange', 25='Address of  customer or supplier.'), 
       'icon': fields.selection(tools.icons, 'Icon', 16=64, 19='onchange', 25='Icon show in  hierarchical tree view'), 
       'comment': fields.text('Additional Information', 19='onchange'), 
       'posx': fields.integer('Corridor (X)', 19='onchange', 25='Optional localization details, for information purpose only'), 
       'posy': fields.integer('Shelves (Y)', 19='onchange', 25='Optional localization details, for information purpose only'), 
       'posz': fields.integer('Height (Z)', 19='onchange', 25='Optional localization details, for information purpose only'), 
       'parent_left': fields.integer('Left Parent', 46=1, 19='onchange'), 
       'parent_right': fields.integer('Right Parent', 46=1, 19='onchange'), 
       'stock_real_value': fields.function(_product_value, 48='float', 19='onchange', 51='Real Stock Value', 57='stock', 127=dp.get_precision('Account')), 
       'stock_virtual_value': fields.function(_product_value, 48='float', 19='onchange', 51='Virtual Stock Value', 57='stock', 127=dp.get_precision('Account')), 
       'company_id': fields.many2one('res.company', 'Company', 46=1, 19='onchange', 25='Let this field empty if this location is shared between all companies'), 
       'scrap_location': fields.boolean('Scrap Location', 19='onchange', 25='Check this box to allow using this location to put scrapped/damaged goods.'), 
       'valuation_in_account_id': fields.many2one('account.account', 'Stock Valuation Account (Incoming)', 19='onchange', 140=[('type', '=', 'other')], 25='Used for real-time inventory valuation. When set on a virtual location (non internal type), this account will be used to hold the value of products being moved from an internal location into this location, instead of the generic Stock Output Account set on the product. This has no effect for internal locations.'), 
       'valuation_out_account_id': fields.many2one('account.account', 'Stock Valuation Account (Outgoing)', 19='onchange', 140=[('type', '=', 'other')], 25='Used for real-time inventory valuation. When set on a virtual location (non internal type), this account will be used to hold the value of products being moved out of this location and into an internal location, instead of the generic Stock Output Account set on the product. This has no effect for internal locations.'), 
       'partner_id_diadiem': fields.many2one('res.partner', 'Location Address', 19='onchange', 25='Address of  customer or supplier.'), 
       'loai_hinh': fields.selection([('kho_congty', 'Kho công ty'), ('kho_taptrung', 'Kho tập trung'), ('kho_daily', 'Kho đại lý')], 'Loại hình', 19='onchange'), 
       'allow': fields.boolean('Cho phép tồn kho âm', 19='onchange')}
    _defaults = {'active': True, 'usage': 'internal', 
       'chained_location_type': 'none', 
       'chained_auto_packing': 'manual', 
       'company_id': lambda self, cr, uid, c: self.pool.get('res.company')._company_default_get(cr, uid, 'stock.location', 3=c), 
       'posx': 0, 
       'posy': 0, 
       'posz': 0, 
       'icon': False, 
       'scrap_location': False}

    def chained_location_get(self, cr, uid, location, partner=None, product=None, context=None):
        """ Finds chained location
        @param location: Location id
        @param partner: Partner id
        @param product: Product id
        @return: List of values
        """
        result = None
        if location.chained_location_type == 'customer':
            if partner:
                result = partner.property_stock_customer
        elif location.chained_location_type == 'fixed':
            result = location.chained_location_id
        if result:
            return (result,
             location.chained_auto_packing,
             location.chained_delay,
             location.chained_journal_id and location.chained_journal_id.id or False,
             location.chained_company_id and location.chained_company_id.id or False,
             location.chained_picking_type,
             False)
        else:
            return result
            return

    def picking_type_get(self, cr, uid, from_location, to_location, context=None):
        """ Gets type of picking.
        @param from_location: Source location
        @param to_location: Destination location
        @return: Location type
        """
        result = 'internal'
        if from_location.usage == 'internal' and to_location and to_location.usage in ('customer',
                                                                                       'supplier'):
            result = 'out'
        elif from_location.usage in ('supplier', 'customer') and to_location.usage == 'internal':
            result = 'in'
        return result

    def _product_get_all_report(self, cr, uid, ids, product_ids=False, context=None):
        return self._product_get_report(cr, uid, ids, product_ids, context, 1=True)

    def _product_get_report(self, cr, uid, ids, product_ids=False, context=None, recursive=False):
        """ Finds the product quantity and price for particular location.
        @param product_ids: Ids of product
        @param recursive: True or False
        @return: Dictionary of values
        """
        if context is None:
            context = {}
        product_obj = self.pool.get('product.product')
        context['currency_id'] = self.pool.get('res.users').browse(cr, uid, uid, 3=context).company_id.currency_id.id
        context['compute_child'] = False
        if not product_ids:
            product_ids = product_obj.search(cr, uid, [], 3={'active_test': False})
        products = product_obj.browse(cr, uid, product_ids, 3=context)
        products_by_uom = {}
        products_by_id = {}
        for product in products:
            products_by_uom.setdefault(product.uom_id.id, [])
            products_by_uom[product.uom_id.id].append(product)
            products_by_id.setdefault(product.id, [])
            products_by_id[product.id] = product

        result = {}
        result['product'] = []
        for id in ids:
            quantity_total = 0.0
            total_price = 0.0
            for uom_id in products_by_uom.keys():
                fnc = self._product_get
                if recursive:
                    fnc = self._product_all_get
                ctx = context.copy()
                ctx['uom'] = uom_id
                qty = fnc(cr, uid, id, [ x.id for x in products_by_uom[uom_id] ], 3=ctx)
                for product_id in qty.keys():
                    if not qty[product_id]:
                        continue
                    product = products_by_id[product_id]
                    quantity_total += qty[product_id]
                    amount_unit = product.price_get('standard_price', 3=context)[product.id]
                    price = qty[product_id] * amount_unit
                    total_price += price
                    result['product'].append({'price': amount_unit, 'prod_name': product.name, 
                       'code': product.default_code, 
                       'variants': product.variants or '', 
                       'uom': product.uom_id.name, 
                       'prod_qty': qty[product_id], 
                       'price_value': price})

        result['total'] = quantity_total
        result['total_price'] = total_price
        return result

    def _product_get_multi_location(self, cr, uid, ids, product_ids=False, context=None, states=['done'], what=('in', 'out')):
        """
        @param product_ids: Ids of product
        @param states: List of states
        @param what: Tuple of
        @return:
        """
        product_obj = self.pool.get('product.product')
        if context is None:
            context = {}
        context.update({'states': states, 'what': what, 
           'location': ids})
        return product_obj.get_product_available(cr, uid, product_ids, 5=context)

    def _product_get(self, cr, uid, id, product_ids=False, context=None, states=None):
        """
        @param product_ids:
        @param states:
        @return:
        """
        if states is None:
            states = [
             'done']
        ids = id and [id] or []
        return self._product_get_multi_location(cr, uid, ids, product_ids, 2=context, 3=states)

    def _product_all_get(self, cr, uid, id, product_ids=False, context=None, states=None):
        if states is None:
            states = [
             'done']
        ids = id and [id] or []
        location_ids = self.search(cr, uid, [('location_id', 'child_of', ids)])
        return self._product_get_multi_location(cr, uid, location_ids, product_ids, context, states)

    def _product_virtual_get(self, cr, uid, id, product_ids=False, context=None, states=None):
        if states is None:
            states = [
             'done']
        return self._product_all_get(cr, uid, id, product_ids, context, ['confirmed',
         'waiting',
         'assigned',
         'done'])

    def _product_reserve(self, cr, uid, ids, product_id, product_qty, context=None, lock=False):
        """
        Attempt to find a quantity ``product_qty`` (in the product's default uom or the uom passed in ``context``) of product ``product_id``
        in locations with id ``ids`` and their child locations. If ``lock`` is True, the stock.move lines
        of product with id ``product_id`` in the searched location will be write-locked using Postgres's
        "FOR UPDATE NOWAIT" option until the transaction is committed or rolled back, to prevent reservin
        twice the same products.
        If ``lock`` is True and the lock cannot be obtained (because another transaction has locked some of
        the same stock.move lines), a log line will be output and False will be returned, as if there was
        not enough stock.
        
        :param product_id: Id of product to reserve
        :param product_qty: Quantity of product to reserve (in the product's default uom or the uom passed in ``context``)
        :param lock: if True, the stock.move lines of product with id ``product_id`` in all locations (and children locations) with ``ids`` will
                     be write-locked using postgres's "FOR UPDATE NOWAIT" option until the transaction is committed or rolled back. This is
                     to prevent reserving twice the same products.
        :param context: optional context dictionary: if a 'uom' key is present it will be used instead of the default product uom to
                        compute the ``product_qty`` and in the return value.
        :return: List of tuples in the form (qty, location_id) with the (partial) quantities that can be taken in each location to
                 reach the requested product_qty (``qty`` is expressed in the default uom of the product), of False if enough
                 products could not be found, or the lock could not be obtained (and ``lock`` was True).
        """
        result = []
        amount = 0.0
        if context is None:
            context = {}
        uom_obj = self.pool.get('product.uom')
        uom_rounding = self.pool.get('product.product').browse(cr, uid, product_id, 4=context).uom_id.rounding
        if context.get('uom'):
            uom_rounding = uom_obj.browse(cr, uid, context.get('uom'), 4=context).rounding
        for id in self.search(cr, uid, [('location_id', 'child_of', ids)]):
            if lock:
                try:
                    cr.execute('SAVEPOINT stock_location_product_reserve')
                    cr.execute("SELECT id FROM stock_move\n                                  WHERE product_id=%s AND\n                                          (\n                                            (location_dest_id=%s AND\n                                             location_id<>%s AND\n                                             state='done')\n                                            OR\n                                            (location_id=%s AND\n                                             location_dest_id<>%s AND\n                                             state in ('done', 'assigned'))\n                                          )\n                                  FOR UPDATE of stock_move NOWAIT", (product_id,
                     id,
                     id,
                     id,
                     id), 10=False)
                except Exception:
                    cr.execute('ROLLBACK TO stock_location_product_reserve')
                    _logger.warning('Failed attempt to reserve %s x product %s, likely due to another transaction already in progress. Next attempt is likely to work. Detailed error available at DEBUG level.', product_qty, product_id)
                    _logger.debug('Trace of the failed product reservation attempt: ', 14=True)
                    return False

            cr.execute("SELECT product_uom, sum(product_qty) AS product_qty\n                          FROM stock_move\n                          WHERE location_dest_id=%s AND\n                                location_id<>%s AND\n                                product_id=%s AND\n                                state='done'\n                          GROUP BY product_uom\n                       ", (id, id, product_id))
            results = cr.dictfetchall()
            cr.execute("SELECT product_uom,-sum(product_qty) AS product_qty\n                          FROM stock_move\n                          WHERE location_id=%s AND\n                                location_dest_id<>%s AND\n                                product_id=%s AND\n                                state in ('done', 'assigned')\n                          GROUP BY product_uom\n                       ", (id, id, product_id))
            results += cr.dictfetchall()
            total = 0.0
            results2 = 0.0
            for r in results:
                amount = uom_obj._compute_qty(cr, uid, r['product_uom'], r['product_qty'], context.get('uom', False))
                results2 += amount
                total += amount

            if total <= 0.0:
                continue
            amount = results2
            compare_qty = float_compare(amount, 0, 20=uom_rounding)
            if compare_qty == 1:
                if amount > min(total, product_qty):
                    amount = min(product_qty, total)
                result.append((amount, id))
                product_qty -= amount
                total -= amount
                if product_qty <= 0.0:
                    return result
                if total <= 0.0:
                    continue

        return False


stock_location()

class stock_tracking(osv.osv):
    _name = 'stock.tracking'
    _description = 'Packs'

    def checksum(sscc):
        salt = '31313131313131313'
        sum = 0
        for sscc_part, salt_part in zip(sscc, salt):
            sum += int(sscc_part) * int(salt_part)

        return (10 - sum % 10) % 10

    checksum = staticmethod(checksum)

    def make_sscc(self, cr, uid, context=None):
        sequence = self.pool.get('ir.sequence').get(cr, uid, 'stock.lot.tracking')
        try:
            return sequence + str(self.checksum(sequence))
        except Exception:
            return sequence

    _columns = {'name': fields.char('Pack Reference', 5=64, 7=True, 8=True, 9='By default, the pack reference is generated following the sscc standard. (Serial number + 1 check digit)'), 'active': fields.boolean('Active', 9='By unchecking the active field, you may hide a pack without deleting it.'), 
       'serial': fields.char('Additional Reference', 5=64, 8=True, 9='Other reference or serial number'), 
       'move_ids': fields.one2many('stock.move', 'tracking_id', 'Moves for this pack', 21=True), 
       'date': fields.datetime('Creation Date', 7=True)}
    _defaults = {'active': 1, 'name': make_sscc, 
       'date': lambda *a: time.strftime('%Y-%m-%d %H:%M:%S')}

    def name_search(self, cr, user, name, args=None, operator='ilike', context=None, limit=100):
        if not args:
            args = []
        ids = self.search(cr, user, [('serial', '=', name)] + args, 3=limit, 4=context)
        ids += self.search(cr, user, [('name', operator, name)] + args, 3=limit, 4=context)
        return self.name_get(cr, user, ids, context)

    def name_get(self, cr, uid, ids, context=None):
        """Append the serial to the name"""
        if not len(ids):
            return []
        res = [ (r['id'], r['serial'] and '%s [%s]' % (r['name'], r['serial']) or r['name']) for r in self.read(cr, uid, ids, ['name', 'serial'], 3=context) ]
        return res

    def unlink(self, cr, uid, ids, context=None):
        raise osv.except_osv(_('Error!'), _('You cannot remove a lot line.'))

    def action_traceability(self, cr, uid, ids, context=None):
        """ It traces the information of a product
        @param self: The object pointer.
        @param cr: A database cursor
        @param uid: ID of the user currently logged in
        @param ids: List of IDs selected
        @param context: A standard dictionary
        @return: A dictionary of values
        """
        return self.pool.get('action.traceability').action_traceability(cr, uid, ids, context)


stock_tracking()

class stock_picking(osv.osv):
    _name = 'stock.picking'
    _inherit = ['mail.thread']
    _description = 'Picking List'
    _order = 'id desc'

    def _set_maximum_date(self, cr, uid, ids, name, value, arg, context=None):
        """ Calculates planned date if it is greater than 'value'.
        @param name: Name of field
        @param value: Value of field
        @param arg: User defined argument
        @return: True or False
        """
        if not value:
            return False
        if isinstance(ids, (int, long)):
            ids = [
             ids]
        for pick in self.browse(cr, uid, ids, 1=context):
            sql_str = "update stock_move set\n                    date_expected='%s'\n                where\n                    picking_id=%d " % (value, pick.id)
            if pick.max_date:
                sql_str += " and (date_expected='" + pick.max_date + "')"
            cr.execute(sql_str)

        return True

    def _set_minimum_date(self, cr, uid, ids, name, value, arg, context=None):
        """ Calculates planned date if it is less than 'value'.
        @param name: Name of field
        @param value: Value of field
        @param arg: User defined argument
        @return: True or False
        """
        if not value:
            return False
        if isinstance(ids, (int, long)):
            ids = [
             ids]
        for pick in self.browse(cr, uid, ids, 1=context):
            sql_str = "update stock_move set\n                    date_expected='%s'\n                where\n                    picking_id=%s " % (value, pick.id)
            if pick.min_date:
                sql_str += " and (date_expected='" + pick.min_date + "')"
            cr.execute(sql_str)

        return True

    def get_min_max_date(self, cr, uid, ids, field_name, arg, context=None):
        """ Finds minimum and maximum dates for picking.
        @return: Dictionary of values
        """
        res = {}
        for id in ids:
            res[id] = {'min_date': False, 'max_date': False}

        if not ids:
            return res
        cr.execute('select\n                picking_id,\n                min(date_expected),\n                max(date_expected)\n            from\n                stock_move\n            where\n                picking_id IN %s\n            group by\n                picking_id', (tuple(ids),))
        for pick, dt1, dt2 in cr.fetchall():
            res[pick]['min_date'] = dt1
            res[pick]['max_date'] = dt2

        return res

    def _check_price(self, cr, uid, orders_line_list, p_product_id, sale_line_id):
        if len(orders_line_list) > 0:
            for line_id in orders_line_list:
                orderline = self.pool.get('stock.move').browse(cr, uid, line_id)
                prod_id = orderline.product_id.id
                p_sale_line_id = orderline.sale_line_id.id
                prodlot_id = False
                if orderline.prodlot_id:
                    prodlot_id = orderline.prodlot_id.id
                if prod_id == p_product_id and p_sale_line_id == sale_line_id:
                    return line_id

        return False

    def merge_move_line(self, cr, uid, order_id, context=None):
        picking_obj = self.browse(cr, uid, order_id, context)
        if picking_obj:
            move_lines = picking_obj.move_lines
            orders_line_list = []
            for line in move_lines:
                if line.product_id:
                    prod_id = line.product_id.id
                    if line.sale_line_id.id:
                        line_get = self._check_price(cr, uid, orders_line_list, prod_id, line.sale_line_id.id)
                        if line_get:
                            move1 = self.pool.get('stock.move').browse(cr, uid, line_get)
                            product_qty1 = move1.product_qty
                            product_qty2 = line.product_qty
                            self.pool.get('stock.move').write(cr, uid, line_get, {'product_qty': product_qty1 + product_qty2})
                            self.pool.get('stock.move').unlink(cr, uid, [line.id])
                        else:
                            orders_line_list.append(line.id)

        return True

    def create(self, cr, user, vals, context=None):
        if 'name' not in vals or vals.get('name') == '/':
            seq_obj_name = self._name
            vals['name'] = self.pool.get('ir.sequence').get(cr, user, seq_obj_name)
        new_id = super(stock_picking, self).create(cr, user, vals, context)
        self.merge_move_line(cr, user, new_id, 4=context)
        return new_id

    _columns = {'name': fields.char('Reference', 11=64, 13=True, 14={'done': [('readonly', True)], 'cancel': [
                         (
                          'readonly', True)]}), 
       'origin': fields.char('Source Document', 11=64, 14={'done': [('readonly', True)], 'cancel': [
                           (
                            'readonly', True)]}, 20='Reference of the document', 13=True), 
       'backorder_id': fields.many2one('stock.picking', 'Back Order of', 14={'done': [('readonly', True)], 'cancel': [
                                 (
                                  'readonly', True)]}, 20='If this shipment was split, then this field links to the shipment which contains the already processed part.', 13=True), 
       'type': fields.selection([('out', 'Sending Goods'), ('in', 'Getting Goods'), ('internal', 'Internal')], 'Shipping Type', 33=True, 13=True, 20='Shipping type specify, goods coming in or going out.', 14={'done': [('readonly', True)], 'cancel': [
                         (
                          'readonly', True)]}), 
       'note': fields.text('Notes', 14={'done': [('readonly', True)], 'cancel': [
                         (
                          'readonly', True)]}), 
       'stock_journal_id': fields.many2one('stock.journal', 'Stock Journal', 13=True, 14={'done': [('readonly', True)], 'cancel': [
                                     (
                                      'readonly', True)]}), 
       'location_id': fields.many2one('stock.location', 'Location', 15=True, 14={'draft': [('readonly', False)], 'confirmed': [
                                   (
                                    'readonly', False)], 
                       'assigned': [
                                  (
                                   'readonly', False)]}, 20='Keep empty if you produce at the location where the finished products are needed.Set a location if you produce at a fixed location. This can be a partner location if you subcontract the manufacturing operations.', 13=True), 
       'location_dest_id': fields.many2one('stock.location', 'Dest. Location', 14={'done': [('readonly', True)], 'cancel': [
                                     (
                                      'readonly', True)]}, 20='Location where the system will stock the finished products.', 13=True), 
       'move_type': fields.selection([('direct', 'Partial'), ('one', 'All at once')], 'Delivery Method', 33=True, 14={'done': [('readonly', True)], 'cancel': [
                              (
                               'readonly', True)]}, 20='It specifies goods to be deliver partially or all at once'), 
       'state': fields.selection([('draft', 'Draft'),
               ('cancel', 'Cancelled'),
               ('auto', 'Waiting Another Operation'),
               ('confirmed', 'Waiting Availability'),
               ('assigned', 'Ready to Transfer'),
               ('done', 'Transferred')], 'Status', 15=True, 13=True, 66='onchange', 20="\n            * Draft: not confirmed yet and will not be scheduled until confirmed\n\n            * Waiting Another Operation: waiting for another move to proceed before it becomes automatically available (e.g. in Make-To-Order flows)\n\n            * Waiting Availability: still waiting for the availability of products\n\n            * Ready to Transfer: products reserved, simply waiting for confirmation.\n\n            * Transferred: has been processed, can't be modified or cancelled anymore\n\n            * Cancelled: has been cancelled, can't be confirmed anymore"), 
       'min_date': fields.function(get_min_max_date, 70=_set_minimum_date, 71='min_max_date', 73=True, 35='datetime', 75='Scheduled Time', 13=1, 20='Scheduled time for the shipment to be processed'), 
       'date': fields.datetime('Creation Date', 20='Creation date, usually the time of the order.', 13=True, 14={'done': [('readonly', True)], 'cancel': [
                         (
                          'readonly', True)]}), 
       'date_done': fields.datetime('Ngày hoàn tất', 20='Date of Completion', 14={'done': [('readonly', True)], 'cancel': [
                              (
                               'readonly', True)]}), 
       'max_date': fields.function(get_min_max_date, 70=_set_maximum_date, 71='min_max_date', 73=True, 35='datetime', 75='Max. Expected Date', 13=2), 
       'move_lines': fields.one2many('stock.move', 'picking_id', 'Internal Moves', 14={'done': [('readonly', True)], 'cancel': [
                               (
                                'readonly', True)]}), 
       'product_id': fields.related('move_lines', 'product_id', 35='many2one', 95='product.product', 75='Product'), 
       'auto_picking': fields.boolean('Auto-Picking', 14={'done': [('readonly', True)], 'cancel': [
                                 (
                                  'readonly', True)]}), 
       'partner_id': fields.many2one('res.partner', 'Partner', 14={'done': [('readonly', True)], 'cancel': [
                               (
                                'readonly', True)]}), 
       'invoice_state': fields.selection([('invoiced', 'Invoiced'), ('2binvoiced', 'To Be Invoiced'), ('none', 'Not Applicable')], 'Invoice Control', 13=True, 33=True, 15=True, 66='onchange', 14={'draft': [('readonly', False)]}), 
       'company_id': fields.many2one('res.company', 'Company', 33=True, 13=True, 14={'done': [('readonly', True)], 'cancel': [
                               (
                                'readonly', True)]}), 
       'loai_xuatkho': fields.selection([('thongthuong', 'VAT'), ('noibo', 'Nội bộ')], 'Loại xuất kho'), 
       'tach_id': fields.many2one('stock.picking', 'Back Order of', 14={'done': [('readonly', True)], 'cancel': [
                            (
                             'readonly', True)]}, 20='If this shipment was split, then this field links to the shipment which contains the already processed part.', 13=True), 
       'tach_ids': fields.one2many('stock.picking', 'tach_id', 'Back Order of', 14={'done': [('readonly', True)], 'cancel': [
                             (
                              'readonly', True)]}, 20='If this shipment was split, then this field links to the shipment which contains the already processed part.', 13=True), 
       'backorder_ids': fields.one2many('stock.picking', 'backorder_id', 'Back Order of', 14={'done': [('readonly', True)], 'cancel': [
                                  (
                                   'readonly', True)]}, 20='If this shipment was split, then this field links to the shipment which contains the already processed part.', 13=True), 
       'nguoi_lap_phieu': fields.many2one('res.users', 'Người lập phiếu')}
    _defaults = {'loai_xuatkho': 'thongthuong', 'name': lambda self, cr, uid, context: '/', 
       'state': 'draft', 
       'move_type': 'direct', 
       'type': 'internal', 
       'invoice_state': '2binvoiced', 
       'date': lambda *a: time.strftime('%Y-%m-%d %H:%M:%S'), 
       'company_id': lambda self, cr, uid, c: self.pool.get('res.company')._company_default_get(cr, uid, 'stock.picking', 3=c)}

    def tach_phieu(self, cr, uid, ids, context=None):
        """ Confirm the inventory and writes its finished date
        @return: True
        """
        if context is None:
            context = {}
        id_item = []
        check = 0
        stock_move = self.pool.get('stock.move')
        for pick in self.browse(cr, uid, ids, context):
            pick_id = pick.id
            loai_xuatkho = pick.loai_xuatkho
            name_pick_new = pick.name
            seq_obj_name = 'stock.picking.' + loai_xuatkho
            location_id_start = False
            count = 0
            if pick_id:
                query_soluong = 'select count(*) as soluong,location_id from stock_move \n                    where  picking_id= ' + str(pick_id) + ' group by location_id'
                cr.execute(query_soluong)
                for check_soluong in cr.dictfetchall():
                    count += 1
                    location_id_start = check_soluong['location_id']

            if count > 1:
                self.write(cr, uid, ids, {'tach_id': ids[0]}, context)
                query_location = 'select location_id from stock_move \n                    where  picking_id= ' + str(pick_id) + ' group by location_id'
                cr.execute(query_location)
                for check_chitiet in cr.dictfetchall():
                    location_id_split = check_chitiet['location_id']
                    if location_id_start != location_id_split:
                        a = self.pool.get('sequence.custormize.pickingout').get_name(cr, uid, seq_obj_name, 'stock_picking', loai_xuatkho)
                        new_picking = self.create(cr, uid, {'name': a, 'state': 'done', 
                           'backorder_id': pick.backorder_id.id, 
                           'tach_id': pick.id, 
                           'origin': pick.origin, 
                           'date_done': pick.date_done, 
                           'min_date': pick.min_date, 
                           'date': pick.date, 
                           'partner_id': pick.partner_id.id, 
                           'stock_journal_id': pick.stock_journal_id.id, 
                           'move_type': pick.move_type, 
                           'company_id': pick.company_id.id, 
                           'invoice_state': '2binvoiced', 
                           'note': pick.note, 
                           'type': pick.type, 
                           'loai_xuatkho': pick.loai_xuatkho, 
                           'sale_id': pick.sale_id.id, 
                           'doitac_giaohang': pick.doitac_giaohang.id, 
                           'khoxuat_id': pick.khoxuat_id.id, 
                           'so_theo_doi_vc': pick.so_theo_doi_vc, 
                           'kehoach_vanchuyen_id': pick.kehoach_vanchuyen_id.id, 
                           'ma_vung': pick.ma_vung, 
                           'loai_xuatkho': pick.loai_xuatkho, 
                           'loai_vanchuyen': pick.loai_vanchuyen, 
                           'bang_kiem_soat': pick.bang_kiem_soat, 
                           'donvi_vanchuyen': pick.donvi_vanchuyen.id, 
                           'daidien_muahang': pick.daidien_muahang.id, 
                           'type_kho': pick.type_kho, 
                           'dai_dien': pick.dai_dien.id, 
                           'nguoi_lap_phieu': pick.nguoi_lap_phieu.id})
                        new_id = int(new_picking)
                        check += 1
                        for move_line_tach in self.browse(cr, uid, pick_id, 42=context).move_lines:
                            location_move = move_line_tach.location_id.id
                            if location_id_split == location_move:
                                stock_move.write(cr, uid, [move_line_tach.id], {'picking_id': new_id})

        if check > 0:
            return {'name': _('Phiếu xuất kho đã hoàn tất'), 'domain': "[('tach_id', 'in', [" + str(ids[0]) + '])]', 
               'view_type': 'form', 
               'view_mode': 'tree,form', 
               'res_model': 'stock.picking.out', 
               'context': "{'type':'out','state':'done'}", 
               'type': 'ir.actions.act_window', 
               'context': context}
        else:
            return True
            return

    def action_process(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        query_kh = "select * from stock_location where name='Customers' or name='Các khách hàng' "
        cr.execute(query_kh)
        for item_kh in cr.dictfetchall():
            kho_khach_hang = item_kh['id']

        string = matinh = ''
        for pick in self.browse(cr, uid, ids, context):
            if pick.type == 'out':
                type_kho = pick.type_kho
                loai_kho = ''
                if type_kho == 'kho_taptrung':
                    loai_kho = 'Kho tập trung'
                if type_kho == 'kho_daily':
                    loai_kho = 'Kho đại lý'
                if type_kho == 'kho_congty':
                    loai_kho = 'Kho công ty'
                loai_xuatkho = pick.loai_xuatkho
                partner_id = pick.partner_id.ma_quanly
                if partner_id:
                    left_code_kh = partner_id[:2] + '-'
                else:
                    left_code_kh = ''
                string += left_code_kh
                for move in pick.move_lines:
                    location_id = move.location_id.loai_hinh
                    assert not type_kho != location_id and move.state != 'cancel', _('Thông báo!')
                    doitac_giaohang = move.doitac_giaohang
                    if doitac_giaohang:
                        matinh = doitac_giaohang.state_id.code
                    if matinh != None:
                        string += matinh
                    location_id = move.location_id.id
                    if loai_xuatkho == 'noibo':
                        location_dest_id = move.location_dest_id.id
                        if location_dest_id == 9:
                            raise osv.except_osv(_('Thông báo!'), _('Địa điểm đích không được là %s .') % move.location_dest_id.name)
                    if type_kho == 'kho_taptrung' or type_kho == 'kho_daily':
                        if location_id == kho_khach_hang:
                            raise osv.except_osv(_('Thông báo!'), _('Vui lòng chọn địa điểm nguồn trên chi tiết giao hàng. Địa điểm nguồn đối với Kho đại lý và Kho tập trung phải khác %s.') % move.location_id.name)

            self.write(cr, uid, ids, {'ma_vung': string}, context)

        context.update({'active_model': self._name, 'active_ids': ids, 
           'active_id': len(ids) and ids[0] or False})
        return {'view_type': 'form', 'view_mode': 'form', 
           'res_model': 'stock.partial.picking', 
           'type': 'ir.actions.act_window', 
           'target': 'new', 
           'context': context, 
           'nodestroy': True}

    def copy(self, cr, uid, id, default=None, context=None):
        if default is None:
            default = {}
        default = default.copy()
        picking_obj = self.browse(cr, uid, id, 1=context)
        move_obj = self.pool.get('stock.move')
        if 'name' not in default or picking_obj.name == '/':
            seq_obj_name = 'stock.picking.' + picking_obj.type
            default['name'] = self.pool.get('ir.sequence').get(cr, uid, seq_obj_name)
            default['origin'] = ''
            default['backorder_id'] = False
        default['backorder_ids'] = []
        default['tong_khoiluong'] = 0
        default['tach_ids'] = []
        default['pvc_ids'] = []
        if 'invoice_state' not in default and picking_obj.invoice_state == 'invoiced':
            default['invoice_state'] = '2binvoiced'
        res = super(stock_picking, self).copy(cr, uid, id, default, context)
        if res:
            for move in picking_obj.move_lines:
                state = move.sale_line_id.state
                if state == 'cancel' or move.state == 'cancel':
                    move_obj.action_cancel(cr, uid, [move.id], context)
                    move_obj.write(cr, uid, [move.id], {'tracking_id': False, 'prodlot_id': False, 
                       'move_history_ids2': [
                                           (
                                            6, 0, [])], 
                       'move_history_ids': [
                                          (
                                           6, 0, [])]})
                else:
                    move_obj.write(cr, uid, [move.id], {'tracking_id': False, 'prodlot_id': False, 
                       'move_history_ids2': [
                                           (
                                            6, 0, [])], 
                       'move_history_ids': [
                                          (
                                           6, 0, [])]})

        return res

    def fields_view_get(self, cr, uid, view_id=None, view_type=False, context=None, toolbar=False, submenu=False):
        if view_type == 'form' and not view_id:
            mod_obj = self.pool.get('ir.model.data')
            if self._name == 'stock.picking.in':
                model, view_id = mod_obj.get_object_reference(cr, uid, 'stock', 'view_picking_in_form')
            if self._name == 'stock.picking.out':
                model, view_id = mod_obj.get_object_reference(cr, uid, 'stock', 'view_picking_out_form')
        return super(stock_picking, self).fields_view_get(cr, uid, 8=view_id, 9=view_type, 10=context, 11=toolbar, 12=submenu)

    def onchange_partner_in(self, cr, uid, ids, partner_id=None, context=None):
        return {}

    def action_explode(self, cr, uid, moves, context=None):
        """Hook to allow other modules to split the moves of a picking."""
        return moves

    def action_confirm(self, cr, uid, ids, context=None):
        """ Confirms picking.
        @return: True
        """
        pickings = self.browse(cr, uid, ids, 1=context)
        self.write(cr, uid, ids, {'state': 'confirmed'})
        todo = []
        for picking in pickings:
            for r in picking.move_lines:
                if r.state == 'draft':
                    todo.append(r.id)

        todo = self.action_explode(cr, uid, todo, context)
        if len(todo):
            self.pool.get('stock.move').write(cr, uid, todo, {'date': picking.date_done or time.strftime('%Y-%m-%d %H:%M:%S')}, 1=context)
            self.pool.get('stock.move').action_confirm(cr, uid, todo, 1=context)
        return True

    def test_auto_picking(self, cr, uid, ids):
        return True

    def action_assign(self, cr, uid, ids, *args):
        """ Changes state of picking to available if all moves are confirmed.
        @return: True
        """
        wf_service = netsvc.LocalService('workflow')
        for pick in self.browse(cr, uid, ids):
            if pick.state == 'draft':
                wf_service.trg_validate(uid, 'stock.picking', pick.id, 'button_confirm', cr)
            move_ids = [ x.id for x in pick.move_lines if x.state == 'confirmed' ]
            assert move_ids, _('Warning!')
            self.pool.get('stock.move').action_assign(cr, uid, move_ids)

        return True

    def force_assign(self, cr, uid, ids, *args):
        """ Changes state of picking to available if moves are confirmed or waiting.
        @return: True
        """
        wf_service = netsvc.LocalService('workflow')
        for pick in self.browse(cr, uid, ids):
            move_ids = [ x.id for x in pick.move_lines if x.state in ('confirmed',
                                                                      'waiting') ]
            self.pool.get('stock.move').force_assign(cr, uid, move_ids)
            wf_service.trg_write(uid, 'stock.picking', pick.id, cr)

        return True

    def draft_force_assign(self, cr, uid, ids, *args):
        """ Confirms picking directly from draft state.
        @return: True
        """
        wf_service = netsvc.LocalService('workflow')
        for pick in self.browse(cr, uid, ids):
            assert pick.move_lines, _('Error!')
            wf_service.trg_validate(uid, 'stock.picking', pick.id, 'button_confirm', cr)

        return True

    def draft_validate(self, cr, uid, ids, context=None):
        """ Validates picking directly from draft state.
        @return: True
        """
        string = ''
        wf_service = netsvc.LocalService('workflow')
        self.draft_force_assign(cr, uid, ids)
        for pick in self.browse(cr, uid, ids, 3=context):
            if pick.type == 'out':
                partner_id = pick.partner_id.ma_quanly
                if partner_id:
                    left_code_kh = partner_id[:2] + '-'
                else:
                    left_code_kh = ''
                string += left_code_kh
                doitac_giaohang = pick.doitac_giaohang
                if doitac_giaohang:
                    matinh = doitac_giaohang.state_id.code
                    if matinh:
                        string += matinh
                self.write(cr, uid, ids, {'ma_vung': string}, context)
            move_ids = [ x.id for x in pick.move_lines ]
            self.pool.get('stock.move').write(cr, uid, move_ids, {'date': pick.date_done or time.strftime('%Y-%m-%d %H:%M:%S')}, 3=context)
            self.pool.get('stock.move').force_assign(cr, uid, move_ids)
            wf_service.trg_write(uid, 'stock.picking', pick.id, cr)

        return self.action_process(cr, uid, ids, 3=context)

    def cancel_assign(self, cr, uid, ids, *args):
        """ Cancels picking and moves.
        @return: True
        """
        wf_service = netsvc.LocalService('workflow')
        for pick in self.browse(cr, uid, ids):
            move_ids = [ x.id for x in pick.move_lines ]
            self.pool.get('stock.move').cancel_assign(cr, uid, move_ids)
            wf_service.trg_write(uid, 'stock.picking', pick.id, cr)

        return True

    def action_assign_wkf(self, cr, uid, ids, context=None):
        """ Changes picking state to assigned.
        @return: True
        """
        self.write(cr, uid, ids, {'state': 'assigned'})
        return True

    def test_finished(self, cr, uid, ids):
        """ Tests whether the move is in done or cancel state or not.
        @return: True or False
        """
        move_ids = self.pool.get('stock.move').search(cr, uid, [('picking_id', 'in', ids)])
        for move in self.pool.get('stock.move').browse(cr, uid, move_ids):
            if move.state not in ('done', 'cancel'):
                if move.product_qty != 0.0:
                    return False
                move.write({'state': 'done'})

        return True

    def test_assigned(self, cr, uid, ids):
        """ Tests whether the move is in assigned state or not.
        @return: True or False
        """
        ok = True
        for pick in self.browse(cr, uid, ids):
            mt = pick.move_type
            if pick.type == 'in':
                if all([ x.state != 'waiting' for x in pick.move_lines ]):
                    return True
            for move in pick.move_lines:
                if move.state in ('confirmed', 'draft') and mt == 'one':
                    return False
                if mt == 'direct' and move.state == 'assigned' and move.product_qty:
                    return True
                ok = ok and move.state in ('cancel', 'done', 'assigned')

        return ok

    def action_cancel(self, cr, uid, ids, context=None):
        """ Changes picking state to cancel.
        @return: True
        """
        for pick in self.browse(cr, uid, ids, 1=context):
            ids2 = [ move.id for move in pick.move_lines ]
            self.pool.get('stock.move').action_cancel(cr, uid, ids2, context)

        self.write(cr, uid, ids, {'state': 'cancel', 'invoice_state': 'none'})
        return True

    def action_done(self, cr, uid, ids, context=None):
        """Changes picking state to done.
        
        This method is called at the end of the workflow by the activity "done".
        @return: True
        """
        date_done = time.strftime('%Y-%m-%d %H:%M:%S')
        self.write(cr, uid, ids, {'state': 'done'})
        return True

    def action_move(self, cr, uid, ids, context=None):
        """Process the Stock Moves of the Picking
        
        This method is called by the workflow by the activity "move".
        Normally that happens when the signal button_done is received (button 
        "Done" pressed on a Picking view). 
        @return: True
        """
        for pick in self.browse(cr, uid, ids, 1=context):
            todo = []
            for move in pick.move_lines:
                if move.state == 'draft':
                    self.pool.get('stock.move').action_confirm(cr, uid, [move.id], 1=context)
                    todo.append(move.id)
                elif move.state in ('assigned', 'confirmed'):
                    todo.append(move.id)

            if len(todo):
                self.pool.get('stock.move').action_done(cr, uid, todo, 1=context)

        return True

    def get_currency_id(self, cr, uid, picking):
        return False

    def _get_partner_to_invoice(self, cr, uid, picking, context=None):
        """ Gets the partner that will be invoiced
            Note that this function is inherited in the sale and purchase modules
            @param picking: object of the picking for which we are selecting the partner to invoice
            @return: object of the partner to invoice
        """
        return picking.partner_id and picking.partner_id.id

    def _get_comment_invoice(self, cr, uid, picking):
        """
        @return: comment string for invoice
        """
        return picking.note or ''

    def _get_price_unit_invoice(self, cr, uid, move_line, type, context=None):
        """ Gets price unit for invoice
        @param move_line: Stock move lines
        @param type: Type of invoice
        @return: The price unit for the move line
        """
        if context is None:
            context = {}
        if type in ('in_invoice', 'in_refund'):
            context['currency_id'] = move_line.company_id.currency_id.id
            amount_unit = move_line.product_id.price_get('standard_price', 5=context)[move_line.product_id.id]
            return amount_unit
        else:
            return move_line.product_id.list_price
            return

    def _get_discount_invoice(self, cr, uid, move_line):
        """Return the discount for the move line"""
        return 0.0

    def _get_taxes_invoice(self, cr, uid, move_line, type):
        """ Gets taxes on invoice
        @param move_line: Stock move lines
        @param type: Type of invoice
        @return: Taxes Ids for the move line
        """
        if type in ('in_invoice', 'in_refund'):
            taxes = move_line.product_id.supplier_taxes_id
        else:
            taxes = move_line.product_id.taxes_id
        if move_line.picking_id and move_line.picking_id.partner_id and move_line.picking_id.partner_id.id:
            return self.pool.get('account.fiscal.position').map_tax(cr, uid, move_line.picking_id.partner_id.property_account_position, taxes)
        else:
            return map(lambda x: x.id, taxes)

    def _get_account_analytic_invoice(self, cr, uid, picking, move_line):
        return False

    def _invoice_line_hook(self, cr, uid, move_line, invoice_line_id):
        """Call after the creation of the invoice line"""
        pass

    def _invoice_hook(self, cr, uid, picking, invoice_id):
        """Call after the creation of the invoice"""
        pass

    def _get_invoice_type(self, pick):
        src_usage = dest_usage = None
        inv_type = None
        if pick.invoice_state == '2binvoiced':
            if pick.move_lines:
                src_usage = pick.move_lines[0].location_id.usage
                dest_usage = pick.move_lines[0].location_dest_id.usage
            if pick.type == 'out' and dest_usage == 'supplier':
                inv_type = 'in_refund'
            elif pick.type == 'out' and dest_usage == 'customer':
                inv_type = 'out_invoice'
            elif pick.type == 'in' and src_usage == 'supplier':
                inv_type = 'in_invoice'
            elif pick.type == 'in' and src_usage == 'customer':
                inv_type = 'out_refund'
            else:
                inv_type = 'out_invoice'
        return inv_type

    def _prepare_invoice_group(self, cr, uid, picking, partner, invoice, context=None):
        """ Builds the dict for grouped invoices
            @param picking: picking object
            @param partner: object of the partner to invoice (not used here, but may be usefull if this function is inherited)
            @param invoice: object of the invoice that we are updating
            @return: dict that will be used to update the invoice
        """
        comment = self._get_comment_invoice(cr, uid, picking)
        return {'name': (invoice.name or '') + ', ' + (picking.name or ''), 'origin': (invoice.origin or '') + ', ' + (picking.name or '') + (picking.origin and ':' + picking.origin or ''), 
           'comment': comment and (invoice.comment and invoice.comment + '\n' + comment or comment) or invoice.comment and invoice.comment or '', 
           'date_invoice': context.get('date_inv', False), 
           'user_id': uid}

    def _prepare_invoice(self, cr, uid, picking, partner, inv_type, journal_id, context=None):
        """ Builds the dict containing the values for the invoice
            @param picking: picking object
            @param partner: object of the partner to invoice
            @param inv_type: type of the invoice ('out_invoice', 'in_invoice', ...)
            @param journal_id: ID of the accounting journal
            @return: dict that will be used to create the invoice object
        """
        if isinstance(partner, int):
            partner = self.pool.get('res.partner').browse(cr, uid, partner, 2=context)
        if inv_type in ('out_invoice', 'out_refund'):
            account_id = partner.property_account_receivable.id
            payment_term = partner.property_payment_term.id or False
        else:
            account_id = partner.property_account_payable.id
            payment_term = partner.property_supplier_payment_term.id or False
        comment = self._get_comment_invoice(cr, uid, picking)
        lxh = km = False
        if picking.sale_id:
            lxh = picking.sale_id.id
            km = picking.sale_id.hinhthuc_khuyenmai
            phieuxuat = self.pool.get('sale.order').browse(cr, uid, picking.sale_id.id)
            loai_hoadon = False
            loai_lenh_xuat = phieuxuat.loai_lenh_xuat
            if loai_lenh_xuat == 'vat':
                loai_hoadon = 'thongthuong'
            else:
                loai_hoadon = 'noibo'
        else:
            loai_hoadon = False
            lxh = False
            km = False
        invoice_vals = {'name': picking.name, 'origin': (picking.name or '') + (picking.origin and ':' + picking.origin or ''), 'type': inv_type, 
           'account_id': account_id, 
           'partner_id': partner.id, 
           'comment': comment, 
           'payment_term': payment_term, 
           'fiscal_position': partner.property_account_position.id, 
           'date_invoice': context.get('date_inv', False), 
           'company_id': picking.company_id.id, 
           'user_id': uid, 
           'lenh_xuat_hang_id': lxh, 
           'hinh_thuc_khuyenmai': km, 
           'loai_hoadon': loai_hoadon, 
           'lenh_xuat_kho_id': picking.id, 
           'daidien_muahang': picking.daidien_muahang.id}
        cur_id = self.get_currency_id(cr, uid, picking)
        if cur_id:
            invoice_vals['currency_id'] = cur_id
        if journal_id:
            invoice_vals['journal_id'] = journal_id
        return invoice_vals

    def _prepare_invoice_line(self, cr, uid, group, picking, move_line, invoice_id, invoice_vals, context=None):
        """ Builds the dict containing the values for the invoice line
            @param group: True or False
            @param picking: picking object
            @param: move_line: move_line object
            @param: invoice_id: ID of the related invoice
            @param: invoice_vals: dict used to created the invoice
            @return: dict that will be used to create the invoice line
        """
        if group:
            mv = '- %s' % move_line.name
            name = (picking.name or '') + '%s ' % mv
        else:
            name = move_line.name
        origin = move_line.picking_id.name or ''
        if move_line.picking_id.origin:
            origin += ':' + move_line.picking_id.origin
        if invoice_vals['type'] in ('out_invoice', 'out_refund'):
            account_id = move_line.product_id.property_account_income.id
            if not account_id:
                account_id = move_line.product_id.categ_id.property_account_income_categ.id
        else:
            account_id = move_line.product_id.property_account_expense.id
            if not account_id:
                account_id = move_line.product_id.categ_id.property_account_expense_categ.id
        if invoice_vals['fiscal_position']:
            fp_obj = self.pool.get('account.fiscal.position')
            fiscal_position = fp_obj.browse(cr, uid, invoice_vals['fiscal_position'], 10=context)
            account_id = fp_obj.map_account(cr, uid, fiscal_position, account_id)
        uos_id = move_line.product_uos and move_line.product_uos.id or False
        if not uos_id and invoice_vals['type'] in ('out_invoice', 'out_refund'):
            uos_id = move_line.product_uom.id
        return {'name': name, 'origin': origin, 
           'invoice_id': invoice_id, 
           'uos_id': uos_id, 
           'product_id': move_line.product_id.id, 
           'account_id': account_id, 
           'price_unit': self._get_price_unit_invoice(cr, uid, move_line, invoice_vals['type']), 
           'discount': self._get_discount_invoice(cr, uid, move_line), 
           'quantity': move_line.product_qty, 
           'invoice_line_tax_id': [
                                 (
                                  6, 0, self._get_taxes_invoice(cr, uid, move_line, invoice_vals['type']))], 
           'account_analytic_id': self._get_account_analytic_invoice(cr, uid, picking, move_line)}

    def action_invoice_create(self, cr, uid, ids, journal_id=False, group=False, type='out_invoice', context=None):
        """ Creates invoice based on the invoice state selected for picking.
        @param journal_id: Id of journal
        @param group: Whether to create a group invoice or not
        @param type: Type invoice to be created
        @return: Ids of created invoices for the pickings
        """
        if context is None:
            context = {}
        invoice_obj = self.pool.get('account.invoice')
        invoice_line_obj = self.pool.get('account.invoice.line')
        partner_obj = self.pool.get('res.partner')
        invoices_group = {}
        res = {}
        inv_type = type
        for picking in self.browse(cr, uid, ids, 4=context):
            count = 0
            query_soluong = 'select distinct location_id from stock_move \n                where  picking_id= ' + str(picking.id)
            cr.execute(query_soluong)
            for check_soluong in cr.dictfetchall():
                count += 1

            assert not count > 1, _('Cảnh báo!')
            if picking.invoice_state != '2binvoiced':
                continue
            partner = self._get_partner_to_invoice(cr, uid, picking, 4=context)
            if isinstance(partner, int):
                partner = partner_obj.browse(cr, uid, [partner], 4=context)[0]
            assert partner, _('Error, no partner!')
            if not inv_type:
                inv_type = self._get_invoice_type(picking)
            if group and partner.id in invoices_group:
                invoice_id = invoices_group[partner.id]
                invoice = invoice_obj.browse(cr, uid, invoice_id)
                invoice_vals_group = self._prepare_invoice_group(cr, uid, picking, partner, invoice, 4=context)
                invoice_obj.write(cr, uid, [invoice_id], invoice_vals_group, 4=context)
            else:
                invoice_vals = self._prepare_invoice(cr, uid, picking, partner, inv_type, journal_id, 4=context)
                invoice_id = invoice_obj.create(cr, uid, invoice_vals, 4=context)
                invoices_group[partner.id] = invoice_id
            res[picking.id] = invoice_id
            for move_line in picking.move_lines:
                if move_line.state == 'cancel':
                    continue
                if move_line.scrapped:
                    continue
                vals = self._prepare_invoice_line(cr, uid, group, picking, move_line, invoice_id, invoice_vals, 4=context)
                if vals:
                    invoice_line_id = invoice_line_obj.create(cr, uid, vals, 4=context)
                    self._invoice_line_hook(cr, uid, move_line, invoice_line_id)

            invoice_obj.button_compute(cr, uid, [invoice_id], 4=context, 14=inv_type in ('in_invoice',
                                                                                         'in_refund'))
            self.write(cr, uid, [picking.id], {'invoice_state': 'invoiced', 'hoa_don_id': invoice_id}, 4=context)
            self._invoice_hook(cr, uid, picking, invoice_id)

        self.write(cr, uid, res.keys(), {'invoice_state': 'invoiced', 'hoa_don_id': invoice_id}, 4=context)
        return res

    def test_done(self, cr, uid, ids, context=None):
        """ Test whether the move lines are done or not.
        @return: True or False
        """
        ok = False
        for pick in self.browse(cr, uid, ids, 1=context):
            if not pick.move_lines:
                return True
            for move in pick.move_lines:
                if move.state not in ('cancel', 'done'):
                    return False
                if move.state == 'done':
                    ok = True

        return ok

    def test_cancel(self, cr, uid, ids, context=None):
        """ Test whether the move lines are canceled or not.
        @return: True or False
        """
        for pick in self.browse(cr, uid, ids, 1=context):
            for move in pick.move_lines:
                if move.state not in ('cancel', ):
                    return False

        return True

    def allow_cancel(self, cr, uid, ids, context=None):
        for pick in self.browse(cr, uid, ids, 1=context):
            nguoilap = pick.nguoi_lap_phieu
            if nguoilap:
                if nguoilap.id != uid:
                    raise osv.except_osv(_('Thông báo!'), _('Bạn không có quyền hủy PXK. Vui lòng liên hệ với người lập phiếu: %s để được hủy PXK.') % nguoilap.name)
            if not pick.move_lines:
                return True
            for move in pick.move_lines:
                assert not move.state == 'done', _('Error!')

        return True

    def unlink(self, cr, uid, ids, context=None):
        move_obj = self.pool.get('stock.move')
        if context is None:
            context = {}
        for pick in self.browse(cr, uid, ids, 2=context):
            if pick.state in ('done', 'cancel'):
                raise osv.except_osv(_('Error!'), _('You cannot remove the picking which is in %s state!') % (pick.state,))
            else:
                ids2 = [ move.id for move in pick.move_lines ]
                ctx = context.copy()
                ctx.update({'call_unlink': True})
                if pick.state != 'draft':
                    move_obj.action_cancel(cr, uid, ids2, ctx)
                move_obj.unlink(cr, uid, ids2, ctx)

        return super(stock_picking, self).unlink(cr, uid, ids, 2=context)

    def _product_available(self, cr, uid, product_id, location_ids, context=None):
        """ Finds the incoming and outgoing quantity of product.
        @return: Dictionary of values
        """
        location_obj = self.pool.get('stock.location')
        move_obj = self.pool.get('stock.move')
        uom_obj = self.pool.get('product.uom')
        datas = {}
        res = {}
        qty = 0
        for location in location_ids:
            res[location] = {}
            move_ids = move_obj.search(cr, uid, ['|',
             (
              'location_dest_id', '=', location),
             (
              'location_id', '=', location),
             ('state', '=', 'done')], 11=context)
            for move in move_obj.browse(cr, uid, move_ids, 11=context):
                lot_id = move.prodlot_id.id
                prod_id = move.product_id.id
                if move.product_id.id == product_id:
                    if move.location_dest_id.id != move.location_id.id:
                        if move.location_dest_id.id == location:
                            qty = uom_obj._compute_qty(cr, uid, move.product_uom.id, move.product_qty, move.product_id.uom_id.id)
                        else:
                            qty = -uom_obj._compute_qty(cr, uid, move.product_uom.id, move.product_qty, move.product_id.uom_id.id)
                        if datas.get((prod_id, lot_id)):
                            qty += datas[(prod_id, lot_id)]['product_qty']
                        datas[(prod_id, lot_id)] = {'product_id': prod_id, 'location_id': location, 'product_qty': qty, 
                           'product_uom': move.product_id.uom_id.id, 
                           'prod_lot_id': lot_id}

        return qty

    def do_partial(self, cr, uid, ids, partial_datas, context=None):
        """ Makes partial picking and moves done.
        @param partial_datas : Dictionary containing details of partial picking
                          like partner_id, partner_id, delivery_date,
                          delivery moves with product_id, product_qty, uom
        @return: Dictionary of values
        """
        if context is None:
            context = {}
        else:
            context = dict(context)
        res = {}
        move_obj = self.pool.get('stock.move')
        product_obj = self.pool.get('product.product')
        currency_obj = self.pool.get('res.currency')
        uom_obj = self.pool.get('product.uom')
        sequence_obj = self.pool.get('ir.sequence')
        name_pick = False
        wf_service = netsvc.LocalService('workflow')
        for pick in self.browse(cr, uid, ids, 7=context):
            loai_xuatkho = pick.loai_xuatkho
            seq_obj_name = 'stock.picking.' + loai_xuatkho
            new_picking = None
            name_pick = pick.name
            complete, too_many, too_few = [], [], []
            move_product_qty, prodlot_ids, product_avail, partial_qty, product_uoms = ({}, {}, {}, {}, {})
            for move in pick.move_lines:
                if move.state in ('done', 'cancel'):
                    continue
                partial_data = partial_datas.get('move%s' % move.id, {})
                product_qty = partial_data.get('product_qty', 0.0)
                move_product_qty[move.id] = product_qty
                product_uom = partial_data.get('product_uom', False)
                product_price = partial_data.get('product_price', 0.0)
                product_currency = partial_data.get('product_currency', False)
                prodlot_id = partial_data.get('prodlot_id')
                prodlot_ids[move.id] = prodlot_id
                product_uoms[move.id] = product_uom
                partial_qty[move.id] = uom_obj._compute_qty(cr, uid, product_uoms[move.id], product_qty, move.product_uom.id)
                if move.product_qty == partial_qty[move.id]:
                    product_id = move.product_id.id
                    tonkho = self._product_available(cr, uid, product_id, [move.location_id.id], context)
                    a = move.location_id.name
                    if move.location_id.allow == False:
                        if round(product_qty, 4) > round(tonkho, 4):
                            raise osv.except_osv(_('Lỗi!'), _('Sản phẩm trong kho %s không đủ để thực hiện việc giao hàng!') % a)
                    complete.append(move)
                elif move.product_qty > partial_qty[move.id]:
                    too_few.append(move)
                else:
                    too_many.append(move)
                if pick.type == 'in' and move.product_id.cost_method == 'average':
                    product = product_obj.browse(cr, uid, move.product_id.id)
                    move_currency_id = move.company_id.currency_id.id
                    context['currency_id'] = move_currency_id
                    qty = uom_obj._compute_qty(cr, uid, product_uom, product_qty, product.uom_id.id)
                    if product.id in product_avail:
                        product_avail[product.id] += qty
                    else:
                        product_avail[product.id] = product.qty_available
                    if qty > 0:
                        new_price = currency_obj.compute(cr, uid, product_currency, move_currency_id, product_price)
                        new_price = uom_obj._compute_price(cr, uid, product_uom, new_price, product.uom_id.id)
                        if product.qty_available <= 0:
                            new_std_price = new_price
                        else:
                            amount_unit = product.price_get('standard_price', 7=context)[product.id]
                            new_std_price = (amount_unit * product_avail[product.id] + new_price * qty) / (product_avail[product.id] + qty)
                        product_obj.write(cr, uid, [product.id], {'standard_price': new_std_price})
                        move_obj.write(cr, uid, [move.id], {'price_unit': product_price, 'price_currency_id': product_currency, 
                           'check': False, 
                           'date': partial_datas.get('delivery_date')})

            for move in too_few:
                product_qty = move_product_qty[move.id]
                if not new_picking:
                    new_picking_name = pick.name
                    string = matinh = ''
                    partner_id = pick.partner_id.ma_quanly
                    if partner_id:
                        left_code_kh = partner_id[:2] + '-'
                    else:
                        left_code_kh = ''
                    string += left_code_kh
                    for moves in pick.move_lines:
                        doitac_giaohang = moves.doitac_giaohang
                        if doitac_giaohang:
                            matinh = doitac_giaohang.state_id.code
                        if matinh != None:
                            string += matinh

                    fist_1 = name_pick[:3]
                    if fist_1 == 'OUT':
                        name_new = self.pool.get('sequence.custormize.pickingout').get_name(cr, uid, seq_obj_name, 'stock_picking', loai_xuatkho)
                    else:
                        name_new = self.pool.get('ir.sequence').get(cr, uid, 'stock.picking.in')
                    new_picking = self.copy(cr, uid, pick.id, {'date_done': partial_datas.get('delivery_date'), 'date': partial_datas.get('delivery_date'), 
                       'move_lines': [], 'state': 'draft', 
                       'ma_vung': matinh, 
                       'name': name_new, 
                       'nguoi_lap_phieu': partial_datas.get('user_id') or uid})
                    self.write(cr, uid, [pick.id], {'ma_vung': False, 'daidien_muahang': False, 
                       'bang_kiem_soat': False, 
                       'date_done': False, 
                       'date': partial_datas.get('delivery_date'), 
                       'check': False})
                if product_qty != 0:
                    defaults = {'product_qty': product_qty, 'product_uos_qty': product_qty, 'picking_id': new_picking, 
                       'state': 'assigned', 
                       'move_dest_id': False, 
                       'price_unit': move.price_unit, 
                       'product_uom': product_uoms[move.id], 
                       'date': partial_datas.get('delivery_date'), 
                       'check': False}
                    product_id = move.product_id.id
                    tonkho = self._product_available(cr, uid, product_id, [move.location_id.id], context)
                    if move.location_id.allow == False:
                        if round(product_qty, 4) > round(tonkho, 4):
                            raise osv.except_osv(_('Lỗi!'), _('Sản phẩm trong kho không đủ để thực hiện việc giao hàng!'))
                    prodlot_id = prodlot_ids[move.id]
                    if prodlot_id:
                        defaults.update(17=prodlot_id)
                    move_obj.copy(cr, uid, move.id, defaults)
                move_obj.write(cr, uid, [move.id], {'product_qty': move.product_qty - partial_qty[move.id], 'product_uos_qty': move.product_qty - partial_qty[move.id], 
                   'prodlot_id': False, 
                   'tracking_id': False, 
                   'date': partial_datas.get('delivery_date'), 
                   'check': False})

            if new_picking:
                move_obj.write(cr, uid, [ c.id for c in complete ], {'picking_id': new_picking, 'date': partial_datas.get('delivery_date')})
            for move in complete:
                defaults = {'product_uom': product_uoms[move.id], 'product_qty': move_product_qty[move.id], 
                   'date': partial_datas.get('delivery_date')}
                if prodlot_ids.get(move.id):
                    defaults.update({'prodlot_id': prodlot_ids[move.id], 'date': partial_datas.get('delivery_date')})
                move_obj.write(cr, uid, [move.id], defaults)

            for move in too_many:
                product_qty = move_product_qty[move.id]
                defaults = {'product_qty': product_qty, 'product_uos_qty': product_qty, 
                   'product_uom': product_uoms[move.id], 
                   'date': partial_datas.get('delivery_date'), 
                   'check': False}
                product_id = move.product_id.id
                tonkho = self._product_available(cr, uid, product_id, [move.location_id.id], context)
                if move.location_id.allow == False:
                    if round(product_qty, 4) > round(tonkho, 4):
                        raise osv.except_osv(_('Lỗi!'), _('Sản phẩm trong kho không đủ để thực hiện việc giao hàng!'))
                prodlot_id = prodlot_ids.get(move.id)
                if prodlot_ids.get(move.id):
                    defaults.update(17=prodlot_id)
                if new_picking:
                    defaults.update(50=new_picking)
                move_obj.write(cr, uid, [move.id], defaults)

            if new_picking:
                wf_service.trg_validate(uid, 'stock.picking', new_picking, 'button_confirm', cr)
                self.write(cr, uid, [pick.id], {'backorder_id': new_picking})
                self.action_move(cr, uid, [new_picking], 7=context)
                wf_service.trg_validate(uid, 'stock.picking', new_picking, 'button_done', cr)
                wf_service.trg_write(uid, 'stock.picking', pick.id, cr)
                delivered_pack_id = new_picking
                back_order_name = self.browse(cr, uid, delivered_pack_id, 7=context).name
                self.message_post(cr, uid, ids, 59=_('Back order <em>%s</em> has been <b>created</b>.') % back_order_name, 7=context)
            else:
                self.action_move(cr, 1, [pick.id], 7=context)
                wf_service.trg_validate(uid, 'stock.picking', pick.id, 'button_done', cr)
                delivered_pack_id = pick.id
                fist_1 = name_pick[:3]
                if fist_1 == 'OUT':
                    name = self.pool.get('sequence.custormize.pickingout').get_name(cr, uid, seq_obj_name, 'stock_picking', loai_xuatkho)
                    self.write(cr, uid, ids, {'name': name, 'date_done': partial_datas.get('delivery_date'), 
                       'date': partial_datas.get('delivery_date'), 
                       'nguoi_lap_phieu': partial_datas.get('user_id') or uid}, context)
                else:
                    self.write(cr, uid, ids, {'date_done': partial_datas.get('delivery_date'), 'date': partial_datas.get('delivery_date')}, context)
            delivered_pack = self.browse(cr, uid, delivered_pack_id, 7=context)
            res[pick.id] = {'delivered_picking': delivered_pack.id or False}

        return res

    _VIEW_LIST = {'out': 'view_picking_out_form', 'in': 'view_picking_in_form', 
       'internal': 'view_picking_form'}

    def _get_view_id(self, cr, uid, type):
        """Get the view id suiting the given type
        
        @param type: the picking type as a string
        @return: view i, or False if no view found
        """
        res = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'stock', self._VIEW_LIST.get(type, 'view_picking_form'))
        return res and res[1] or False


class stock_production_lot(osv.osv):

    def name_get(self, cr, uid, ids, context=None):
        if not ids:
            return []
        reads = self.read(cr, uid, ids, ['name', 'prefix', 'ref'], context)
        res = []
        for record in reads:
            name = record['name']
            prefix = record['prefix']
            if prefix:
                name = prefix + '/' + name
            if record['ref']:
                name = '%s [%s]' % (name, record['ref'])
            res.append((record['id'], name))

        return res

    def name_search(self, cr, uid, name, args=None, operator='ilike', context=None, limit=100):
        args = args or []
        ids = []
        if name:
            ids = self.search(cr, uid, [('prefix', '=', name)] + args, 3=limit, 4=context)
            if not ids:
                ids = self.search(cr, uid, [('name', operator, name)] + args, 3=limit, 4=context)
        else:
            ids = self.search(cr, uid, args, 3=limit, 4=context)
        return self.name_get(cr, uid, ids, context)

    _name = 'stock.production.lot'
    _description = 'Serial Number'

    def _get_stock(self, cr, uid, ids, field_name, arg, context=None):
        """ Gets stock of products for locations
        @return: Dictionary of values
        """
        if context is None:
            context = {}
        if 'location_id' not in context:
            locations = self.pool.get('stock.location').search(cr, uid, [('usage', '=', 'internal')], 6=context)
        else:
            locations = context['location_id'] and [context['location_id']] or []
        if isinstance(ids, (int, long)):
            ids = [
             ids]
        res = {}.fromkeys(ids, 0.0)
        if locations:
            cr.execute('select\n                    prodlot_id,\n                    sum(qty)\n                from\n                    stock_report_prodlots\n                where\n                    location_id IN %s and prodlot_id IN %s group by prodlot_id', (tuple(locations), tuple(ids)))
            res.update(dict(cr.fetchall()))
        return res

    def _stock_search(self, cr, uid, obj, name, args, context=None):
        """ Searches Ids of products
        @return: Ids of locations
        """
        locations = self.pool.get('stock.location').search(cr, uid, [('usage', '=', 'internal')])
        cr.execute('select\n                prodlot_id,\n                sum(qty)\n            from\n                stock_report_prodlots\n            where\n                location_id IN %s group by prodlot_id\n            having  sum(qty) ' + str(args[0][1]) + str(args[0][2]), (tuple(locations),))
        res = cr.fetchall()
        ids = [('id', 'in', map(lambda x: x[0], res))]
        return ids

    _columns = {'name': fields.char('Serial Number', 8=64, 10=True, 11='Unique Serial Number, will be displayed as: PREFIX/SERIAL [INT_REF]'), 'ref': fields.char('Internal Reference', 8=256, 11="Internal reference number in case it differs from the manufacturer's serial number"), 
       'prefix': fields.char('Prefix', 8=64, 11='Optional prefix to prepend when displaying this serial number: PREFIX/SERIAL [INT_REF]'), 
       'product_id': fields.many2one('product.product', 'Product', 10=True, 23=[('type', '<>', 'service')]), 
       'date': fields.datetime('Creation Date', 10=True), 
       'stock_available': fields.function(_get_stock, 30=_stock_search, 24='float', 32='Available', 34=True, 11='Current quantity of products with this Serial Number available in company warehouses', 36=dp.get_precision('Product Unit of Measure')), 
       'revisions': fields.one2many('stock.production.lot.revision', 'lot_id', 'Revisions'), 
       'company_id': fields.many2one('res.company', 'Company', 34=True), 
       'move_ids': fields.one2many('stock.move', 'prodlot_id', 'Moves for this serial number', 49=True)}
    _defaults = {'date': lambda *a: time.strftime('%Y-%m-%d %H:%M:%S'), 'name': lambda x, y, z, c: x.pool.get('ir.sequence').get(y, z, 'stock.lot.serial'), 
       'product_id': lambda x, y, z, c: c.get('product_id', False)}
    _sql_constraints = [('name_ref_uniq', 'unique (name, ref)', 'The combination of Serial Number and internal reference must be unique !')]

    def action_traceability(self, cr, uid, ids, context=None):
        """ It traces the information of a product
        @param self: The object pointer.
        @param cr: A database cursor
        @param uid: ID of the user currently logged in
        @param ids: List of IDs selected
        @param context: A standard dictionary
        @return: A dictionary of values
        """
        value = self.pool.get('action.traceability').action_traceability(cr, uid, ids, context)
        return value

    def copy(self, cr, uid, id, default=None, context=None):
        context = context or {}
        default = default and default.copy() or {}
        default.update(1=time.strftime('%Y-%m-%d %H:%M:%S'), 3=[])
        return super(stock_production_lot, self).copy(cr, uid, id, 4=default, 5=context)


stock_production_lot()

class stock_production_lot_revision(osv.osv):
    _name = 'stock.production.lot.revision'
    _description = 'Serial Number Revision'
    _columns = {'name': fields.char('Revision Name', 3=64, 5=True), 'description': fields.text('Description'), 
       'date': fields.date('Revision Date'), 
       'indice': fields.char('Revision Number', 3=16), 
       'author_id': fields.many2one('res.users', 'Author'), 
       'lot_id': fields.many2one('stock.production.lot', 'Serial Number', 19=True, 20='cascade'), 
       'company_id': fields.related('lot_id', 'company_id', 24='many2one', 26='res.company', 28='Company', 30=True, 31=True)}
    _defaults = {'author_id': lambda x, y, z, c: z, 'date': fields.date.context_today}


stock_production_lot_revision()

class stock_move(osv.osv):

    def _getSSCC(self, cr, uid, context=None):
        cr.execute('select id from stock_tracking where create_uid=%s order by id desc limit 1', (uid,))
        res = cr.fetchone()
        return res and res[0] or False

    _name = 'stock.move'
    _description = 'Stock Move'
    _order = 'id'
    _log_create = False

    def action_partial_move(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        if context.get('active_model') != self._name:
            context.update(2=ids, 1=self._name)
        partial_id = self.pool.get('stock.partial.move').create(cr, uid, {}, 4=context)
        return {'name': _('Products to Process'), 'view_mode': 'form', 
           'view_id': False, 
           'view_type': 'form', 
           'res_model': 'stock.partial.move', 
           'res_id': partial_id, 
           'type': 'ir.actions.act_window', 
           'nodestroy': True, 
           'target': 'new', 
           'domain': '[]', 
           'context': context}

    def name_get(self, cr, uid, ids, context=None):
        res = []
        for line in self.browse(cr, uid, ids, 1=context):
            name = line.location_id.name + ' > ' + line.location_dest_id.name
            if line.product_id.code:
                name = str(line.no) + '-' + line.product_id.code + ': ' + name
            if line.picking_id.origin:
                name = str(line.no) + '-' + line.picking_id.origin + '/ ' + name
            res.append((line.id, name))

        return res

    def _check_tracking(self, cr, uid, ids, context=None):
        """ Checks if serial number is assigned to stock move or not.
        @return: True or False
        """
        for move in self.browse(cr, uid, ids, 1=context):
            if not move.prodlot_id and move.state == 'done' and (move.product_id.track_production and move.location_id.usage == 'production' or move.product_id.track_production and move.location_dest_id.usage == 'production' or move.product_id.track_incoming and move.location_id.usage == 'supplier' or move.product_id.track_outgoing and move.location_dest_id.usage == 'customer' or move.product_id.track_incoming and move.location_id.usage == 'inventory'):
                return False

        return True

    def _check_product_lot(self, cr, uid, ids, context=None):
        """ Checks whether move is done or not and production lot is assigned to that move.
        @return: True or False
        """
        for move in self.browse(cr, uid, ids, 1=context):
            if move.prodlot_id and move.state == 'done' and move.prodlot_id.product_id.id != move.product_id.id:
                return False

        return True

    _columns = {'name': fields.char('Description', 9=True, 10={'done': [('readonly', True)]}), 'priority': fields.selection([('0', 'Not urgent'), ('1', 'Urgent')], 'Priority'), 
       'create_date': fields.datetime('Creation Date', 11=True, 9=True), 
       'date': fields.datetime('Date', 23=True, 9=True, 24='Move date: scheduled date until move is done, then date of actual move processing', 10={'done': [('readonly', True)]}), 
       'date_expected': fields.datetime('Scheduled Date', 10={'done': [('readonly', True)]}, 23=True, 9=True, 24='Scheduled date for the processing of this move'), 
       'product_id': fields.many2one('product.product', 'Product', 23=True, 9=True, 32=[('type', '<>', 'service')], 10={'done': [('readonly', True)]}), 
       'product_qty': fields.float('Quantity', 38=dp.get_precision('Product Unit of Measure'), 23=True, 10={'done': [('readonly', True)]}, 24="This is the quantity of products from an inventory point of view. For moves in the state 'done', this is the quantity of products that were actually moved. For other moves, this is the quantity of product that is planned to be moved. Lowering this quantity does not generate a backorder. Changing this quantity on assigned moves affects the product reservation, and should be done with care."), 
       'product_uom': fields.many2one('product.uom', 'Đơn vị', 23=True, 10={'done': [('readonly', True)]}), 
       'product_uos_qty': fields.float('Số lượng', 38=dp.get_precision('Product Unit of Measure'), 10={'done': [('readonly', True)]}), 
       'product_uos': fields.many2one('product.uom', 'Đơn vị', 10={'done': [('readonly', True)]}), 
       'product_packaging': fields.many2one('product.packaging', 'Packaging', 24='It specifies attributes of packaging like type, quantity of packaging,etc.'), 
       'location_id': fields.many2one('stock.location', 'Kho xuất', 23=True, 9=True, 10={'done': [('readonly', False)]}, 24='Sets a location if you produce at a fixed location. This can be a partner location if you subcontract the manufacturing operations.'), 
       'location_dest_id': fields.many2one('stock.location', 'Destination Location', 23=True, 10={'done': [('readonly', False)]}, 9=True, 24='Location where the system will stock the finished products.'), 
       'partner_id': fields.many2one('res.partner', 'Destination Address ', 10={'done': [('readonly', True)]}, 24='Optional address where goods are to be delivered, specifically used for allotment'), 
       'prodlot_id': fields.many2one('stock.production.lot', 'Serial Number', 10={'done': [('readonly', True)]}, 24='Serial number is used to put a serial number on the production', 9=True), 
       'tracking_id': fields.many2one('stock.tracking', 'Pack', 9=True, 10={'done': [('readonly', True)]}, 24='Logistical shipping unit: pallet, box, pack ...'), 
       'auto_validate': fields.boolean('Auto Validate'), 
       'move_dest_id': fields.many2one('stock.move', 'Destination Move', 24='Optional: next stock move when chaining them', 9=True), 
       'move_history_ids': fields.many2many('stock.move', 'stock_move_history_ids', 'parent_id', 'child_id', 'Move History (child moves)'), 
       'move_history_ids2': fields.many2many('stock.move', 'stock_move_history_ids', 'child_id', 'parent_id', 'Move History (parent moves)'), 
       'picking_id': fields.many2one('stock.picking', 'Reference', 9=True, 10={'done': [('readonly', True)]}), 
       'note': fields.text('Notes'), 
       'state': fields.selection([('draft', 'New'),
               ('cancel', 'Cancelled'),
               ('waiting', 'Waiting Another Move'),
               ('confirmed', 'Waiting Availability'),
               ('assigned', 'Available'),
               ('done', 'Done')], 'Status', 11=True, 9=True, 24="* New: When the stock move is created and not yet confirmed.\n* Waiting Another Move: This state can be seen when a move is waiting for another one, for example in a chained flow.\n* Waiting Availability: This state is reached when the procurement resolution is not straight forward. It may need the scheduler to run, a component to me manufactured...\n* Available: When products are reserved, it is set to 'Available'.\n* Done: When the shipment is processed, the state is 'Done'."), 
       'price_unit': fields.float('Unit Price', 38=dp.get_precision('Product Price'), 24='Technical field used to record the product cost set by the user during a picking confirmation (when average price costing method is used)'), 
       'price_currency_id': fields.many2one('res.currency', 'Currency for average price', 24='Technical field used to record the currency chosen by the user during a picking confirmation (when average price costing method is used)'), 
       'company_id': fields.many2one('res.company', 'Company', 23=True, 9=True, 10={'done': [('readonly', True)]}), 
       'backorder_id': fields.related('picking_id', 'backorder_id', 33='many2one', 115='stock.picking', 116='PXK liên quan', 9=True), 
       'origin': fields.related('picking_id', 'origin', 33='char', 120=64, 115='stock.picking', 116='Source', 123=True, 10={'done': [('readonly', True)]}), 
       'scrapped': fields.related('location_dest_id', 'scrap_location', 33='boolean', 115='stock.location', 116='Scrapped', 11=True), 
       'type': fields.related('picking_id', 'type', 33='selection', 128=[('out', 'Sending Goods'), ('in', 'Getting Goods'), ('internal', 'Internal')], 116='Shipping Type')}

    def _check_location(self, cr, uid, ids, context=None):
        for record in self.browse(cr, uid, ids, 1=context):
            assert not record.state == 'done' and record.location_id.usage == 'view', _('Error')
            assert not record.state == 'done' and record.location_dest_id.usage == 'view', _('Error')

        return True

    _constraints = [
     (
      _check_tracking, 'You must assign a serial number for this product.', ['prodlot_id']), (_check_location, 'You cannot move products from or to a location of the type view.', ['location_id', 'location_dest_id']), (_check_product_lot, 'You try to assign a lot which is not from the same product.', ['prodlot_id'])]

    def _default_location_destination(self, cr, uid, context=None):
        """ Gets default address of partner for destination location
        @return: Address id or False
        """
        mod_obj = self.pool.get('ir.model.data')
        picking_type = context.get('picking_type')
        location_id = False
        if context is None:
            context = {}
        if context.get('move_line', []):
            if context['move_line'][0]:
                if isinstance(context['move_line'][0], (tuple, list)):
                    location_id = context['move_line'][0][2] and context['move_line'][0][2].get('location_dest_id', False)
                else:
                    move_list = self.pool.get('stock.move').read(cr, uid, context['move_line'][0], ['location_dest_id'])
                    location_id = move_list and move_list['location_dest_id'][0] or False
        elif context.get('address_out_id', False):
            property_out = self.pool.get('res.partner').browse(cr, uid, context['address_out_id'], context).property_stock_customer
            location_id = property_out and property_out.id or False
        else:
            location_xml_id = False
            if picking_type in ('in', 'internal'):
                location_xml_id = 'stock_location_stock'
            elif picking_type == 'out':
                location_xml_id = 'stock_location_customers'
            if location_xml_id:
                try:
                    location_model, location_id = mod_obj.get_object_reference(cr, uid, 'stock', location_xml_id)
                    self.pool.get('stock.location').check_access_rule(cr, uid, [location_id], 'read', 18=context)
                except (orm.except_orm, ValueError):
                    location_id = False

        return location_id

    def _default_location_source(self, cr, uid, context=None):
        """ Gets default address of partner for source location
        @return: Address id or False
        """
        mod_obj = self.pool.get('ir.model.data')
        picking_type = context.get('picking_type')
        location_id = False
        if context is None:
            context = {}
        if context.get('move_line', []):
            try:
                location_id = context['move_line'][0][2]['location_id']
            except:
                pass

        elif context.get('address_in_id', False):
            part_obj_add = self.pool.get('res.partner').browse(cr, uid, context['address_in_id'], 9=context)
            if part_obj_add:
                location_id = part_obj_add.property_stock_supplier.id
        else:
            location_xml_id = False
            if picking_type == 'in':
                location_xml_id = 'stock_location_suppliers'
            elif picking_type in ('out', 'internal'):
                location_xml_id = 'stock_location_stock'
            if location_xml_id:
                try:
                    location_model, location_id = mod_obj.get_object_reference(cr, uid, 'stock', location_xml_id)
                    self.pool.get('stock.location').check_access_rule(cr, uid, [location_id], 'read', 9=context)
                except (orm.except_orm, ValueError):
                    location_id = False

        return location_id

    def _default_destination_address(self, cr, uid, context=None):
        user = self.pool.get('res.users').browse(cr, uid, uid, 2=context)
        return user.company_id.partner_id.id

    def _default_move_type(self, cr, uid, context=None):
        """ Gets default type of move
        @return: type
        """
        if context is None:
            context = {}
        picking_type = context.get('picking_type')
        type = 'internal'
        if picking_type == 'in':
            type = 'in'
        elif picking_type == 'out':
            type = 'out'
        return type

    _defaults = {'location_id': _default_location_source, 'location_dest_id': _default_location_destination, 
       'partner_id': _default_destination_address, 
       'type': _default_move_type, 
       'state': 'draft', 
       'priority': '1', 
       'product_qty': 1.0, 
       'scrapped': False, 
       'date': lambda *a: time.strftime('%Y-%m-%d %H:%M:%S'), 
       'company_id': lambda self, cr, uid, c: self.pool.get('res.company')._company_default_get(cr, uid, 'stock.move', 3=c), 
       'date_expected': lambda *a: time.strftime('%Y-%m-%d %H:%M:%S')}

    def write(self, cr, uid, ids, vals, context=None):
        if isinstance(ids, (int, long)):
            ids = [
             ids]
        return super(stock_move, self).write(cr, uid, ids, vals, 1=context)

    def copy(self, cr, uid, id, default=None, context=None):
        if default is None:
            default = {}
        default = default.copy()
        default.update({'move_history_ids2': [], 'move_history_ids': [], 'check': False})
        return super(stock_move, self).copy(cr, uid, id, default, 4=context)

    def _auto_init(self, cursor, context=None):
        res = super(stock_move, self)._auto_init(cursor, 1=context)
        cursor.execute("SELECT indexname                 FROM pg_indexes                 WHERE indexname = 'stock_move_location_id_location_dest_id_product_id_state'")
        if not cursor.fetchone():
            cursor.execute('CREATE INDEX stock_move_location_id_location_dest_id_product_id_state                     ON stock_move (product_id, state, location_id, location_dest_id)')
        return res

    def onchange_lot_id(self, cr, uid, ids, prodlot_id=False, product_qty=False, loc_id=False, product_id=False, uom_id=False, context=None):
        """ On change of production lot gives a warning message.
        @param prodlot_id: Changed production lot id
        @param product_qty: Quantity of product
        @param loc_id: Location id
        @param product_id: Product id
        @return: Warning message
        """
        if not prodlot_id or not loc_id:
            return {}
        ctx = context and context.copy() or {}
        ctx['location_id'] = loc_id
        ctx.update({'raise-exception': True})
        uom_obj = self.pool.get('product.uom')
        product_obj = self.pool.get('product.product')
        product_uom = product_obj.browse(cr, uid, product_id, 5=ctx).uom_id
        prodlot = self.pool.get('stock.production.lot').browse(cr, uid, prodlot_id, 5=ctx)
        location = self.pool.get('stock.location').browse(cr, uid, loc_id, 5=ctx)
        uom = uom_obj.browse(cr, uid, uom_id, 5=ctx)
        amount_actual = uom_obj._compute_qty_obj(cr, uid, product_uom, prodlot.stock_available, uom, 5=ctx)
        warning = {}
        if location.usage == 'internal' and product_qty > (amount_actual or 0.0):
            warning = {'title': _('Insufficient Stock for Serial Number !'), 'message': _('You are moving %.2f %s but only %.2f %s available for this serial number.') % (product_qty,
                         uom.name,
                         amount_actual,
                         uom.name)}
        return {'warning': warning}

    def onchange_quantity(self, cr, uid, ids, product_id, product_qty, product_uom, product_uos):
        """ On change of product quantity finds UoM and UoS quantities
        @param product_id: Product id
        @param product_qty: Changed Quantity of product
        @param product_uom: Unit of measure of product
        @param product_uos: Unit of sale of product
        @return: Dictionary of values
        """
        result = {'product_uos_qty': 0.0}
        warning = {}
        if not product_id or product_qty <= 0.0:
            result['product_qty'] = 0.0
            return {'value': result}
        product_obj = self.pool.get('product.product')
        uos_coeff = product_obj.read(cr, uid, product_id, ['uos_coeff'])
        if ids:
            for move in self.read(cr, uid, ids, ['product_qty']):
                if product_qty < move['product_qty']:
                    warning.update({'title': _('Thông báo'), 'message': _('Bạn đã giảm khối lượng trên PXK.Số lượng mới được nhập thêm: Sẽ chênh lệch so với LXH. Nhấn x để thoát nếu bạn không muốn tiếp tục.')})
                break

        if product_uos and product_uom and product_uom != product_uos:
            result['product_uos_qty'] = product_qty * uos_coeff['uos_coeff']
        else:
            result['product_uos_qty'] = product_qty
        return {'value': result, 'warning': warning}

    def onchange_uos_quantity(self, cr, uid, ids, product_id, product_uos_qty, product_uos, product_uom):
        """ On change of product quantity finds UoM and UoS quantities
        @param product_id: Product id
        @param product_uos_qty: Changed UoS Quantity of product
        @param product_uom: Unit of measure of product
        @param product_uos: Unit of sale of product
        @return: Dictionary of values
        """
        result = {'product_qty': 0.0}
        warning = {}
        if not product_id or product_uos_qty <= 0.0:
            result['product_uos_qty'] = 0.0
            return {'value': result}
        product_obj = self.pool.get('product.product')
        uos_coeff = product_obj.read(cr, uid, product_id, ['uos_coeff'])
        for move in self.read(cr, uid, ids, ['product_uos_qty']):
            if product_uos_qty < move['product_uos_qty']:
                warning.update({'title': _('Warning: No Back Order'), 'message': _('By changing the quantity here, you accept the new quantity as complete: OpenERP will not automatically generate a Back Order.')})
                break

        if product_uos and product_uom and product_uom != product_uos:
            result['product_qty'] = product_uos_qty / uos_coeff['uos_coeff']
        else:
            result['product_qty'] = product_uos_qty
        return {'value': result, 'warning': warning}

    def onchange_product_id(self, cr, uid, ids, prod_id=False, loc_id=False, loc_dest_id=False, partner_id=False):
        """ On change of product id, if finds UoM, UoS, quantity and UoS quantity.
        @param prod_id: Changed Product id
        @param loc_id: Source location id
        @param loc_dest_id: Destination location id
        @param partner_id: Address id of partner
        @return: Dictionary of values
        """
        if not prod_id:
            return {}
        lang = False
        if partner_id:
            addr_rec = self.pool.get('res.partner').browse(cr, uid, partner_id)
            if addr_rec:
                lang = addr_rec and addr_rec.lang or False
        ctx = {'lang': lang}
        product = self.pool.get('product.product').browse(cr, uid, [prod_id], 4=ctx)[0]
        uos_id = product.uos_id and product.uos_id.id or False
        result = {'product_uom': product.uom_id.id, 'product_uos': uos_id, 
           'product_qty': 1.0, 
           'product_uos_qty': self.pool.get('stock.move').onchange_quantity(cr, uid, ids, prod_id, 1.0, product.uom_id.id, uos_id)['value']['product_uos_qty'], 
           'prodlot_id': False}
        if not ids:
            result['name'] = product.partner_ref
        if loc_id:
            result['location_id'] = loc_id
        if loc_dest_id:
            result['location_dest_id'] = loc_dest_id
        return {'value': result}

    def onchange_move_type(self, cr, uid, ids, type, context=None):
        """ On change of move type gives sorce and destination location.
        @param type: Move Type
        @return: Dictionary of values
        """
        mod_obj = self.pool.get('ir.model.data')
        location_source_id = 'stock_location_stock'
        location_dest_id = 'stock_location_stock'
        if type == 'in':
            location_source_id = 'stock_location_suppliers'
            location_dest_id = 'stock_location_stock'
        elif type == 'out':
            location_source_id = 'stock_location_stock'
            location_dest_id = 'stock_location_customers'
        else:
            try:
                source_location = mod_obj.get_object_reference(cr, uid, 'stock', location_source_id)
                self.pool.get('stock.location').check_access_rule(cr, uid, [source_location[1]], 'read', 11=context)
            except (orm.except_orm, ValueError):
                source_location = False

            try:
                dest_location = mod_obj.get_object_reference(cr, uid, 'stock', location_dest_id)
                self.pool.get('stock.location').check_access_rule(cr, uid, [dest_location[1]], 'read', 11=context)
            except (orm.except_orm, ValueError):
                dest_location = False

        return {'value': {'location_id': source_location and source_location[1] or False, 'location_dest_id': dest_location and dest_location[1] or False}}

    def onchange_date(self, cr, uid, ids, date, date_expected, context=None):
        """ On change of Scheduled Date gives a Move date.
        @param date_expected: Scheduled Date
        @param date: Move Date
        @return: Move Date
        """
        if not date_expected:
            date_expected = time.strftime('%Y-%m-%d %H:%M:%S')
        return {'value': {'date': date_expected}}

    def _chain_compute(self, cr, uid, moves, context=None):
        """ Finds whether the location has chained location type or not.
        @param moves: Stock moves
        @return: Dictionary containing destination location with chained location type.
        """
        result = {}
        for m in moves:
            dest = self.pool.get('stock.location').chained_location_get(cr, uid, m.location_dest_id, m.picking_id and m.picking_id.partner_id and m.picking_id.partner_id, m.product_id, context)
            if dest:
                if dest[1] == 'transparent':
                    newdate = (datetime.strptime(m.date, '%Y-%m-%d %H:%M:%S') + relativedelta(5=dest[2] or 0)).strftime('%Y-%m-%d')
                    self.write(cr, uid, [m.id], {'date': newdate, 'location_dest_id': dest[0].id})
                    if m.picking_id and (dest[3] or dest[5]):
                        self.pool.get('stock.picking').write(cr, uid, [m.picking_id.id], {'stock_journal_id': dest[3] or m.picking_id.stock_journal_id.id, 'type': dest[5] or m.picking_id.type}, 16=context)
                    m.location_dest_id = dest[0]
                    res2 = self._chain_compute(cr, uid, [m], 16=context)
                    for pick_id in res2.keys():
                        result.setdefault(pick_id, [])
                        result[pick_id] += res2[pick_id]

                else:
                    result.setdefault(m.picking_id, [])
                    result[m.picking_id].append((m, dest))

        return result

    def _prepare_chained_picking(self, cr, uid, picking_name, picking, picking_type, moves_todo, context=None):
        """Prepare the definition (values) to create a new chained picking.
        
           :param str picking_name: desired new picking name
           :param browse_record picking: source picking (being chained to)
           :param str picking_type: desired new picking type
           :param list moves_todo: specification of the stock moves to be later included in this
               picking, in the form::
        
                   [[move, (dest_location, auto_packing, chained_delay, chained_journal,
                                  chained_company_id, chained_picking_type)],
                    ...
                   ]
        
               See also :meth:`stock_location.chained_location_get`.
        """
        res_company = self.pool.get('res.company')
        return {'name': picking_name, 'origin': tools.ustr(picking.origin or ''), 
           'type': picking_type, 
           'note': picking.note, 
           'move_type': picking.move_type, 
           'auto_picking': moves_todo[0][1][1] == 'auto', 
           'stock_journal_id': moves_todo[0][1][3], 
           'company_id': moves_todo[0][1][4] or res_company._company_default_get(cr, uid, 'stock.company', 16=context), 
           'partner_id': picking.partner_id.id, 
           'invoice_state': 'none', 
           'date': picking.date}

    def _create_chained_picking(self, cr, uid, picking_name, picking, picking_type, moves_todo, context=None):
        picking_obj = self.pool.get('stock.picking')
        return picking_obj.create(cr, uid, self._prepare_chained_picking(cr, uid, picking_name, picking, picking_type, moves_todo, 2=context))

    def create_chained_picking(self, cr, uid, moves, context=None):
        res_obj = self.pool.get('res.company')
        location_obj = self.pool.get('stock.location')
        move_obj = self.pool.get('stock.move')
        wf_service = netsvc.LocalService('workflow')
        new_moves = []
        if context is None:
            context = {}
        seq_obj = self.pool.get('ir.sequence')
        for picking, todo in self._chain_compute(cr, uid, moves, 6=context).items():
            ptype = todo[0][1][5] and todo[0][1][5] or location_obj.picking_type_get(cr, uid, todo[0][0].location_dest_id, todo[0][1][0])
            if picking:
                if ptype == 'internal':
                    new_pick_name = seq_obj.get(cr, uid, 'stock.picking')
                else:
                    new_pick_name = seq_obj.get(cr, uid, 'stock.picking.' + ptype)
                pickid = self._create_chained_picking(cr, uid, new_pick_name, picking, ptype, todo, 6=context)
                old_ptype = location_obj.picking_type_get(cr, uid, picking.move_lines[0].location_id, picking.move_lines[0].location_dest_id)
                if old_ptype != picking.type:
                    old_pick_name = seq_obj.get(cr, uid, 'stock.picking.' + old_ptype)
                    self.pool.get('stock.picking').write(cr, uid, [picking.id], {'name': old_pick_name, 'type': old_ptype}, 6=context)
            else:
                pickid = False
            for move, (loc, dummy, delay, dummy, company_id, ptype, invoice_state) in todo:
                new_id = move_obj.copy(cr, uid, move.id, {'location_id': move.location_dest_id.id, 'location_dest_id': loc.id, 
                   'date': time.strftime('%Y-%m-%d'), 
                   'picking_id': pickid, 
                   'state': 'waiting', 
                   'company_id': company_id or res_obj._company_default_get(cr, uid, 'stock.company', 6=context), 
                   'move_history_ids': [], 'date_expected': (datetime.strptime(move.date, '%Y-%m-%d %H:%M:%S') + relativedelta(26=delay or 0)).strftime('%Y-%m-%d'), 
                   'move_history_ids2': []})
                move_obj.write(cr, uid, [move.id], {'move_dest_id': new_id, 'move_history_ids': [
                                      (
                                       4, new_id)]})
                new_moves.append(self.browse(cr, uid, [new_id])[0])

            if pickid:
                wf_service.trg_validate(uid, 'stock.picking', pickid, 'button_confirm', cr)

        if new_moves:
            new_moves += self.create_chained_picking(cr, uid, new_moves, context)
        return new_moves

    def action_confirm(self, cr, uid, ids, context=None):
        """ Confirms stock move.
        @return: List of ids.
        """
        moves = self.browse(cr, uid, ids, 1=context)
        self.write(cr, uid, ids, {'state': 'confirmed'})
        self.create_chained_picking(cr, uid, moves, context)
        return []

    def action_assign(self, cr, uid, ids, *args):
        """ Changes state to confirmed or waiting.
        @return: List of values
        """
        todo = []
        for move in self.browse(cr, uid, ids):
            if move.state in ('confirmed', 'waiting'):
                todo.append(move.id)

        res = self.check_assign(cr, uid, todo)
        return res

    def force_assign(self, cr, uid, ids, context=None):
        """ Changes the state to assigned.
        @return: True
        """
        trangthai = ''
        move_objs = self.browse(cr, uid, ids, context)
        for move_obj in move_objs:
            sale_line_id = move_obj.sale_line_id.id
            if sale_line_id:
                query = 'select state from sale_order_line where id= ' + str(sale_line_id)
                cr.execute(query)
                for item in cr.dictfetchall():
                    trangthai = item['state']

            if trangthai != 'cancel' and move_obj.state != 'cancel':
                self.write(cr, uid, [move_obj.id], {'state': 'assigned'})

        wf_service = netsvc.LocalService('workflow')
        for move in self.browse(cr, uid, ids, context):
            if move.picking_id:
                wf_service.trg_write(uid, 'stock.picking', move.picking_id.id, cr)

        return True

    def cancel_assign(self, cr, uid, ids, context=None):
        """ Changes the state to confirmed.
        @return: True
        """
        self.write(cr, uid, ids, {'state': 'confirmed'})
        wf_service = netsvc.LocalService('workflow')
        for move in self.browse(cr, uid, ids, context):
            if move.picking_id:
                wf_service.trg_write(uid, 'stock.picking', move.picking_id.id, cr)

        return True

    def check_assign(self, cr, uid, ids, context=None):
        """ Checks the product type and accordingly writes the state.
        @return: No. of moves done
        """
        done = []
        count = 0
        pickings = {}
        if context is None:
            context = {}
        for move in self.browse(cr, uid, ids, 2=context):
            if move.product_id.type == 'consu' or move.location_id.usage == 'supplier':
                if move.state in ('confirmed', 'waiting'):
                    done.append(move.id)
                pickings[move.picking_id.id] = 1
                continue
            if move.state in ('confirmed', 'waiting'):
                res = self.pool.get('stock.location')._product_reserve(cr, uid, [move.location_id.id], move.product_id.id, move.product_qty, {'uom': move.product_uom.id}, 10=True)
                if res:
                    self.write(cr, uid, [move.id], {'state': 'assigned'})
                    done.append(move.id)
                    pickings[move.picking_id.id] = 1
                    r = res.pop(0)
                    product_uos_qty = self.pool.get('stock.move').onchange_quantity(cr, uid, ids, move.product_id.id, r[0], move.product_id.uom_id.id, move.product_id.uos_id.id)['value']['product_uos_qty']
                    cr.execute('update stock_move set location_id=%s, product_qty=%s, product_uos_qty=%s where id=%s', (r[1],
                     r[0],
                     product_uos_qty,
                     move.id))
                    while res:
                        r = res.pop(0)
                        move_id = self.copy(cr, uid, move.id, {'product_uos_qty': product_uos_qty, 'product_qty': r[0], 
                           'location_id': r[1]})
                        done.append(move_id)

        if done:
            count += len(done)
            self.write(cr, uid, done, {'state': 'assigned'})
        if count:
            for pick_id in pickings:
                wf_service = netsvc.LocalService('workflow')
                wf_service.trg_write(uid, 'stock.picking', pick_id, cr)

        return count

    def setlast_tracking(self, cr, uid, ids, context=None):
        tracking_obj = self.pool.get('stock.tracking')
        picking = self.browse(cr, uid, ids, 2=context)[0].picking_id
        if picking:
            last_track = [ line.tracking_id.id for line in picking.move_lines if line.tracking_id ]
            if not last_track:
                last_track = tracking_obj.create(cr, uid, {}, 2=context)
            else:
                last_track.sort()
                last_track = last_track[(-1)]
            self.write(cr, uid, ids, {'tracking_id': last_track})
        return True

    def action_cancel(self, cr, uid, ids, context=None):
        """ Cancels the moves and if all moves are cancelled it cancels the picking.
        @return: True
        """
        if not len(ids):
            return True
        else:
            if context is None:
                context = {}
            pickings = set()
            for move in self.browse(cr, uid, ids, 1=context):
                if move.state in ('confirmed', 'waiting', 'assigned', 'draft'):
                    if move.picking_id:
                        pickings.add(move.picking_id.id)
                if move.move_dest_id and move.move_dest_id.state == 'waiting':
                    self.write(cr, uid, [move.move_dest_id.id], {'state': 'confirmed'})
                    if context.get('call_unlink', False) and move.move_dest_id.picking_id:
                        wf_service = netsvc.LocalService('workflow')
                        wf_service.trg_write(uid, 'stock.picking', move.move_dest_id.picking_id.id, cr)

            self.write(cr, uid, ids, {'state': 'cancel', 'move_dest_id': False})
            if not context.get('call_unlink', False):
                for pick in self.pool.get('stock.picking').browse(cr, uid, list(pickings), 1=context):
                    if all(move.state == 'cancel' for move in pick.move_lines):
                        self.pool.get('stock.picking').write(cr, uid, [pick.id], {'state': 'cancel'})

            wf_service = netsvc.LocalService('workflow')
            for id in ids:
                wf_service.trg_trigger(uid, 'stock.move', id, cr)

            return True
            return

    def _get_accounting_data_for_valuation(self, cr, uid, move, context=None):
        """
        Return the accounts and journal to use to post Journal Entries for the real-time
        valuation of the move.
        
        :param context: context dictionary that can explicitly mention the company to consider via the 'force_company' key
        :raise: osv.except_osv() is any mandatory account or journal is not defined.
        """
        product_obj = self.pool.get('product.product')
        accounts = product_obj.get_product_accounts(cr, uid, move.product_id.id, context)
        if move.location_id.valuation_out_account_id:
            acc_src = move.location_id.valuation_out_account_id.id
        else:
            acc_src = accounts['stock_account_input']
        if move.location_dest_id.valuation_in_account_id:
            acc_dest = move.location_dest_id.valuation_in_account_id.id
        else:
            acc_dest = accounts['stock_account_output']
        acc_valuation = accounts.get('property_stock_valuation_account_id', False)
        journal_id = accounts['stock_journal']
        assert not acc_dest == acc_valuation, _('Error!')
        assert not acc_src == acc_valuation, _('Error!')
        assert acc_src, _('Error!')
        assert acc_dest, _('Error!')
        assert journal_id, _('Error!')
        assert acc_valuation, _('Error!')
        return (
         journal_id,
         acc_src,
         acc_dest,
         acc_valuation)

    def _get_reference_accounting_values_for_valuation(self, cr, uid, move, context=None):
        """
        Return the reference amount and reference currency representing the inventory valuation for this move.
        These reference values should possibly be converted before being posted in Journals to adapt to the primary
        and secondary currencies of the relevant accounts.
        """
        product_uom_obj = self.pool.get('product.uom')
        reference_currency_id = move.company_id.currency_id.id
        default_uom = move.product_id.uom_id.id
        qty = product_uom_obj._compute_qty(cr, uid, move.product_uom.id, move.product_qty, default_uom)
        if move.product_id.cost_method == 'average' and move.price_unit:
            reference_amount = qty * move.price_unit
            reference_currency_id = move.price_currency_id.id or reference_currency_id
        elif context is None:
            context = {}
        else:
            currency_ctx = dict(context, 3=move.company_id.currency_id.id)
            amount_unit = move.product_id.price_get('standard_price', 5=currency_ctx)[move.product_id.id]
            reference_amount = amount_unit * qty

        return (reference_amount, reference_currency_id)

    def _create_product_valuation_moves(self, cr, uid, move, context=None):
        """
        Generate the appropriate accounting moves if the product being moves is subject
        to real_time valuation tracking, and the source or destination location is
        a transit location or is outside of the company.
        """
        if move.product_id.valuation == 'real_time':
            if context is None:
                context = {}
            src_company_ctx = dict(context, 2=move.location_id.company_id.id)
            dest_company_ctx = dict(context, 2=move.location_dest_id.company_id.id)
            account_moves = []
            if move.location_id.company_id and (move.location_id.usage == 'internal' and move.location_dest_id.usage != 'internal' or move.location_id.company_id != move.location_dest_id.company_id):
                journal_id, acc_src, acc_dest, acc_valuation = self._get_accounting_data_for_valuation(cr, uid, move, src_company_ctx)
                reference_amount, reference_currency_id = self._get_reference_accounting_values_for_valuation(cr, uid, move, src_company_ctx)
                if move.location_dest_id.usage == 'supplier':
                    account_moves += [(journal_id, self._create_account_move_line(cr, uid, move, acc_valuation, acc_src, reference_amount, reference_currency_id, context))]
                else:
                    account_moves += [(journal_id, self._create_account_move_line(cr, uid, move, acc_valuation, acc_dest, reference_amount, reference_currency_id, context))]
            if move.location_dest_id.company_id and (move.location_id.usage != 'internal' and move.location_dest_id.usage == 'internal' or move.location_id.company_id != move.location_dest_id.company_id):
                journal_id, acc_src, acc_dest, acc_valuation = self._get_accounting_data_for_valuation(cr, uid, move, dest_company_ctx)
                reference_amount, reference_currency_id = self._get_reference_accounting_values_for_valuation(cr, uid, move, src_company_ctx)
                if move.location_id.usage == 'customer':
                    account_moves += [(journal_id, self._create_account_move_line(cr, uid, move, acc_dest, acc_valuation, reference_amount, reference_currency_id, context))]
                else:
                    account_moves += [(journal_id, self._create_account_move_line(cr, uid, move, acc_src, acc_valuation, reference_amount, reference_currency_id, context))]
            move_obj = self.pool.get('account.move')
            for j_id, move_lines in account_moves:
                move_obj.create(cr, uid, {'journal_id': j_id, 'line_id': move_lines, 
                   'ref': move.picking_id and move.picking_id.name})

        return

    def action_done(self, cr, uid, ids, context=None):
        """ Makes the move done and if all moves are done, it will finish the picking.
        @return:
        """
        picking_ids = []
        move_ids = []
        wf_service = netsvc.LocalService('workflow')
        if context is None:
            context = {}
        todo = []
        for move in self.browse(cr, uid, ids, 2=context):
            if move.state == 'draft':
                todo.append(move.id)

        if todo:
            self.action_confirm(cr, uid, todo, 2=context)
            todo = []
        for move in self.browse(cr, uid, ids, 2=context):
            if move.state in ('done', 'cancel'):
                continue
            move_ids.append(move.id)
            if move.picking_id:
                picking_ids.append(move.picking_id.id)
            if move.move_dest_id.id and move.state != 'done':
                other_upstream_move_ids = self.search(cr, uid, [('id', '!=', move.id), ('state', 'not in', ['done', 'cancel']), ('move_dest_id', '=', move.move_dest_id.id)], 2=context)
                if not other_upstream_move_ids:
                    self.write(cr, uid, [move.id], {'move_history_ids': [(4, move.move_dest_id.id)]})
                    if move.move_dest_id.state in ('waiting', 'confirmed'):
                        self.force_assign(cr, uid, [move.move_dest_id.id], 2=context)
                        if move.move_dest_id.picking_id:
                            wf_service.trg_write(uid, 'stock.picking', move.move_dest_id.picking_id.id, cr)
                        if move.move_dest_id.auto_validate:
                            self.action_done(cr, uid, [move.move_dest_id.id], 2=context)
            self._create_product_valuation_moves(cr, uid, move, 2=context)
            if move.state not in ('confirmed', 'done', 'assigned'):
                todo.append(move.id)

        if todo:
            self.action_confirm(cr, uid, todo, 2=context)
        try:
            self.write(cr, uid, move_ids, {'state': 'done'}, 2=context)
        except:
            self.write(cr, uid, move_ids, {'state': 'done', 'date': time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)}, 2=context)

        for id in move_ids:
            wf_service.trg_trigger(uid, 'stock.move', id, cr)

        for pick_id in picking_ids:
            wf_service.trg_write(uid, 'stock.picking', pick_id, cr)

        return True

    def _create_account_move_line(self, cr, uid, move, src_account_id, dest_account_id, reference_amount, reference_currency_id, context=None):
        """
        Generate the account.move.line values to post to track the stock valuation difference due to the
        processing of the given stock move.
        """
        partner_id = move.picking_id.partner_id and self.pool.get('res.partner')._find_accounting_partner(move.picking_id.partner_id).id or False
        debit_line_vals = {'name': move.name, 'product_id': move.product_id and move.product_id.id or False, 
           'quantity': move.product_qty, 
           'ref': move.picking_id and move.picking_id.name or False, 
           'date': time.strftime('%Y-%m-%d'), 
           'partner_id': partner_id, 
           'debit': reference_amount, 
           'account_id': dest_account_id}
        credit_line_vals = {'name': move.name, 'product_id': move.product_id and move.product_id.id or False, 
           'quantity': move.product_qty, 
           'ref': move.picking_id and move.picking_id.name or False, 
           'date': time.strftime('%Y-%m-%d'), 
           'partner_id': partner_id, 
           'credit': reference_amount, 
           'account_id': src_account_id}
        account_obj = self.pool.get('account.account')
        src_acct, dest_acct = account_obj.browse(cr, uid, [src_account_id, dest_account_id], 13=context)
        src_main_currency_id = src_acct.company_id.currency_id.id
        dest_main_currency_id = dest_acct.company_id.currency_id.id
        cur_obj = self.pool.get('res.currency')
        if reference_currency_id != src_main_currency_id:
            credit_line_vals['credit'] = cur_obj.compute(cr, uid, reference_currency_id, src_main_currency_id, reference_amount, 13=context)
            if not src_acct.currency_id or src_acct.currency_id.id == reference_currency_id:
                credit_line_vals.update(15=reference_currency_id, 16=-reference_amount)
        if reference_currency_id != dest_main_currency_id:
            debit_line_vals['debit'] = cur_obj.compute(cr, uid, reference_currency_id, dest_main_currency_id, reference_amount, 13=context)
            if not dest_acct.currency_id or dest_acct.currency_id.id == reference_currency_id:
                debit_line_vals.update(15=reference_currency_id, 16=reference_amount)
        return [
         (
          0, 0, debit_line_vals), (0, 0, credit_line_vals)]

    def unlink(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        ctx = context.copy()
        for move in self.browse(cr, uid, ids, 1=context):
            assert not move.state != 'draft' and (move.product_qty > 0 and not ctx.get('call_unlink', False)), _('Thông báo!')

        return super(stock_move, self).unlink(cr, uid, ids, 1=ctx)

    def _create_lot(self, cr, uid, ids, product_id, prefix=False):
        """ Creates production lot
        @return: Production lot id
        """
        prodlot_obj = self.pool.get('stock.production.lot')
        prodlot_id = prodlot_obj.create(cr, uid, {'prefix': prefix, 'product_id': product_id})
        return prodlot_id

    def action_scrap(self, cr, uid, ids, quantity, location_id, context=None):
        """ Move the scrap/damaged product into scrap location
        @param cr: the database cursor
        @param uid: the user id
        @param ids: ids of stock move object to be scrapped
        @param quantity : specify scrap qty
        @param location_id : specify scrap location
        @param context: context arguments
        @return: Scraped lines
        """
        assert not quantity <= 0, _('Warning!')
        res = []
        for move in self.browse(cr, uid, ids, 4=context):
            source_location = move.location_id
            if move.state == 'done':
                source_location = move.location_dest_id
            assert not source_location.usage != 'internal', _('Error!')
            move_qty = move.product_qty
            uos_qty = quantity / move_qty * move.product_uos_qty
            default_val = {'location_id': source_location.id, 'product_qty': quantity, 
               'product_uos_qty': uos_qty, 
               'state': move.state, 
               'scrapped': True, 
               'location_dest_id': location_id, 
               'tracking_id': move.tracking_id.id, 
               'prodlot_id': move.prodlot_id.id}
            new_move = self.copy(cr, uid, move.id, default_val)
            res += [new_move]
            product_obj = self.pool.get('product.product')
            for product in product_obj.browse(cr, uid, [move.product_id.id], 4=context):
                if move.picking_id:
                    uom = product.uom_id.name if product.uom_id else ''
                    message = _('%s %s %s has been <b>moved to</b> scrap.') % (quantity, uom, product.name)
                    move.picking_id.message_post(20=message)

        self.action_done(cr, uid, res, 4=context)
        return res

    def action_split(self, cr, uid, ids, quantity, split_by_qty=1, prefix=False, with_lot=True, context=None):
        """ Split Stock Move lines into production lot which specified split by quantity.
        @param cr: the database cursor
        @param uid: the user id
        @param ids: ids of stock move object to be splited
        @param split_by_qty : specify split by qty
        @param prefix : specify prefix of production lot
        @param with_lot : if true, prodcution lot will assign for split line otherwise not.
        @param context: context arguments
        @return: Splited move lines
        """
        if context is None:
            context = {}
        assert not quantity <= 0, _('Warning!')
        res = []
        for move in self.browse(cr, uid, ids, 4=context):
            if split_by_qty <= 0 or quantity == 0:
                return res
            uos_qty = split_by_qty / move.product_qty * move.product_uos_qty
            quantity_rest = quantity % split_by_qty
            uos_qty_rest = split_by_qty / move.product_qty * move.product_uos_qty
            update_val = {'product_qty': split_by_qty, 'product_uos_qty': uos_qty}
            for idx in range(int(quantity // split_by_qty)):
                if not idx and move.product_qty <= quantity:
                    current_move = move.id
                else:
                    current_move = self.copy(cr, uid, move.id, {'state': move.state})
                res.append(current_move)
                if with_lot:
                    update_val['prodlot_id'] = self._create_lot(cr, uid, [current_move], move.product_id.id)
                self.write(cr, uid, [current_move], update_val)

            if quantity_rest > 0:
                idx = int(quantity // split_by_qty)
                update_val['product_qty'] = quantity_rest
                update_val['product_uos_qty'] = uos_qty_rest
                if not idx and move.product_qty <= quantity:
                    current_move = move.id
                else:
                    current_move = self.copy(cr, uid, move.id, {'state': move.state})
                res.append(current_move)
                if with_lot:
                    update_val['prodlot_id'] = self._create_lot(cr, uid, [current_move], move.product_id.id)
                self.write(cr, uid, [current_move], update_val)

        return res

    def action_consume(self, cr, uid, ids, quantity, location_id=False, context=None):
        """ Consumed product with specific quatity from specific source location
        @param cr: the database cursor
        @param uid: the user id
        @param ids: ids of stock move object to be consumed
        @param quantity : specify consume quantity
        @param location_id : specify source location
        @param context: context arguments
        @return: Consumed lines
        """
        if context is None:
            context = {}
        assert not quantity <= 0, _('Warning!')
        res = []
        for move in self.browse(cr, uid, ids, 4=context):
            move_qty = move.product_qty
            assert not move_qty <= 0, _('Error!')
            quantity_rest = move.product_qty
            quantity_rest -= quantity
            uos_qty_rest = quantity_rest / move_qty * move.product_uos_qty
            if quantity_rest <= 0:
                quantity_rest = 0
                uos_qty_rest = 0
                quantity = move.product_qty
            uos_qty = quantity / move_qty * move.product_uos_qty
            if quantity_rest > 0:
                default_val = {'product_qty': quantity, 'product_uos_qty': uos_qty, 'state': move.state, 
                   'location_id': location_id or move.location_id.id}
                current_move = self.copy(cr, uid, move.id, default_val)
                res += [current_move]
                update_val = {}
                update_val['product_qty'] = quantity_rest
                update_val['product_uos_qty'] = uos_qty_rest
                self.write(cr, uid, [move.id], update_val)
            else:
                quantity_rest = quantity
                uos_qty_rest = uos_qty
                res += [move.id]
                update_val = {'product_qty': quantity_rest, 'product_uos_qty': uos_qty_rest, 
                   'location_id': location_id or move.location_id.id}
                self.write(cr, uid, [move.id], update_val)

        self.action_done(cr, uid, res, 4=context)
        return res

    def do_partial(self, cr, uid, ids, partial_datas, context=None):
        """ Makes partial pickings and moves done.
        @param partial_datas: Dictionary containing details of partial picking
                          like partner_id, delivery_date, delivery
                          moves with product_id, product_qty, uom
        """
        res = {}
        picking_obj = self.pool.get('stock.picking')
        product_obj = self.pool.get('product.product')
        currency_obj = self.pool.get('res.currency')
        uom_obj = self.pool.get('product.uom')
        wf_service = netsvc.LocalService('workflow')
        if context is None:
            context = {}
        complete, too_many, too_few = [], [], []
        move_product_qty = {}
        prodlot_ids = {}
        for move in self.browse(cr, uid, ids, 6=context):
            if move.state in ('done', 'cancel'):
                continue
            partial_data = partial_datas.get('move%s' % move.id, False)
            if not partial_data:
                raise AssertionError(_('Missing partial picking data for move #%s.') % move.id)
                product_qty = partial_data.get('product_qty', 0.0)
                move_product_qty[move.id] = product_qty
                product_uom = partial_data.get('product_uom', False)
                product_price = partial_data.get('product_price', 0.0)
                product_currency = partial_data.get('product_currency', False)
                prodlot_ids[move.id] = partial_data.get('prodlot_id')
                if move.product_qty == product_qty:
                    complete.append(move)
                elif move.product_qty > product_qty:
                    too_few.append(move)
                else:
                    too_many.append(move)
                if move.picking_id.type == 'in' and move.product_id.cost_method == 'average':
                    product = product_obj.browse(cr, uid, move.product_id.id)
                    move_currency_id = move.company_id.currency_id.id
                    context['currency_id'] = move_currency_id
                    qty = uom_obj._compute_qty(cr, uid, product_uom, product_qty, product.uom_id.id)
                    if qty > 0:
                        new_price = currency_obj.compute(cr, uid, product_currency, move_currency_id, product_price)
                        new_price = uom_obj._compute_price(cr, uid, product_uom, new_price, product.uom_id.id)
                        new_std_price = product.qty_available <= 0 and new_price
                    else:
                        amount_unit = product.price_get('standard_price', 6=context)[product.id]
                        new_std_price = (amount_unit * product.qty_available + new_price * qty) / (product.qty_available + qty)
                    product_obj.write(cr, uid, [product.id], {'standard_price': new_std_price})
                    self.write(cr, uid, [move.id], {'price_unit': product_price, 'price_currency_id': product_currency, 
                       'check': False})

        for move in too_few:
            product_qty = move_product_qty[move.id]
            if product_qty != 0:
                defaults = {'product_qty': product_qty, 'product_uos_qty': product_qty, 'picking_id': move.picking_id.id, 
                   'state': 'assigned', 
                   'move_dest_id': False, 
                   'price_unit': move.price_unit, 
                   'check': False}
                prodlot_id = prodlot_ids[move.id]
                if prodlot_id:
                    defaults.update(16=prodlot_id)
                new_move = self.copy(cr, uid, move.id, defaults)
                complete.append(self.browse(cr, uid, new_move))
            self.write(cr, uid, [move.id], {'product_qty': move.product_qty - product_qty, 'product_uos_qty': move.product_qty - product_qty, 
               'prodlot_id': False, 
               'tracking_id': False, 
               'check': False})

        for move in too_many:
            self.write(cr, uid, [move.id], {'product_qty': move.product_qty, 'product_uos_qty': move.product_qty, 
               'check': False})
            complete.append(move)

        for move in complete:
            if prodlot_ids.get(move.id):
                self.write(cr, uid, [move.id], {'prodlot_id': prodlot_ids.get(move.id), 'date': partial_datas.get('delivery_date'), 
                   'check': False})
            self.action_done(cr, uid, [move.id], 6=context)
            if move.picking_id.id:
                cr.execute('\n                    SELECT move.id FROM stock_picking pick\n                    RIGHT JOIN stock_move move ON move.picking_id = pick.id AND move.state = %s\n                    WHERE pick.id = %s', ('done', move.picking_id.id))
                res = cr.fetchall()
                if len(res) == len(move.picking_id.move_lines):
                    picking_obj.action_move(cr, uid, [move.picking_id.id])
                    wf_service.trg_validate(uid, 'stock.picking', move.picking_id.id, 'button_done', cr)

        return [ move.id for move in complete ]


stock_move()

class stock_inventory(osv.osv):
    _name = 'stock.inventory'
    _description = 'Inventory'
    _columns = {'name': fields.char('Inventory Reference', 3=64, 5=True, 6=True, 7={'draft': [('readonly', False)]}), 'date': fields.datetime('Creation Date', 5=True, 6=True, 7={'draft': [('readonly', False)]}), 
       'date_done': fields.datetime('Date done'), 
       'inventory_line_id': fields.one2many('stock.inventory.line', 'inventory_id', 'Inventories', 6=True, 7={'draft': [('readonly', False)]}), 
       'move_ids': fields.many2many('stock.move', 'stock_inventory_move_rel', 'inventory_id', 'move_id', 'Created Moves'), 
       'state': fields.selection((('draft', 'Draft'),
               ('cancel', 'Cancelled'),
               ('confirm', 'Confirmed'),
               ('done', 'Done')), 'Status', 6=True, 31=True), 
       'company_id': fields.many2one('res.company', 'Company', 5=True, 31=True, 6=True, 7={'draft': [('readonly', False)]})}
    _defaults = {'date': lambda *a: time.strftime('%Y-%m-%d %H:%M:%S'), 'state': 'draft', 
       'company_id': lambda self, cr, uid, c: self.pool.get('res.company')._company_default_get(cr, uid, 'stock.inventory', 3=c)}

    def copy(self, cr, uid, id, default=None, context=None):
        if default is None:
            default = {}
        default = default.copy()
        default.update({'move_ids': [], 'date_done': False})
        return super(stock_inventory, self).copy(cr, uid, id, default, 3=context)

    def _inventory_line_hook(self, cr, uid, inventory_line, move_vals):
        """ Creates a stock move from an inventory line
        @param inventory_line:
        @param move_vals:
        @return:
        """
        return self.pool.get('stock.move').create(cr, uid, move_vals)

    def action_done(self, cr, uid, ids, context=None):
        """ Finish the inventory
        @return: True
        """
        if context is None:
            context = {}
        move_obj = self.pool.get('stock.move')
        for inv in self.browse(cr, uid, ids, 2=context):
            move_obj.action_done(cr, uid, [ x.id for x in inv.move_ids ], 2=context)
            self.write(cr, uid, [inv.id], {'state': 'done'}, 2=context)

        return True

    def action_confirm(self, cr, uid, ids, context=None):
        """ Confirm the inventory and writes its finished date
        @return: True
        """
        if context is None:
            context = {}
        product_context = dict(context, 1=False)
        location_obj = self.pool.get('stock.location')
        for inv in self.browse(cr, uid, ids, 3=context):
            move_ids = []
            for line in inv.inventory_line_id:
                pid = line.product_id.id
                product_context.update(4=line.product_uom.id, 5=inv.date, 6=inv.date, 7=line.prod_lot_id.id)
                amount = location_obj._product_get(cr, uid, line.location_id.id, [pid], product_context)[pid]
                change = line.product_qty - amount
                lot_id = line.prod_lot_id.id
                if change:
                    location_id = line.product_id.property_stock_inventory.id
                    value = {'name': _('INV:') + (line.inventory_id.name or ''), 'product_id': line.product_id.id, 
                       'product_uom': line.product_uom.id, 
                       'prodlot_id': lot_id, 
                       'date': inv.date}
                    if change > 0:
                        value.update({'product_qty': change, 'location_id': location_id, 
                           'location_dest_id': line.location_id.id})
                    else:
                        value.update({'product_qty': -change, 'location_id': line.location_id.id, 
                           'location_dest_id': location_id})
                    move_ids.append(self._inventory_line_hook(cr, uid, line, value))

            self.write(cr, uid, [inv.id], {'state': 'confirm', 'move_ids': [
                          (
                           6, 0, move_ids)]})
            self.pool.get('stock.move').action_confirm(cr, uid, move_ids, 3=context)

        return True

    def action_cancel_draft(self, cr, uid, ids, context=None):
        """ Cancels the stock move and change inventory state to draft.
        @return: True
        """
        for inv in self.browse(cr, uid, ids, 1=context):
            self.pool.get('stock.move').action_cancel(cr, uid, [ x.id for x in inv.move_ids ], 1=context)
            self.write(cr, uid, [inv.id], {'state': 'draft'}, 1=context)

        return True

    def action_cancel_inventory(self, cr, uid, ids, context=None):
        """ Cancels both stock move and inventory
        @return: True
        """
        move_obj = self.pool.get('stock.move')
        account_move_obj = self.pool.get('account.move')
        for inv in self.browse(cr, uid, ids, 3=context):
            move_obj.action_cancel(cr, uid, [ x.id for x in inv.move_ids ], 3=context)
            for move in inv.move_ids:
                account_move_ids = account_move_obj.search(cr, uid, [('name', '=', move.name)])
                if account_move_ids:
                    account_move_data_l = account_move_obj.read(cr, uid, account_move_ids, ['state'], 3=context)
                    for account_move in account_move_data_l:
                        assert not account_move['state'] == 'posted', _('User Error!')
                        account_move_obj.unlink(cr, uid, [account_move['id']], 3=context)

            self.write(cr, uid, [inv.id], {'state': 'cancel'}, 3=context)

        return True


stock_inventory()

class stock_inventory_line(osv.osv):
    _name = 'stock.inventory.line'
    _description = 'Inventory Line'
    _rec_name = 'inventory_id'
    _order = 'location_id'
    _columns = {'inventory_id': fields.many2one('stock.inventory', 'Inventory', 6='cascade', 8=True), 'location_id': fields.many2one('stock.location', 'Location', 11=True), 
       'product_id': fields.many2one('product.product', 'Product', 11=True, 8=True), 
       'product_uom': fields.many2one('product.uom', 'Product Unit of Measure', 11=True), 
       'product_qty': fields.float('Quantity', 19=dp.get_precision('Product Unit of Measure')), 
       'company_id': fields.related('inventory_id', 'company_id', 22='many2one', 24='res.company', 26='Company', 28=True, 8=True, 29=True), 
       'prod_lot_id': fields.many2one('stock.production.lot', 'Serial Number', 32="[('product_id','=',product_id)]"), 
       'state': fields.related('inventory_id', 'state', 22='char', 26='Status', 29=True)}

    def _default_stock_location(self, cr, uid, context=None):
        try:
            location_model, location_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'stock', 'stock_location_stock')
            self.pool.get('stock.location').check_access_rule(cr, uid, [location_id], 'read', 6=context)
        except (orm.except_orm, ValueError):
            location_id = False

        return location_id

    _defaults = {'location_id': _default_stock_location}

    def on_change_product_id(self, cr, uid, ids, location_id, product, uom=False, to_date=False):
        """ Changes UoM and name if product_id changes.
        @param location_id: Location id
        @param product: Changed product_id
        @param uom: UoM product
        @return:  Dictionary of changed values
        """
        if not product:
            return {'value': {'product_qty': 0.0, 'product_uom': False, 
                         'prod_lot_id': False}}
        obj_product = self.pool.get('product.product').browse(cr, uid, product)
        uom = uom or obj_product.uom_id.id
        amount = self.pool.get('stock.location')._product_get(cr, uid, location_id, [product], {'uom': uom, 'to_date': to_date, 
           'compute_child': False})[product]
        result = {'product_qty': amount, 'product_uom': uom, 
           'prod_lot_id': False}
        return {'value': result}


stock_inventory_line()

class stock_warehouse(osv.osv):
    _name = 'stock.warehouse'
    _description = 'Warehouse'
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _columns = {'name': fields.char('Name', 5=600, 7=True, 8=True, 9='onchange'), 'company_id': fields.many2one('res.company', 'Company', 7=True, 8=True, 9='onchange'), 
       'partner_id': fields.many2one('res.partner', 'Owner Address', 17=[('kho', '=', True)], 9='onchange'), 
       'lot_input_id': fields.many2one('stock.location', 'Location Input', 7=True, 17=[('usage', '<>', 'view')], 9='onchange'), 
       'lot_stock_id': fields.many2one('stock.location', 'Location Stock', 7=True, 17=[('usage', '=', 'internal')], 9='onchange'), 
       'lot_output_id': fields.many2one('stock.location', 'Location Output', 7=True, 17=[('usage', '<>', 'view')], 9='onchange'), 
       'type_kho': fields.selection([('kho_congty', 'Kho công ty'), ('kho_taptrung', 'Kho tập trung'), ('kho_daily', 'Kho đại lý')], 'Loại hình kho', 7=True, 9='onchange'), 
       'ma_kho': fields.char('Mã Kho', 5=256, 7=True, 8=True, 9='onchange')}

    def _default_lot_input_stock_id(self, cr, uid, context=None):
        try:
            lot_input_stock_model, lot_input_stock_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'stock', 'stock_location_stock')
            self.pool.get('stock.location').check_access_rule(cr, uid, [lot_input_stock_id], 'read', 6=context)
        except (ValueError, orm.except_orm):
            lot_input_stock_id = False

        return lot_input_stock_id

    def _default_lot_output_id(self, cr, uid, context=None):
        try:
            lot_output_model, lot_output_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'stock', 'stock_location_output')
            self.pool.get('stock.location').check_access_rule(cr, uid, [lot_output_id], 'read', 6=context)
        except (ValueError, orm.except_orm):
            lot_output_id = False

        return lot_output_id

    _defaults = {'company_id': lambda self, cr, uid, c: self.pool.get('res.company')._company_default_get(cr, uid, 'stock.inventory', 3=c), 
       'lot_input_id': _default_lot_input_stock_id, 
       'lot_stock_id': _default_lot_input_stock_id, 
       'lot_output_id': _default_lot_output_id}

    def create(self, cr, uid, vals, context=None):
        if context is None:
            context = {}
        partner_pool = self.pool.get('res.partner')
        kho_id = super(stock_warehouse, self).create(cr, uid, vals, 2=context)
        kho_object = self.browse(cr, uid, kho_id, context)
        name = kho_object.name
        company_id = kho_object.company_id.id
        type_kho = kho_object.type_kho
        kh_id = partner_pool.create(cr, uid, {'name': name, 'kho': True, 
           'customer': False, 
           'is_diadiem': True, 
           'company_id': company_id, 
           'street': name, 
           'type_kho': type_kho}, 2=context)
        self.write(cr, uid, [kho_id], {'partner_id': kh_id}, 2=context)
        return kho_id


stock_warehouse()

class stock_picking_in(osv.osv):
    _name = 'stock.picking.in'
    _inherit = 'stock.picking'
    _table = 'stock_picking'
    _description = 'Incoming Shipments'

    def search(self, cr, user, args, offset=0, limit=None, order=None, context=None, count=False):
        return self.pool.get('stock.picking').search(cr, user, args, offset, limit, order, context, count)

    def read(self, cr, uid, ids, fields=None, context=None, load='_classic_read'):
        return self.pool.get('stock.picking').read(cr, uid, ids, 2=fields, 3=context, 4=load)

    def check_access_rights(self, cr, uid, operation, raise_exception=True):
        return self.pool.get('stock.picking').check_access_rights(cr, uid, operation, 2=raise_exception)

    def check_access_rule(self, cr, uid, ids, operation, context=None):
        return self.pool.get('stock.picking').check_access_rule(cr, uid, ids, operation, 2=context)

    def _workflow_trigger(self, cr, uid, ids, trigger, context=None):
        return self.pool.get('stock.picking')._workflow_trigger(cr, uid, ids, trigger, 2=context)

    def _workflow_signal(self, cr, uid, ids, signal, context=None):
        return self.pool.get('stock.picking')._workflow_signal(cr, uid, ids, signal, 2=context)

    def message_post(self, *args, **kwargs):
        """Post the message on stock.picking to be able to see it in the form view when using the chatter"""
        return self.pool.get('stock.picking').message_post(*args, **kwargs)

    def message_subscribe(self, *args, **kwargs):
        """Send the subscribe action on stock.picking model as it uses _name in request"""
        return self.pool.get('stock.picking').message_subscribe(*args, **kwargs)

    def message_unsubscribe(self, *args, **kwargs):
        """Send the unsubscribe action on stock.picking model to match with subscribe"""
        return self.pool.get('stock.picking').message_unsubscribe(*args, **kwargs)

    _columns = {'backorder_id': fields.many2one('stock.picking.in', 'Back Order of', 16={'done': [('readonly', True)], 'cancel': [
                                 (
                                  'readonly', True)]}, 20='If this shipment was split, then this field links to the shipment which contains the already processed part.', 22=True), 
       'state': fields.selection([('draft', 'Draft'),
               ('auto', 'Waiting Another Operation'),
               ('confirmed', 'Waiting Availability'),
               ('assigned', 'Ready to Receive'),
               ('done', 'Received'),
               ('cancel', 'Cancelled')], 'Status', 17=True, 22=True, 20="* Draft: not confirmed yet and will not be scheduled until confirmed\n\n                 * Waiting Another Operation: waiting for another move to proceed before it becomes automatically available (e.g. in Make-To-Order flows)\n\n                 * Waiting Availability: still waiting for the availability of products\n\n                 * Ready to Receive: products reserved, simply waiting for confirmation.\n\n                 * Received: has been processed, can't be modified or cancelled anymore\n\n                 * Cancelled: has been cancelled, can't be confirmed anymore")}
    _defaults = {'type': 'in', 'invoice_state': 'none'}


class stock_picking_out(osv.osv):
    _name = 'stock.picking.out'
    _inherit = 'stock.picking'
    _table = 'stock_picking'
    _description = 'Delivery Orders'

    def search(self, cr, user, args, offset=0, limit=None, order=None, context=None, count=False):
        return self.pool.get('stock.picking').search(cr, user, args, offset, limit, order, context, count)

    def read(self, cr, uid, ids, fields=None, context=None, load='_classic_read'):
        return self.pool.get('stock.picking').read(cr, uid, ids, 2=fields, 3=context, 4=load)

    def check_access_rights(self, cr, uid, operation, raise_exception=True):
        return self.pool.get('stock.picking').check_access_rights(cr, uid, operation, 2=raise_exception)

    def check_access_rule(self, cr, uid, ids, operation, context=None):
        return self.pool.get('stock.picking').check_access_rule(cr, uid, ids, operation, 2=context)

    def _workflow_trigger(self, cr, uid, ids, trigger, context=None):
        return self.pool.get('stock.picking')._workflow_trigger(cr, uid, ids, trigger, 2=context)

    def _workflow_signal(self, cr, uid, ids, signal, context=None):
        return self.pool.get('stock.picking')._workflow_signal(cr, uid, ids, signal, 2=context)

    def message_post(self, *args, **kwargs):
        """Post the message on stock.picking to be able to see it in the form view when using the chatter"""
        return self.pool.get('stock.picking').message_post(*args, **kwargs)

    def message_subscribe(self, *args, **kwargs):
        """Send the subscribe action on stock.picking model as it uses _name in request"""
        return self.pool.get('stock.picking').message_subscribe(*args, **kwargs)

    def message_unsubscribe(self, *args, **kwargs):
        """Send the unsubscribe action on stock.picking model to match with subscribe"""
        return self.pool.get('stock.picking').message_unsubscribe(*args, **kwargs)

    _columns = {'backorder_id': fields.many2one('stock.picking.out', 'PXK liên quan', 16={'done': [('readonly', True)], 'cancel': [
                                 (
                                  'readonly', True)]}, 20='If this shipment was split, then this field links to the shipment which contains the already processed part.', 22=True), 
       'state': fields.selection([('draft', 'Draft'),
               ('auto', 'Waiting Another Operation'),
               ('confirmed', 'Waiting Availability'),
               ('assigned', 'Ready to Deliver'),
               ('done', 'Delivered'),
               ('cancel', 'Cancelled')], 'Status', 17=True, 22=True, 20="* Draft: not confirmed yet and will not be scheduled until confirmed\n\n                 * Waiting Another Operation: waiting for another move to proceed before it becomes automatically available (e.g. in Make-To-Order flows)\n\n                 * Waiting Availability: still waiting for the availability of products\n\n                 * Ready to Deliver: products reserved, simply waiting for confirmation.\n\n                 * Delivered: has been processed, can't be modified or cancelled anymore\n\n                 * Cancelled: has been cancelled, can't be confirmed anymore")}
    _defaults = {'type': 'out'}