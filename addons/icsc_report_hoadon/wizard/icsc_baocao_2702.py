# -*- coding: utf-8 -*-
from openerp.osv import osv, fields
from datetime import date
import datetime

def resolve_http_redirect(url, depth=0):
        #return redirect(new_path, code)
        return {
        'type': 'ir.actions.act_url',
        'url':url,
        'target': 'new'
        }
class icsc_print_2702(osv.osv):
    _name = 'icsc.print.2702'
    _columns = { 
                 'dv_vanchuyen' : fields.many2one('res.partner', 'Đơn vị vận chuyển',
                                            domain=[('supplier', '=', True)], required=True),
                 'ngay_bd': fields.date('Từ ngày', required=True),
                 'ngay_kt': fields.date('Đến ngày', required=True),
                 'chitiet_ids': fields.one2many('icsc.print.2702.chitiet', 'phieu_id', 'Chi tiết'),
                 'name': fields.char('Mô tả'),
                 'parent_id': fields.many2one('icsc.denghithanhtoan.vanchuyen', 'DNTT'),
                }
    
    def default_get(self, cr, uid, fields, context=None):
        if context is None:
            context = {}
        vals= []
        data_pool = self.pool.get('icsc.denghithanhtoan.vanchuyen')
        data_obj = data_pool.browse(cr, uid, context.get('active_id', False))      
        res = super(icsc_print_2702, self).default_get(cr, uid, fields, context=context) 
        if data_obj.id:
            dv_vanchuyen = data_obj.tennha_vanchuyen.id 
            ngay_bd = data_obj.thanhtoan_tungay
            ngay_kt = data_obj.thanhtoan_denngay
            if 'dv_vanchuyen' in fields:
                res.update({'dv_vanchuyen': dv_vanchuyen})
            if 'ngay_bd' in fields:
                res.update({'ngay_bd': ngay_bd})
            if 'ngay_kt' in fields:
                res.update({'ngay_kt': ngay_kt})
            if 'parent_id' in fields:
                res.update({'parent_id': context.get('active_id', False)})
