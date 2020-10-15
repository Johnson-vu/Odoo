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
from openerp import tools
from openerp.osv import fields, osv
from openerp.addons.decimal_precision import decimal_precision as dp

class report_stock_move(osv.osv):
    _name = 'report.stock.move'
    _description = 'Moves Statistics'
    _auto = False
    _columns = {'date': fields.date('Date', readonly=True),
     'year': fields.char('Year', size=4, readonly=True),
     'day': fields.char('Day', size=128, readonly=True),
     'month': fields.selection([('01', 'January'),
               ('02', 'February'),
               ('03', 'March'),
               ('04', 'April'),
               ('05', 'May'),
               ('06', 'June'),
               ('07', 'July'),
               ('08', 'August'),
               ('09', 'September'),
               ('10', 'October'),
               ('11', 'November'),
               ('12', 'December')], 'Month', readonly=True),
     'partner_id': fields.many2one('res.partner', 'Partner', readonly=True),
     'product_id': fields.many2one('product.product', 'Product', readonly=True),
     'company_id': fields.many2one('res.company', 'Company', readonly=True),
     'picking_id': fields.many2one('stock.picking', 'Shipment', readonly=True),
     'type': fields.selection([('out', 'Sending Goods'),
              ('in', 'Getting Goods'),
              ('internal', 'Internal'),
              ('other', 'Others')], 'Shipping Type', required=True, select=True, help='Shipping type specify, goods coming in or going out.'),
     'location_id': fields.many2one('stock.location', 'Source Location', readonly=True, select=True, help='Sets a location if you produce at a fixed location. This can be a partner location if you subcontract the manufacturing operations.'),
     'location_dest_id': fields.many2one('stock.location', 'Dest. Location', readonly=True, select=True, help='Location where the system will stock the finished products.'),
     'state': fields.selection([('draft', 'Draft'),
               ('waiting', 'Waiting'),
               ('confirmed', 'Confirmed'),
               ('assigned', 'Available'),
               ('done', 'Done'),
               ('cancel', 'Cancelled')], 'Status', readonly=True, select=True),
     'product_qty': fields.integer('Quantity', readonly=True),
     'categ_id': fields.many2one('product.category', 'Product Category'),
     'product_qty_in': fields.integer('In Qty', readonly=True),
     'product_qty_out': fields.integer('Out Qty', readonly=True),
     'value': fields.float('Total Value', required=True),
     'day_diff2': fields.float('Lag (Days)', readonly=True, digits_compute=dp.get_precision('Shipping Delay'), group_operator='avg'),
     'day_diff1': fields.float('Planned Lead Time (Days)', readonly=True, digits_compute=dp.get_precision('Shipping Delay'), group_operator='avg'),
     'day_diff': fields.float('Execution Lead Time (Days)', readonly=True, digits_compute=dp.get_precision('Shipping Delay'), group_operator='avg'),
     'stock_journal': fields.many2one('stock.journal', 'Stock Journal', select=True)}

    def init(self, cr):
        tools.drop_view_if_exists(cr, 'report_stock_move')
        cr.execute("\n            CREATE OR REPLACE view report_stock_move AS (\n                SELECT\n                        min(sm_id) as id,\n                        date_trunc('day',al.dp) as date,\n                        al.curr_year as year,\n                        al.curr_month as month,\n                        al.curr_day as day,\n                        al.curr_day_diff as day_diff,\n                        al.curr_day_diff1 as day_diff1,\n                        al.curr_day_diff2 as day_diff2,\n                        al.location_id as location_id,\n                        al.picking_id as picking_id,\n                        al.company_id as company_id,\n                        al.location_dest_id as location_dest_id,\n                        al.product_qty,\n                        al.out_qty as product_qty_out,\n                        al.in_qty as product_qty_in,\n                        al.partner_id as partner_id,\n                        al.product_id as product_id,\n                        al.state as state ,\n                        al.product_uom as product_uom,\n                        al.categ_id as categ_id,\n                        coalesce(al.type, 'other') as type,\n                        al.stock_journal as stock_journal,\n                        sum(al.in_value - al.out_value) as value\n                    FROM (SELECT\n                        CASE WHEN sp.type in ('out') THEN\n                            sum(sm.product_qty * pu.factor / pu2.factor)\n                            ELSE 0.0\n                            END AS out_qty,\n                        CASE WHEN sp.type in ('in') THEN\n                            sum(sm.product_qty * pu.factor / pu2.factor)\n                            ELSE 0.0\n                            END AS in_qty,\n                        CASE WHEN sp.type in ('out') THEN\n                            sum(sm.product_qty * pu.factor / pu2.factor) * pt.standard_price\n                            ELSE 0.0\n                            END AS out_value,\n                        CASE WHEN sp.type in ('in') THEN\n                            sum(sm.product_qty * pu.factor / pu2.factor) * pt.standard_price\n                            ELSE 0.0\n                            END AS in_value,\n                        min(sm.id) as sm_id,\n                        sm.date as dp,\n                        to_char(date_trunc('day',sm.date), 'YYYY') as curr_year,\n                        to_char(date_trunc('day',sm.date), 'MM') as curr_month,\n                        to_char(date_trunc('day',sm.date), 'YYYY-MM-DD') as curr_day,\n                        avg(date(sm.date)-date(sm.create_date)) as curr_day_diff,\n                        avg(date(sm.date_expected)-date(sm.create_date)) as curr_day_diff1,\n                        avg(date(sm.date)-date(sm.date_expected)) as curr_day_diff2,\n                        sm.location_id as location_id,\n                        sm.location_dest_id as location_dest_id,\n                        sum(sm.product_qty) as product_qty,\n                        pt.categ_id as categ_id ,\n                        sm.partner_id as partner_id,\n                        sm.product_id as product_id,\n                        sm.picking_id as picking_id,\n                            sm.company_id as company_id,\n                            sm.state as state,\n                            sm.product_uom as product_uom,\n                            sp.type as type,\n                            sp.stock_journal_id AS stock_journal\n                    FROM\n                        stock_move sm\n                        LEFT JOIN stock_picking sp ON (sm.picking_id=sp.id)\n                        LEFT JOIN product_product pp ON (sm.product_id=pp.id)\n                        LEFT JOIN product_uom pu ON (sm.product_uom=pu.id)\n                          LEFT JOIN product_uom pu2 ON (sm.product_uom=pu2.id)\n                        LEFT JOIN product_template pt ON (pp.product_tmpl_id=pt.id)\n                    GROUP BY\n                        sm.id,sp.type, sm.date,sm.partner_id,\n                        sm.product_id,sm.state,sm.product_uom,sm.date_expected,\n                        sm.product_id,pt.standard_price, sm.picking_id, sm.product_qty,\n                        sm.company_id,sm.product_qty, sm.location_id,sm.location_dest_id,pu.factor,pt.categ_id, sp.stock_journal_id)\n                    AS al\n                    GROUP BY\n                        al.out_qty,al.in_qty,al.curr_year,al.curr_month,\n                        al.curr_day,al.curr_day_diff,al.curr_day_diff1,al.curr_day_diff2,al.dp,al.location_id,al.location_dest_id,\n                        al.partner_id,al.product_id,al.state,al.product_uom,\n                        al.picking_id,al.company_id,al.type,al.product_qty, al.categ_id, al.stock_journal\n               )\n        ")


