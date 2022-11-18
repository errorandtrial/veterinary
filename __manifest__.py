# -*- coding: utf-8 -*-
{
    'name': "Veterinary Clinic",

    'summary': """
        Clínica Lemoa 
    """,
    'description': """
        Veterinary clinic management module based on EquiClinic by Bilal
    """,

    'author': "ErrorAndTrial",
    'category': 'Clinic',
    'version': '1.0',

    # any module necessary for this one to work correctly
    'depends': ['account_invoicing','base','mail','document'],

    # always loaded
    'data': [
    
        'views/css_loader.xml', 
        'views/seq.xml',
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/animal.xml',
        'wizard/mail_compose_message_view.xml',
        'wizard/canelreason.xml',
        'views/appointment.xml',
        'views/evaluation.xml',
        'views/evaluation_stages.xml',        
        'views/bloodtest.xml',   
        'views/xr.xml',  
        'views/echo.xml',            
        'views/citology.xml',      
        'views/code.xml',  
        'views/menu.xml',     
        'reports/report.xml',
        'reports/citology_report.xml',
        'reports/xr_report.xml',
        'reports/bloodtest_report.xml',
        'views/email_templates.xml',
        'data/evaluation_stage.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    'images': ['static/description/banner.jpg'],
    'installable': True,
    'application': True,
    'auto_install': False,
}
