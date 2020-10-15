{
    "name" : "ICSC REPORT ACTION",
    "version" : "1.0",
    "author" : "oanhle@icsc.vn",
    "website" : "http://www.icsc.vn/",   
    "depends" : ["base","account","icsc_config_birtreport","stock","sale",
                 "icsc_lt_vanchuyen","icsc_lt_xacnhan_kiemsoat","icsc_lt_baocao"],
    "description" : "Report Button",       
    "data" : [
              "security/lct_customer_security.xml",
              "wizard/icsc_baocao_2702_view.xml",
              "account_invoice_view.xml" ,
              "security/ir.model.access.csv",
              ],
    "installable": True,
    "auto_install": False,
    "application": True,
}