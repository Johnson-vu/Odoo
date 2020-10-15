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
from openerp.tools.translate import _
from openerp import tools
from openerp.tools.sql import drop_view_if_exists

class stock_report_prodlots(osv.osv):
    _name = 'stock.report.prodlots'
    _description = 'Stock report by serial number'
    _auto = False
    _columns = {'qty': fields.float('Quantity', readonly=True),
     'location_id': fields.many2one('stock.location', 'Location', readonly=True, select=True),
     'product_id': fields.many2one('product.product', 'Product', readonly=True, select=True),
     'prodlot_id': fields.many2one('stock.production.lot', 'Serial Number', readonly=True, select=True)}

    def init(self, cr):
        drop_view_if_exists(cr, 'stock_report_prodlots')
        cr.execute("\n            create or replace view stock_report_prodlots as (\n                select max(id) as id,\n                    location_id,\n                    product_id,\n                    prodlot_id,\n                    sum(qty) as qty\n                from (\n                    select -max(sm.id) as id,\n                        sm.location_id,\n                        sm.product_id,\n                        sm.prodlot_id,\n                        -sum(sm.product_qty /uo.factor) as qty\n                    from stock_move as sm\n                    left join stock_location sl\n                        on (sl.id = sm.location_id)\n                    left join product_uom uo\n                        on (uo.id=sm.product_uom)\n                    where state = 'done'\n                    group by sm.location_id, sm.product_id, sm.product_uom, sm.prodlot_id\n                    union all\n                    select max(sm.id) as id,\n                        sm.location_dest_id as location_id,\n                        sm.product_id,\n                        sm.prodlot_id,\n                        sum(sm.product_qty /uo.factor) as qty\n                    from stock_move as sm\n                    left join stock_location sl\n                        on (sl.id = sm.location_dest_id)\n                    left join product_uom uo\n                        on (uo.id=sm.product_uom)\n                    where sm.state = 'done'\n                    group by sm.location_dest_id, sm.product_id, sm.product_uom, sm.prodlot_id\n                ) as report\n                group by location_id, product_id, prodlot_id\n            )")

    def unlink(self, cr, uid, ids, context = None):
        raise osv.except_osv(_('Error!'), _('You cannot delete any record!'))


stock_report_prodlots()

class stock_report_tracklots(osv.osv):
    _name = 'stock.report.tracklots'
    _description = 'Stock report by logistic serial number'
    _auto = False
    _columns = {'name': fields.float('Quantity', readonly=True),
     'location_id': fields.many2one('stock.location', 'Location', readonly=True, select=True),
     'product_id': fields.many2one('product.product', 'Product', readonly=True, select=True),
     'tracking_id': fields.many2one('stock.tracking', 'Logistic Serial Number', readonly=True, select=True)}

    def init(self, cr):
        drop_view_if_exists(cr, 'stock_report_tracklots')
        cr.execute("\n           create or replace view stock_report_tracklots as (\n\n            select max(id) as id,\n                    location_id,\n                    product_id,\n                    tracking_id,\n                    sum(qty) as name\n                from (\n                    select -max(sm.id) as id,\n                        sm.location_id,\n                        sm.product_id,\n                        sm.tracking_id,\n                        -sum(sm.product_qty /uo.factor) as qty\n                    from stock_move as sm\n                    left join stock_location sl\n                        on (sl.id = sm.location_id)\n                    left join product_uom uo\n                        on (uo.id=sm.product_uom)\n                    where state = 'done'\n                    group by sm.location_id, sm.product_id, sm.product_uom, sm.tracking_id\n                    union all\n                    select max(sm.id) as id,\n                        sm.location_dest_id as location_id,\n                        sm.product_id,\n                        sm.tracking_id,\n                        sum(sm.product_qty /uo.factor) as qty\n                    from stock_move as sm\n                    left join stock_location sl\n                        on (sl.id = sm.location_dest_id)\n                    left join product_uom uo\n                        on (uo.id=sm.product_uom)\n                    where sm.state = 'done'\n                    group by sm.location_dest_id, sm.product_id, sm.product_uom, sm.tracking_id\n                ) as report\n                group by location_id, product_id, tracking_id\n            )")

    def unlink(self, cr, uid, ids, context = None):
        raise osv.except_osv(_('Error!'), _('You cannot delete any record!'))


stock_report_tracklots()

class report_stock_lines_date(osv.osv):
    _name = 'report.stock.lines.date'
    _description = 'Dates of Inventories'
    _auto = False
    _order = 'date'
    _columns = {'id': fields.integer('Inventory Line Id', readonly=True),
     'product_id': fields.many2one('product.product', 'Product', readonly=True, select=True),
     'date': fields.datetime('Latest Inventory Date')}

    def init(self, cr):
        drop_view_if_exists(cr, 'report_stock_lines_date')
        cr.execute("\n            create or replace view report_stock_lines_date as (\n                select\n                p.id as id,\n                p.id as product_id,\n                max(s.date) as date\n            from\n                product_product p\n                    left outer join stock_inventory_line l on (p.id=l.product_id)\n                    left join stock_inventory s on (l.inventory_id=s.id)\n                and s.state = 'done'\n                where p.active='true'\n                group by p.id\n            )")


report_stock_lines_date()