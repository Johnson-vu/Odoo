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

from openerp import netsvc

from datetime import datetime
from dateutil.relativedelta import relativedelta
import time
from openerp.osv import fields, osv
from openerp.tools.translate import _
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT

import openerp.addons.decimal_precision as dp

STATE_SELECTION = [
        ('doc', '*.doc'),     
        ('pdf', '*.pdf'),
        ('xls', '*.xls')
      
    ]
def resolve_http_redirect(url, depth=0):
        #return redirect(new_path, code)
        return {
        'type': 'ir.actions.act_url',
        'url':url,
        'target': 'new'
        }
class icsc_report_hoadongtgt(osv.osv):
    _name= 'icsc.report.hoadongtgt'
    _columns = {
        'hoa_don':fields.many2one('account.invoice','Hóa đơn',required=True),
#          'type': fields.selection(STATE_SELECTION, 'Loại file báo cáo', required=True),
    }
    def default_get(self, cr, uid, fields, context=None):
        """ To get default values for the object.
        @param self: The object pointer.
        @param cr: A database cursor
        @param uid: ID of the user currently logged in
        @param fields: List of fields for which we want default values
        @param context: A standard dictionary
        @return: A dictionary which of fields with values.
        """
        if context is None:
            context = {}
        res = super(icsc_report_hoadongtgt, self).default_get(cr, uid, fields, context=context)
        prod_obj = self.pool.get('account.invoice')
        prod = prod_obj.browse(cr, uid, context.get('active_id'), context=context)
        if 'hoa_don' in fields:
            res.update({'hoa_don': prod.id})
#         if 'type' in fields:
#             res.update({'type': 'doc'})
        return res
        
    def print_hoadon(self, cr, uid, ids,context=None): 
        #get user
        user=self.pool.get('res.users').browse(cr, uid,uid, context=context).name
        for report in self.browse(cr, uid,ids, context=context):
            #lay link server tomcat
            link=False
            config=self.pool.get('icsc.config.birtreport')
            sever_ids=config.search(cr, uid, [('hoat_dong','=',True)], context=context)
            for field in config.browse(cr, uid, sever_ids, context=context):
                link=field.name
            if link==False:
                raise osv.except_osv(_('Thông báo!'), _('Trước tiên, bạn phải cấu hình server tomcat cho báo cáo!.') )
                
            url = link
            url += "M3_LT_hoadon_GTGT.rptdesign"
            url += "&active_id="+str(report.hoa_don.id) + ""  
            url += "&user_id="+str(user) + ""           
            url += "&__format=pdf"
            return resolve_http_redirect(url,depth=0)
        return True
   
icsc_report_hoadongtgt()
class icsc_report_hoadongtgt1(osv.osv):
    _name= 'icsc.report.hoadongtgt1'
    _columns = {
        'hoa_don':fields.many2one('account.invoice','Hóa đơn',required=True),
#          'type': fields.selection(STATE_SELECTION, 'Loại file báo cáo', required=True),
    }
    def default_get(self, cr, uid, fields, context=None):
        """ To get default values for the object.
        @param self: The object pointer.
        @param cr: A database cursor
        @param uid: ID of the user currently logged in
        @param fields: List of fields for which we want default values
        @param context: A standard dictionary
        @return: A dictionary which of fields with values.
        """
        if context is None:
            context = {}
        res = super(icsc_report_hoadongtgt1, self).default_get(cr, uid, fields, context=context)
        prod_obj = self.pool.get('account.invoice')
        prod = prod_obj.browse(cr, uid, context.get('active_id'), context=context)
        if 'hoa_don' in fields:
            res.update({'hoa_don': prod.id})
        return res
        
    def print_hoadon1(self, cr, uid, ids,context=None): 
        user=self.pool.get('res.users').browse(cr, uid,uid, context=context).name
        for report in self.browse(cr, uid,ids, context=context):
            #lay link server tomcat
            link=False
            config=self.pool.get('icsc.config.birtreport')
            sever_ids=config.search(cr, uid, [('hoat_dong','=',True)], context=context)
            for field in config.browse(cr, uid, sever_ids, context=context):
                link=field.name
            if link==False:
                raise osv.except_osv(_('Thông báo!'), _('Trước tiên, bạn phải cấu hình server tomcat cho báo cáo!.') )
                
            url = link
            url += "M4_LT_hoadon_GTGT_2.rptdesign"
            url += "&active_id="+str(report.hoa_don.id) + ""  
            url += "&user_id="+str(user) + ""           
            url += "&__format=pdf"
            return resolve_http_redirect(url,depth=0)
        return True
   
icsc_report_hoadongtgt1()
class icsc_report_phieuxuatkho_vanchuyen(osv.osv):
    _name= 'icsc.report.phieuxuatkho.vanchuyen'
    _columns = {
        'hoa_don':fields.many2one('account.invoice','Hóa đơn',required=True),
#          'type': fields.selection(STATE_SELECTION, 'Loại file báo cáo', required=True),
    }
    def default_get(self, cr, uid, fields, context=None):
        """ To get default values for the object.
        @param self: The object pointer.
        @param cr: A database cursor
        @param uid: ID of the user currently logged in
        @param fields: List of fields for which we want default values
        @param context: A standard dictionary
        @return: A dictionary which of fields with values.
        """
        if context is None:
            context = {}
        res = super(icsc_report_phieuxuatkho_vanchuyen, self).default_get(cr, uid, fields, context=context)
        prod_obj = self.pool.get('account.invoice')
        prod = prod_obj.browse(cr, uid, context.get('active_id'), context=context)
        if 'hoa_don' in fields:
            res.update({'hoa_don': prod.id})
#         if 'type' in fields:
#             res.update({'type': 'doc'})
        return res
        
    def print_phieuxuat(self, cr, uid, ids,context=None): 
        user=self.pool.get('res.users').browse(cr, uid,uid, context=context).name
        for report in self.browse(cr, uid,ids, context=context):
            #lay link server tomcat
            link=False
            config=self.pool.get('icsc.config.birtreport')
            sever_ids=config.search(cr, uid, [('hoat_dong','=',True)], context=context)
            for field in config.browse(cr, uid, sever_ids, context=context):
                link=field.name
            if link==False:
                raise osv.except_osv(_('Thông báo!'), _('Trước tiên, bạn phải cấu hình server tomcat cho báo cáo!.') )
                
            url = link
            url += "14_lamthao_luan_chuyen_noibo.rptdesign"
            url += "&active_id="+str(report.hoa_don.id) + ""  
            url += "&user_id="+str(user) + ""           
            url += "&__format=pdf"
            return resolve_http_redirect(url,depth=0)
        return True
   
icsc_report_phieuxuatkho_vanchuyen()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