report_stock_move()

class report_stock_inventory(osv.osv):
    _name = 'report.stock.inventory'
    _description = 'Stock Statistics'
    _auto = False
    _columns = {'date': fields.datetime('Date', readonly=True),
     'year': fields.char('Year', size=4, readonly=True),
     'month': fields.selection([('01', 'January'),
               ('02', 'February'),
               ('03', 'March'),
               ('04', 'April'),
               ('05', 'May'),
               ('06', 'June'),
               ('07', 'July'),
               ('08', 'August'),
               ('09', 'September'),
               ('10', 'October'),
               ('11', 'November'),
               ('12', 'December')], 'Month', readonly=True),
     'partner_id': fields.many2one('res.partner', 'Partner', readonly=True),
     'product_id': fields.many2one('product.product', 'Product', readonly=True),
     'product_categ_id': fields.many2one('product.category', 'Product Category', readonly=True),
     'location_id': fields.many2one('stock.location', 'Location', readonly=True),
     'prodlot_id': fields.many2one('stock.production.lot', 'Lot', readonly=True),
     'company_id': fields.many2one('res.company', 'Company', readonly=True),
     'product_qty': fields.float('Quantity', digits_compute=dp.get_precision('Product Unit of Measure'), readonly=True),
     'value': fields.float('Total Value', digits_compute=dp.get_precision('Account'), required=True),
     'state': fields.selection([('draft', 'Draft'),
               ('waiting', 'Waiting'),
               ('confirmed', 'Confirmed'),
               ('assigned', 'Available'),
               ('done', 'Done'),
               ('cancel', 'Cancelled')], 'Status', readonly=True, select=True, help="When the stock move is created it is in the 'Draft' state.\n After that it is set to 'Confirmed' state.\n If stock is available state is set to 'Avaiable'.\n When the picking it done the state is 'Done'.              \nThe state is 'Waiting' if the move is waiting for another one."),
     'location_type': fields.selection([('supplier', 'Supplier Location'),
                       ('view', 'View'),
                       ('internal', 'Internal Location'),
                       ('customer', 'Customer Location'),
                       ('inventory', 'Inventory'),
                       ('procurement', 'Procurement'),
                       ('production', 'Production'),
                       ('transit', 'Transit Location for Inter-Companies Transfers')], 'Location Type', required=True),
     'scrap_location': fields.boolean('scrap')}

    def init(self, cr):
        tools.drop_view_if_exists(cr, 'report_stock_inventory')
        cr.execute("\nCREATE OR REPLACE view report_stock_inventory AS (\n    (SELECT\n        min(m.id) as id, m.date as date,\n        to_char(m.date, 'YYYY') as year,\n        to_char(m.date, 'MM') as month,\n        m.partner_id as partner_id, m.location_id as location_id,\n        m.product_id as product_id, pt.categ_id as product_categ_id, l.usage as location_type, l.scrap_location as scrap_location,\n        m.company_id,\n        m.state as state, m.prodlot_id as prodlot_id,\n\n        coalesce(sum(-pt.standard_price * m.product_qty * pu.factor / pu2.factor)::decimal, 0.0) as value,\n        coalesce(sum(-m.product_qty * pu.factor / pu2.factor)::decimal, 0.0) as product_qty\n    FROM\n        stock_move m\n            LEFT JOIN stock_picking p ON (m.picking_id=p.id)\n            LEFT JOIN product_product pp ON (m.product_id=pp.id)\n                LEFT JOIN product_template pt ON (pp.product_tmpl_id=pt.id)\n                LEFT JOIN product_uom pu ON (pt.uom_id=pu.id)\n                LEFT JOIN product_uom pu2 ON (m.product_uom=pu2.id)\n            LEFT JOIN product_uom u ON (m.product_uom=u.id)\n            LEFT JOIN stock_location l ON (m.location_id=l.id)\n            WHERE m.state != 'cancel'\n    GROUP BY\n        m.id, m.product_id, m.product_uom, pt.categ_id, m.partner_id, m.location_id,  m.location_dest_id,\n        m.prodlot_id, m.date, m.state, l.usage, l.scrap_location, m.company_id, pt.uom_id, to_char(m.date, 'YYYY'), to_char(m.date, 'MM')\n) UNION ALL (\n    SELECT\n        -m.id as id, m.date as date,\n        to_char(m.date, 'YYYY') as year,\n        to_char(m.date, 'MM') as month,\n        m.partner_id as partner_id, m.location_dest_id as location_id,\n        m.product_id as product_id, pt.categ_id as product_categ_id, l.usage as location_type, l.scrap_location as scrap_location,\n        m.company_id,\n        m.state as state, m.prodlot_id as prodlot_id,\n        coalesce(sum(pt.standard_price * m.product_qty * pu.factor / pu2.factor)::decimal, 0.0) as value,\n        coalesce(sum(m.product_qty * pu.factor / pu2.factor)::decimal, 0.0) as product_qty\n    FROM\n        stock_move m\n            LEFT JOIN stock_picking p ON (m.picking_id=p.id)\n            LEFT JOIN product_product pp ON (m.product_id=pp.id)\n                LEFT JOIN product_template pt ON (pp.product_tmpl_id=pt.id)\n                LEFT JOIN product_uom pu ON (pt.uom_id=pu.id)\n                LEFT JOIN product_uom pu2 ON (m.product_uom=pu2.id)\n            LEFT JOIN product_uom u ON (m.product_uom=u.id)\n            LEFT JOIN stock_location l ON (m.location_dest_id=l.id)\n            WHERE m.state != 'cancel'\n    GROUP BY\n        m.id, m.product_id, m.product_uom, pt.categ_id, m.partner_id, m.location_id, m.location_dest_id,\n        m.prodlot_id, m.date, m.state, l.usage, l.scrap_location, m.company_id, pt.uom_id, to_char(m.date, 'YYYY'), to_char(m.date, 'MM')\n    )\n);\n        ")


report_stock_inventory()