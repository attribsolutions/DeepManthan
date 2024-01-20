# class SweetPOSRouter:
#     def db_for_read(self, model, **hints):
#         if model._meta.app_label == 'FoodERPApp':
#             return 'default'
#         elif model._meta.app_label == 'SweetPOS':
#             return 'sweetpos_db'
#         return None

#     def db_for_write(self, model, **hints):
#         if model._meta.app_label == 'FoodERPApp':
#             return 'default'
#         elif model._meta.app_label == 'SweetPOS':
#             return 'sweetpos_db'
#         return None

#     def allow_relation(self, obj1, obj2, **hints):
#         if (
#             obj1._meta.app_label == 'FoodERPApp' or
#             obj2._meta.app_label == 'FoodERPApp'
#         ) or (
#             obj1._meta.app_label == 'SweetPOS' or
#             obj2._meta.app_label == 'SweetPOS'
#         ):
#             return True
#         return None

#     def allow_migrate(self, db, app_label, model_name=None, **hints):
#         if app_label == 'SweetPOS' or app_label == 'FoodERPApp':
#             return db in[ 'sweetpos_db','default']
#         return None        