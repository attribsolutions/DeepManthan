from django.urls import re_path as url ,path

from .Views.V_CashierSummary import SPOSCashierSummaryList

from .Views.V_SPOSStockProcessing import *

from .Views.V_SPOSInvoices import *

from .Views.V_SweetPosRoleAccess import *

from .Views.V_SweetPoSItemGroup import *

from .Views.V_SweetPoSUsers import *

from .Views.V_SPOSstock import *


urlpatterns = [
    
    # Master APIs IN Projects Add Page ,List Page
    url(r'SPOSroleaccess$', SweetPosRoleAccessView.as_view()),
    url(r'Lspos$', SPOSLog_inView.as_view()),
    url(r'ItemGroupandSubgroup$', ItemGroupandSubgroupView.as_view()),
    url(r'ItemList/([0-9]+)$', ItemListView.as_view()),
    url(r'InsertSweetPOSSaleList$', SPOSInvoiceView.as_view()),
    url(r'GETMaxSweetPOSSaleIDByClientID/([0-9]+)/([0-9]+)$', SPOSMaxsaleIDView.as_view()),
    url(r'StockEntry$', StockView.as_view()),
    url(r'SPOSStockReport$', SPOSStockReportView.as_view()), 


    #User
    url(r'SPOSUsers$', SweetPOSUsersView.as_view()),
    url(r'SweetPOSSingleUser/([0-9]+)$', SweetPOSSingleUserView.as_view()),
    url(r'SPOSUsersOfDivision/(?P<Division_id>\d+)$',SweetPOSUsersSecondView.as_view()),    
    url(r'sposroleslist$', SweetPOSRolesView.as_view()),
    url(r'StockProcesSPOS$',SPOSStockProcessingView.as_view()),
    url(r'Invoice/(?P<id>\d+)(?:/(?P<characters>[A-Z]+))?$',SPOSInvoiceViewSecond.as_view()),
    url(r'CashierSummary$',SPOSCashierSummaryList.as_view()),
    url(r'UpdateCustomerVehiclePOSinvoice$',UpdateCustomerVehiclePOSInvoiceView.as_view()),
    url(r'posDeletEInvoicE$',DeleteInvoiceView.as_view()),
    url(r'GETMaxPOSDeletedInvoiceIDByClientID/([0-9]+)/([0-9]+)$', SPOSMaxDeletedInvoiceIDView.as_view()),
    url(r'TopSaleItemsOfFranchise$', TopSaleItemsOfFranchiseView.as_view()),
    ]
