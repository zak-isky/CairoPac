# -*- coding: utf-8 -*-
# from odoo import http


# class CairopacProductCategoryType(http.Controller):
#     @http.route('/cairopac_product_category_type/cairopac_product_category_type', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/cairopac_product_category_type/cairopac_product_category_type/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('cairopac_product_category_type.listing', {
#             'root': '/cairopac_product_category_type/cairopac_product_category_type',
#             'objects': http.request.env['cairopac_product_category_type.cairopac_product_category_type'].search([]),
#         })

#     @http.route('/cairopac_product_category_type/cairopac_product_category_type/objects/<model("cairopac_product_category_type.cairopac_product_category_type"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('cairopac_product_category_type.object', {
#             'object': obj
#         })
