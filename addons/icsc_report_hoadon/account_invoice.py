# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>). All Rights Reserved
#    $Id$
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
# Python bytecode 2.7 (62211)
# Embedded file name: /opt/openerp/server/openerp/addons/icsc_report_hoadon/account_invoice.py
# Compiled at: 2014-10-22 15:53:27
# Decompiled by https://python-decompiler.com
from openerp import tools
from openerp.osv import osv, fields
from openerp.tools.translate import _
import datetime, openerp.addons.decimal_precision as dp
from openerp.osv.orm import Model
import time
from datetime import datetime
from time import mktime
import logging
_logger = logging.getLogger(__name__)
from dateutil.relativedelta import *
STATE_SELECTION = [
 ('doc', '*.doc'),
 ('pdf', '*.pdf'),
 ('xls', '*.xls')]

def resolve_http_redirect(url, depth=0):
    return {'type': 'ir.actions.act_url', 
       'url': url, 
       'target': 'new'}


class account_invoice(osv.osv):
    _inherit = 'account.invoice'

    def get_shop(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for data in self.browse(cr, uid, ids, 1=context):
            if data.lenh_xuat_hang_id:
                shop_id = data.lenh_xuat_hang_id.haiduong_id.id
                if shop_id == 1:
                    res[data.id] = 'LAMTHAO'
                if shop_id == 2:
                    res[data.id] = 'HAIDUONG'

        return res

    _columns = {'shop': fields.function(get_shop, 2='char', 4='Shop')}

    def print_hoadon1(self, cr, uid, ids, context=None):
        user = self.pool.get('res.users').browse(cr, uid, uid, 2=context).name
        for report in self.browse(cr, uid, ids, 2=context):
            link = False
            config = self.pool.get('icsc.config.birtreport')
            link = config.get_linkreport_user(cr, uid, uid)
            assert not link == False, _('Thông báo!')
            url = link
            url += 'M4_LT_hoadon_GTGT_2.rptdesign'
            url += '&active_id=' + str(report.id) + ''
            url += '&__format=pdf'
            return resolve_http_redirect(url, 10=0)

        return True

    def print_hoadon(self, cr, uid, ids, context=None):
        user = self.pool.get('res.users').browse(cr, uid, uid, 2=context).name
        for report in self.browse(cr, uid, ids, 2=context):
            link = False
            config = self.pool.get('icsc.config.birtreport')
            link = config.get_linkreport_user(cr, uid, uid)
            assert not link == False, _('Thông báo!')
            url = link
            url += 'M3_LT_hoadon_GTGT.rptdesign'
            url += '&active_id=' + str(report.id) + ''
            url += '&__format=pdf'
            return resolve_http_redirect(url, 10=0)

        return True

    def print_phieuxuat(self, cr, uid, ids, context=None):
        user = self.pool.get('res.users').browse(cr, uid, uid, 2=context).name
        for report in self.browse(cr, uid, ids, 2=context):
            link = False
            config = self.pool.get('icsc.config.birtreport')
            link = config.get_linkreport_user(cr, uid, uid)
            assert not link == False, _('Thông báo!')
            url = link
            url += '14_lamthao_luan_chuyen_noibo.rptdesign'
            url += '&active_id=' + str(report.id) + ''
            url += '&__format=pdf'
            return resolve_http_redirect(url, 10=0)

        return True

    def print_hoadon1_hd(self, cr, uid, ids, context=None):
        user = self.pool.get('res.users').browse(cr, uid, uid, 2=context).name
        for report in self.browse(cr, uid, ids, 2=context):
            link = False
            config = self.pool.get('icsc.config.birtreport')
            link = config.get_linkreport_user(cr, uid, uid)
            assert not link == False, _('Thông báo!')
            url = link
            url += 'HD_hoadon_GTGT_2.rptdesign'
            url += '&active_id=' + str(report.id) + ''
            url += '&__format=pdf'
            return resolve_http_redirect(url, 10=0)

        return True

    def print_hoadon_hd(self, cr, uid, ids, context=None):
        user = self.pool.get('res.users').browse(cr, uid, uid, 2=context).name
        for report in self.browse(cr, uid, ids, 2=context):
            link = False
            config = self.pool.get('icsc.config.birtreport')
            link = config.get_linkreport_user(cr, uid, uid)
            assert not link == False, _('Thông báo!')
            url = link
            url += 'HD_hoadon_GTGT.rptdesign'
            url += '&active_id=' + str(report.id) + ''
            url += '&__format=pdf'
            return resolve_http_redirect(url, 10=0)

        return True

    def print_phieuxuat_hd(self, cr, uid, ids, context=None):
        user = self.pool.get('res.users').browse(cr, uid, uid, 2=context).name
        for report in self.browse(cr, uid, ids, 2=context):
            link = False
            config = self.pool.get('icsc.config.birtreport')
            link = config.get_linkreport_user(cr, uid, uid)
            assert not link == False, _('Thông báo!')
            url = link
            url += 'HD_luanchuyen_noibo.rptdesign'
            url += '&active_id=' + str(report.id) + ''
            url += '&__format=pdf'
            return resolve_http_redirect(url, 10=0)

        return True


account_invoice()

class stock_picking_out(osv.osv):
    _inherit = 'stock.picking.out'

    def print_xuatkho(self, cr, uid, ids, context=None):
        for report in self.browse(cr, uid, ids, 1=context):
            link = False
            config = self.pool.get('icsc.config.birtreport')
            link = config.get_linkreport_user(cr, uid, uid)
            assert not link == False, _('Thông báo!')
            url = link
            url += 'M2_phieuxuatkho.rptdesign'
            url += '&donhang= ' + str(report.id) + ''
            url += '&__format=pdf'
            return resolve_http_redirect(url, 9=0)

        return True


stock_picking_out()

class icsc_phieu_vanchuyen(osv.osv):
    _inherit = 'icsc.phieu.vanchuyen'

    def print_pvc(self, cr, uid, ids, context=None):
        for report in self.browse(cr, uid, ids, 1=context):
            link = False
            config = self.pool.get('icsc.config.birtreport')
            link = config.get_linkreport_user(cr, uid, uid)
            assert not link == False, _('Thông báo!')
            url = link
            url += 'M7_lamthao_phieu_giao_nhan_2.rptdesign'
            url += '&donhang= ' + str(report.id) + ''
            url += '&__format=pdf'
            return resolve_http_redirect(url, 9=0)

        return True

    def print_pvc_hd(self, cr, uid, ids, context=None):
        for report in self.browse(cr, uid, ids, 1=context):
            link = False
            config = self.pool.get('icsc.config.birtreport')
            link = config.get_linkreport_user(cr, uid, uid)
            assert not link == False, _('Thông báo!')
            url = link
            url += 'HD_phieu_giao_nhan_2.rptdesign'
            url += '&donhang= ' + str(report.id) + ''
            url += '&__format=pdf'
            return resolve_http_redirect(url, 9=0)

        return True


icsc_phieu_vanchuyen()

class icsc_xacnhan_kiemsoat(osv.osv):
    _inherit = 'icsc.xacnhan.kiemsoat'

    def print_pks(self, cr, uid, ids, context=None):
        for report in self.browse(cr, uid, ids, 1=context):
            link = False
            config = self.pool.get('icsc.config.birtreport')
            link = config.get_linkreport_user(cr, uid, uid)
            assert not link == False, _('Thông báo!')
            url = link
            url += '39_phieu_qua_tram.rptdesign'
            url += '&active_id= ' + str(report.id) + ''
            url += '&__format=pdf'
            return resolve_http_redirect(url, 9=0)

        return True


icsc_xacnhan_kiemsoat()

class icsc_denghithanhtoan_vanchuyen(osv.osv):
    _inherit = 'icsc.denghithanhtoan.vanchuyen'
    _columns = {}


icsc_denghithanhtoan_vanchuyen()