#         self.action_load_data(self, cr, uid, context.get('active_id', False), context=None)
        chitiet_pool = self.pool.get('icsc.print.2702.chitiet')
        pvc_id = []
        pvc_id_tt = []
        cr.execute("""delete from icsc_print_2702""")
        query = """
        select id from
        (
            select distinct pc.id as id, 
            sum(case when COALESCE(pvc.tung_phan,FALSE)=true then ct.kl_dangvc_dukien else ct.kl_vc end) as slps
            from icsc_phieu_vanchuyen pvc
            left join icsc_phieu_vanchuyen_chitiet ct on ct.phieu_id = pvc.id
            left join product_product p on ct.product_id = p.id
            left join product_template pt on p.product_tmpl_id = pt.id
            left join product_category pc on pt.categ_id = pc.id
            left join res_partner rp on rp.id = pvc.congty_vc
            where pvc.state not in ('draft','cancel') and ct.state not in ('draft','cancel')
            and pvc.ngay_vc between '%s'::date and '%s'::date and rp.id = %s
            group by pc.id     
        ) a order by slps desc       
        """ % (ngay_bd, ngay_kt, dv_vanchuyen)
        cr.execute(query)
        for line in cr.dictfetchall():
            nhomsp = False
            category_id = line['id']
            count = ps = tt = 0
            # dem so phieu vc
            query_ps = """select pvc.id as pvc_id
                         from icsc_phieu_vanchuyen pvc
                         left join icsc_phieu_vanchuyen_chitiet ct on ct.phieu_id = pvc.id
                         left join product_product p on ct.product_id = p.id
                         left join product_template pt on p.product_tmpl_id = pt.id
                         left join product_category pc on pt.categ_id = pc.id
                         left join res_partner rp on rp.id = pvc.congty_vc
                         where pvc.state not in ('draft','cancel') and ct.state not in ('draft','cancel')
                         and pvc.ngay_vc between '%s'::date and '%s'::date and rp.id = %s and pc.id=%s                    
                         """ % (ngay_bd, ngay_kt, dv_vanchuyen, category_id)
            cr.execute(query_ps)
            for item_ps in cr.dictfetchall():
                if item_ps['pvc_id'] not in pvc_id:
                    ps += 1
                    pvc_id.append(item_ps['pvc_id'])
            query_tt = """select pvc.id as pvc_id
                        from icsc_denghithanhtoan_vanchuyen dn
                        left join icsc_denghithanhtoan_vanchuyen_chitiet dnt on dnt.phieu_id = dn.id
                        left join icsc_phieu_vanchuyen pvc on pvc.id = dnt.so_phieu_vc
                        left join icsc_phieu_vanchuyen_chitiet ct on ct.phieu_id = pvc.id
                        left join product_product p on ct.product_id = p.id
                        left join product_template pt on p.product_tmpl_id = pt.id
                        left join product_category pc on pt.categ_id = pc.id
                        left join res_partner rp on rp.id = pvc.congty_vc
                        where dn.state not in ('draft','cancel') and pvc.state not in ('draft','cancel')
                        and dn.thanhtoan_tungay >= '%s'::date and dn.thanhtoan_denngay <= '%s'::date
                        and rp.id = %s and pc.id = %s                    
                         """ % (ngay_bd, ngay_kt, dv_vanchuyen, category_id)
            cr.execute(query_tt)
            for item_tt in cr.dictfetchall():
                if item_tt['pvc_id'] not in pvc_id_tt:
                    tt += 1
                    pvc_id_tt.append(item_tt['pvc_id'])
            vals.append({
                         'category_id': category_id,
                         'so_phieu_ps': ps, 
                         'so_phieu_tt': tt,
                         'so_phieu_ton': ps - tt,
                        })
            if 'chitiet_ids' in fields:
                res.update({'chitiet_ids': vals})  
        return res
    
    def _check_category(self, cr, uid, orders_line_list, category_id):
        if len(orders_line_list) > 0:
            for line_id in orders_line_list:
                orderline = self.pool.get('icsc.thanhtoan.vanchuyen.chitiet').browse(cr, uid, line_id)
                prod_id = orderline.category_id.id                
                if prod_id == category_id:
                    return line_id
        return False
    
    
    def merge_move_line(self, cr, uid, order_id, context=None):
        picking_obj = self.browse(cr, uid, order_id, context)
        if picking_obj:
            move_lines = picking_obj.chitiet_ids
            orders_line_list = []
            for line in move_lines:
                if line.category_id:
                    category_id = line.category_id.id
                    product_qty2 = line.so_phieu  
                    line_get = self._check_category(cr, uid, orders_line_list, category_id)
                    if line_get:
                        move1 = self.pool.get('icsc.thanhtoan.vanchuyen.chitiet').browse(cr, uid, line_get)
                        product_qty1 = move1.so_phieu                        
                        self.pool.get('icsc.thanhtoan.vanchuyen.chitiet').write(cr, uid, line_get, {'so_phieu': product_qty1 + product_qty2})
                        query = """delete from icsc_print_2702_chitiet where id=%s"""
                        cr.execute(query, (line.id,))
                    else:
                        orders_line_list.append(line.id)              
        return True
    
    def print_dntt(self, cr, uid, ids, context=None): 
        cha_pool = self.pool.get('icsc.denghithanhtoan.vanchuyen')
        for report in self.browse(cr, uid, ids, context=context):
            parent_id = report.parent_id.id
            temp = cha_pool.browse(cr, uid, parent_id, context=context)
            link = False
            config=self.pool.get('icsc.config.birtreport')
            link = config.get_linkreport_user(cr, uid, uid)
            if link==False:
                raise osv.except_osv(_('Thông báo!'), _('Trước tiên, bạn phải cấu hình server tomcat cho báo cáo!.') )
            url = link
            url += "31_2_thanhtoan_kl_dg_cp.rptdesign"
            url += "&dv_vanchuyen=%s"%(temp.tennha_vanchuyen.id)
            url += "&tu_ngay=%s"%(temp.thanhtoan_tungay)
            url += "&den_ngay=%s"%(temp.thanhtoan_denngay)  
            url += "&__format=pdf"
            return resolve_http_redirect(url,depth=0)
        return True
    
icsc_print_2702()

class icsc_print_2702_chitiet(osv.osv):
    _name = 'icsc.print.2702.chitiet'
    _order = 'id desc'
    _columns = { 
                 'category_id' : fields.many2one('product.category', 'Loại sản phẩm', ondelete="cascade"),
                 'so_phieu_ps' : fields.integer('Phiếu phát sinh'),
                 'so_phieu_tt' : fields.integer('Phiếu thanh toán'),
                 'so_phieu_ton' : fields.integer('Phiếu tồn'),
                 'phieu_id': fields.many2one('icsc.print.2702', 'Thanh toán' , ondelete="cascade"),
                }
icsc_print_2702_chitiet()
