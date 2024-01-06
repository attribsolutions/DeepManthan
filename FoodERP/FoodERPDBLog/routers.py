# class FoodERPDBLogRouter:
#     def db_for_read(self, model, **hints):
#         if model._meta.app_label == 'FoodERPDBLog':
#             return 'transactionlog_db'
#         return None

#     def db_for_write(self, model, **hints):
#         if model._meta.app_label == 'FoodERPDBLog':
#             return 'transactionlog_db'
#         return None

#     def allow_relation(self, obj1, obj2, **hints):
#         if (
#             obj1._meta.app_label == 'FoodERPDBLog' or
#             obj2._meta.app_label == 'FoodERPDBLog'
#         ):
#             return True
#         return None

#     def allow_migrate(self, db, app_label, model_name=None, **hints):
#         if app_label == 'FoodERPDBLog':
#             return db == 'transactionlog_db'
#         return None        