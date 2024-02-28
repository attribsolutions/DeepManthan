from django.urls import re_path as url ,path
from rest_framework_simplejwt import views as jwt_views

from .Views.V_MobileAppOrder import *

from .Views.V_Claim import *

from .Views.V_Discount import *

from .Views.V_Reports import *

from .Views.V_EInvoiceEwayBill import *

from .Views.V_SAPApi import *

from .Views.V_ProductionReIssue import *

from .Views.V_Production import *

from .Views.V_GRNs import *

from .Views.V_Bom import *

from .Views.V_SuperAdmin import SuperAdminView

from .Views.V_Login import *

from .Views.V_Parties import *

from .Views.V_Orders import *

from .Views.V_Companies import *

from .Views.V_CompanyGroup import *

from .Views.V_Pages import *

from .Views.V_Roles import *

from .Views.V_RoleAccess import *

from .Views.V_Modules import *

from .Views.V_PageAccess import *

from .Views.V_WorkOrder import *

from .Views.V_Items import *

from .Views.V_Invoices import *

from .Views.V_Employees import *

from .Views.V_EmployeeTypes import *

from .Views.V_States import *

from .Views.V_PriceLists import  *

from .Views.V_PartyTypes import *

from .Views.V_abc import * 

from .Views.V_SendMail import *

from .Views.V_CategoryType import *  

from .Views.V_Category import *

from .Views.V_GroupType import * 

from .Views.V_Group import * 

from .Views.V_SubGroup import *

from .Views.V_Units import * 

from .Views.V_Vehicles import *    

from .Views.V_Drivers import *

from .Views.V_VehicleTypes import *

from .Views.V_Mrps import *

from .Views.V_Margins import *

from .Views.V_GSTHSNCode import *

from .Views.V_PartySubParty import *

from .Views.V_PartyItems import *

from .Views.V_MaterialIssue import *

from .Views.V_TermsAndConditions import *

from .Views.V_GeneralMaster import *

from .Views.V_Demands import *

from .Views.V_InterbranchChallan import *

from .Views.V_InterBranchInward import *

from .Views.V_Challan import *

from .Views.V_Routes import *

from .Views.V_LoadingSheet import *

from .Views.V_Salesman import *

from .Views.V_BankMaster import *

from .Views.V_PartyWiseUpdate import *

from .Views.V_Receipts import *

from .Views.V_CreditDebit import *

from .Views.V_CommFunction import *

from .Views.V_ImportField import *

from .Views.V_PurchaseReturn import *

from .Views.V_MappingMaster import *

from .Views.V_Dashboard import *

from .Views.V_StockEntry import *

from .Views.V_R1_Reports import *

from .Views.V_R3B_Reports import *

from .Views.V_GST_Reports import *

from .Views.V_ItemSale import *

from .Views.V_StockAdjustment import *

from .Views.V_Transaction import *

from .Views.V_Cluster import *

from .Views.V_CentralServiceItemMaster import *

from .Views.V_PartyDetails import *


from .Views.V_Settings import *


urlpatterns = [
    
    # Master APIs IN Projects Add Page ,List Page
    url(r'test', AbcView.as_view()),
    url(r'SAPInvoice', SAPInvoiceView.as_view()),
    url(r'SAPOrder', SAPOrderView.as_view()),
    url(r'SAPLedger',SAPLedgerView.as_view()),
    url(r'InvoicetoSCM',InvoiceToSCMView.as_view()),
    
    url(r'MobileAppOrder$',T_MobileAppOrdersView.as_view()),
    url(r'MobileAppOrderDelete$',T_MobileAppOrdersDeleteView.as_view()),
    url(r'MobileAppOrder/([0-9]+)$',T_MobileAppOrdersView.as_view()),
    
   
    url(r'MobileAppAddProduct/([0-9]+)$',NewProductSendToMobileAppView.as_view()),
    url(r'MobileAppUpdateProduct$',NewProductSendToMobileAppView.as_view()),
    url(r'MobileAppDeleteProduct/([0-9]+)$',NewProductSendToMobileAppView.as_view()),
    
    url(r'MobileAppAddRetailer$',NewRetailerSendToMobileAppView.as_view()),
    url(r'MobileAppUpdateRetailer$',NewRetailerSendToMobileAppView.as_view()),
    url(r'MobileAppDeleteRetailer/([0-9]+)$',NewRetailerSendToMobileAppView.as_view()),
    
    url(r'Retailer/Add$',RetailerAddFromMobileAppview.as_view()),
    url(r'Retailer/Update$',RetailerUpdateFromMobileAppview.as_view()),
    url(r'Retailer/Delete/([0-9]+)$',RetailerDeleteFromMobileApp.as_view()),
    
# User 
            path('api/token/', jwt_views.TokenObtainPairView.as_view(), name='token_obtain_pair'),
            path('api/token/refresh/', jwt_views.TokenRefreshView.as_view(), name='token_refresh'),
            url(r'Registration', UserRegistrationView.as_view()),
            url(r'Login', UserLoginView.as_view()),
            url(r'ChangePassword', ChangePasswordView.as_view()),
            url(r'UserList/([0-9]+)$', UserListViewSecond.as_view()),
            url(r'UserList$', UserListView.as_view()),
            #PartyDropdownforloginpage/EmployeeID
            # url(r'Muiltiple$', MultipleReceiptView.as_view()),
            # This below API used for Dropdown populated when user have multiple role and parties.
            url(r'PartyDropdownforloginpage/([0-9]+)$', UserPartiesForLoginPage.as_view()), 
            url(r'GetEmployeeForUserCreation$',GetEmployeeViewForUserCreation.as_view()),
            url(r'GetUserDetails$',GetUserDetailsView.as_view()),
            url(r'SuperAdmin$',SuperAdminView.as_view()),
            url(r'UserPartiesForUserMaster/([0-9]+)$', UserPartiesViewSecond.as_view()),
            url(r'SendMail$', SendViewMail.as_view()),
            url(r'VerifyOTP$', VerifyOTPwithUserData.as_view()),
            url(r'GetOpeningBalance$', GetOpeningBalanceView.as_view()),
            

# Modules 
            url(r'Modules/([0-9]+)$', H_ModulesViewSecond.as_view()),
            url(r'Modules$', H_ModulesView.as_view()),
    
# Roles
            url(r'Roles/([0-9]+)$', M_RolesViewSecond.as_view()),
            url(r'Roles$', M_RolesView.as_view()),
            url(r'RolesFilter$', M_RolesViewFilter.as_view()),

    
# PageMaster 
            url(r'PageMaster/([0-9]+)$', M_PagesViewSecond.as_view()),
            url(r'PageMaster$', M_PagesView.as_view()),
            url(r'PageTypeList$', M_PageTypeView.as_view()),
            url(r'PageAccess$', H_PageAccessView.as_view()),
            url(r'ControlTypes$', ControlTypeMasterView.as_view()),
            url(r'GetFieldValidationOnControlType/([0-9]+)$', FieldValidationsView.as_view()),
            url(r'FieldValidations$', FieldValidationsViewSecond.as_view()),
            url(r'FieldValidations/([0-9]+)$', FieldValidationsViewThird.as_view()),
    
# Company 
            url(r'Company/([0-9]+)$', C_CompaniesViewSecond.as_view()),
            url(r'Company$', C_CompaniesView.as_view()),
            url(r'CompanyFilter$', C_CompaniesViewFilter.as_view()),
            url(r'GetCompanyByDivisionTypeID/([0-9]+)$', GetCompanyByDivisionType.as_view()),
            url(r'GetCompanyByEmployeeType/([0-9]+)$', GetCompanyByEmployeeType.as_view()),
    
# CompanyGroups 
            url(r'CompanyGroups/([0-9]+)$', C_CompanyGroupViewSecond.as_view()),
            url(r'CompanyGroups$', C_CompanyGroupView.as_view()),
    

# Employees 
            url(r'Employees/([0-9]+)$', M_EmployeesViewSecond.as_view()),
            url(r'Employees$', M_EmployeesView.as_view()),
            url(r'EmployeesFilter$', M_EmployeesFilterView.as_view()),
           
#EmployeeTypes           
            url(r'EmployeeTypes/([0-9]+)$', M_EmployeeTypeViewSecond.as_view()),
            url(r'EmployeeTypes$', M_EmployeeTypeView.as_view()),
            url(r'EmployeeTypesFilter$', M_EmployeeTypeFilterView.as_view()),
            
            
# ManagementEmployeeParties
            url(r'ManagementEmployeeList$', ManagementEmployeeViewList.as_view()),
            url(r'ManagementEmpPartiesFilter$', ManagementEmployeePartiesFilterView.as_view()),
            url(r'ManagementEmpParties$', ManagementEmployeePartiesSaveView.as_view()),
            url(r'ManagementEmpParties/([0-9]+)$', ManagementEmployeePartiesSaveView.as_view()),
         

# Order All APIs
            url(r'TestOrderget/([0-9]+)$',TestOrdersView.as_view()),
            url(r'Orders/([0-9]+)$', T_OrdersViewSecond.as_view()),
            url(r'Orders$', T_OrdersView.as_view()),
            url(r'OrdersFilter$', OrderListFilterView.as_view()),
            url(r'OrdersFilterSecond$', OrderListFilterViewSecond.as_view()), #PO order SO order and Challan For GRN
            # url(r'GetItemsForParty$',GetItemsForOrderView.as_view()),
            url(r'POType$',POTypeView.as_view()),
            url(r'OrderEdit$',EditOrderView.as_view()),
            url(r'OrderConfirms$',ConfirmOrderView.as_view()),
            
            

# InterBranch Order All APIs
            url(r'InterBranchesOrder/([0-9]+)$', DemandViewSecond.as_view()),           #PUT,DELETE
            url(r'InterBranchesOrder$', DemandView.as_view()),                          #POST Only
            url(r'InterBranchesOrderFilter$', DemandListFilterView.as_view()),          #POST Filter
            url(r'InterBranches$', InterBranchDivisionView.as_view()),                  #Division Dropdown
            url(r'InterBranchesItems$', InterBranchItemsView.as_view()),                #Go Button

#InterBranch Invoice  All APIs
            url(r'BranchInvoice/([0-9]+)$', InterBranchChallanViewSecond.as_view()),    #DELETE
            url(r'BranchInvoice$', InterBranchChallanView.as_view()),                   #POST Save
            url(r'InterBrancheOrderDetails$', DemandDetailsForIBChallan.as_view()),     #POST GO Button
            url(r'BranchInvoiceFilter$', InterBranchChallanListFilterView.as_view()),   #POST Filter
            
#InterBranch Inward All APIs
            url(r'InterBranchInward/([0-9]+)$', InterBranchInwardViewSecond.as_view()),
            url(r'InterBranchInward$', InterBranchInwardView.as_view()),
            url(r'InterBranchInwardFilter$', InterBranchInwardListFilterView.as_view()),
            url(r'BranchInvoiceDetails/([0-9]+)$', BranchInvoiceDetailsView.as_view()),              

    
# TermsAndCondition All APIs
            url(r'TermsAndCondtions/([0-9]+)$', TermsAndCondtionsViewSecond.as_view()),
            url(r'TermsAndCondtions$', TermsAndCondtionsView.as_view()),

# General Master All APIs
            url(r'GeneralMaster/([0-9]+)$', GeneralMasterViewSecond.as_view()),
            url(r'GeneralMaster$', GeneralMasterView.as_view()),
            url(r'GeneralMasterList$', GeneralMasterFilterView.as_view()),
            url(r'GeneralMasterType$', GeneralMasterTypeView.as_view()),
            url(r'GeneralMasterSubType$', GeneralMasterSubTypeView.as_view()),
            url(r'GeneralMasterBrandName$', GeneralMasterBrandName.as_view()),
#Invoice All APIs
            url(r'Invoicegetandupdate/([0-9]+)$', InvoiceViewEditView.as_view()), # Single Invoice GET,PUT Method                     
            url(r'Invoice/(?P<id>\d+)(?:/(?P<characters>[A-Z]+))?/$', InvoiceViewSecond.as_view()),
            url(r'Invoice$', InvoiceView.as_view()),
            url(r'GetOrderDetails$', OrderDetailsForInvoice.as_view()),
            url(r'InvoicesFilter$', InvoiceListFilterView.as_view()),
            url(r'InvoiceNoList$', InvoiceNoView.as_view()),
            url(r'BulkInvoices$', BulkInvoiceView.as_view()),
            
            url(r'Uploaded_EInvoicea/([0-9]+)/([0-9]+)$', Uploaded_EInvoice.as_view()),
            url(r'Uploaded_EwayBill/([0-9]+)/([0-9]+)$', Uploaded_EwayBill.as_view()),
            url(r'Cancel_EInvoicea/([0-9]+)/([0-9]+)$', Cancel_EInvoice.as_view()),
            url(r'Cancel_EwayBill/([0-9]+)/([0-9]+)$', Cancel_EwayBill.as_view()),
            url(r'UpdateVehicleInvoice/([0-9]+)/([0-9]+)$',UpdateVehicleInvoiceView.as_view()),
            url(r'InvoiceHide/([0-9]+)/([0-9]+)$',InvoiceHideView.as_view()),
            url(r'InvoiceBulkDelete$', InvoiceBulkDeleteView.as_view()),
            
                
#Loading Sheet All APIs
            url(r'LoadingSheet/([0-9]+)$', LoadingSheetView.as_view()),
            url(r'LoadingSheet$', LoadingSheetView.as_view()),
            url(r'LoadingSheetList$', LoadingSheetListView.as_view()),
            url(r'LoadingSheetInvoices$', LoadingSheetInvoicesView.as_view()),
            url(r'LoadingSheetPrint/([0-9]+)$',LoadingSheetPrintView.as_view()),
            url(r'MultipleInvoices/([0-9]+)$',MultipleInvoicesView.as_view()),
            
   
    
# GRN All API's
            url(r'MakeOrdersGrn$', GetOrderDetailsForGrnView.as_view()),
            url(r'GRN/([0-9]+)$',T_GRNViewSecond.as_view()),
            url(r'GRN$', T_GRNView.as_view()),
            url(r'GRNFilter$', GRNListFilterView.as_view()),
            
# GRN All API's

            url(r'Challan$',ChallanView.as_view()),  # Challan Save
            url(r'Challan/([0-9]+)$',ChallanView.as_view()),  #  delete Api
            url(r'ChallanFilter$',ChallanListFilterView.as_view()), # Challan List Api
            url(r'ChallanItems$', ChallanItemsView.as_view()),# ChallanItems Api
            url(r'ChallanItemStock$', ChallanItemStockView.as_view()),   # ChallanItemsStock Api
                    
            
                     
# Bill Of Material All API's
            url(r'Billofmaterial/([0-9]+)/([0-9]+)$',M_BOMsViewSecond.as_view()),
            url(r'Billofmaterial$', M_BOMsView.as_view()),
            url(r'BomFilter$', BOMListFilterView.as_view()),
    
# Work Order All API's
            url(r'BomDetails$', BomDetailsView.as_view()),
            url(r'WorkOrder/([0-9]+)$',WorkOrderViewSecond.as_view()),
            url(r'WorkOrder$', WorkOrderView.as_view()),
            url(r'WorkOrderFilter$', WorkOrderList.as_view()),
         
    
# Material Issues All API's
            url(r'WorkOrderDetails$', WorkOrderDetailsView.as_view()),
            url(r'MaterialIssue/([0-9]+)$',MaterialIssueViewSecond.as_view()),
            url(r'MaterialIssue$', MaterialIssueView.as_view()),
            url(r'MaterialIssueFilter$', MaterialIsssueList.as_view()),
            
#Production ALL API`s

            url(r'MaterialIssueDetails$',MaterialIssueDetailsView.as_view()),
            url(r'Production/([0-9]+)$',ProductionViewSecond.as_view()),
            url(r'Production$',ProductionView.as_view()),
            url(r'ProductionFilter$',ProductionList.as_view()),

#Production ReIssue
           
            url(r'ProductionReIssue$',ProductionReIssueView.as_view()),
            url(r'ProductionReIssue/([0-9]+)$',ProductionReIssueViewSecond.as_view()),
            url(r'ProductionMaterialIssueItem$',MaterialIssueItemsView.as_view()),
            url(r'ProductionReIsssueFilter$',ProductionReIsssueFilter.as_view()),
            
# Party_Type
            url(r'PartyTypes/([0-9]+)$', PartyTypeView.as_view()),
            url(r'PartyTypes$', PartyTypeView.as_view()),
            url(r'PartyTypesFilter$', PartyTypeListView.as_view()),

# Parties=================================================================================
            url(r'States$',M_StateView.as_view()),
            url(r'Parties/([0-9]+)$', M_PartiesViewSecond.as_view()),
            url(r'Parties$', M_PartiesView.as_view()),
            url(r'PartiesFilter$', M_PartiesFilterView.as_view()),
            url(r'ImportRetailerBulkdata$', BulkRetailerDataView.as_view()),
            url(r'Divisions/([0-9]+)$', DivisionsView.as_view()),
            url(r'PriceList/([0-9]+)$', PriceListViewSecond.as_view()),
            url(r'PriceList$', PriceListView.as_view()), 
            url(r'^CompanywisePriceLists/([0-9]+)$', CompanywisePriceListView.as_view()),         
            url(r'ImageTypes$', M_ImageTypesView.as_view()),
            url(r'GetVendorSupplierCustomer$',GetVendorSupplierCustomerListView.as_view()),
            # url(r'GetSupplier/([0-9]+)$',GetSupplierListView.as_view()),
            # url(r'GetCustomer/([0-9]+)$',GetCustomerView.as_view()),
            url(r'PartyAddressDelete/([0-9]+)$',PartyAddressView.as_view()),
            url(r'PartySettings/([0-9]+)/([0-9]+)$',PartiesSettingsDetailsView.as_view()),
            url(r'PartySettings$',PartiesSettingsDetailsView.as_view()),
            url(r'PartyStockEntry$',StockEntryPageView.as_view()),
            url(r'PartyLiveStock$',ShowOBatchWiseLiveStockView.as_view()),
            url(r'AllGSTReportsExport$', AllGSTReportsDownloadView.as_view()),
            
            
           
# State and District
            url(r'States$',M_StateView.as_view()),    
            url(r'GetDistrictOnState/([0-9]+)$',M_DistrictView.as_view()),
            url(r'GetCityOnDistrict/([0-9]+)$',M_CitiesView.as_view()),
            url(r'Cities$',M_CitiesView.as_view()),
            

# PartySubParty
            url(r'PartySubParty/([0-9]+)$',PartySubPartyViewSecond.as_view()),
            url(r'PartySubParty$',PartySubPartyView.as_view()),
            url(r'PartySubPartyList$',PartySubPartyListFilterView.as_view()),
            url(r'RetailerandSSDD$',RetailerandSSDDView.as_view()),
            url(r'CxDDDiffParty$',CxDDDiffPartiesView.as_view()),
            
# PartyWiseUpdate            
            url(r'PartyWiseUpdate$', PartyWiseUpdateView.as_view()),
            url(r'PartyWiseSave$', PartyWiseUpdateViewSecond.as_view()),

# Driver 
            url(r'DriverFilter$', DriverViewList.as_view()),
            url(r'Driver/([0-9]+)$', DriverView.as_view()),
            url(r'Driver$', DriverView.as_view()),
# Vehicle 
            url(r'VehicleTypes/([0-9]+)$', M_VehicleTypesViewSecond.as_view()),
            url(r'VehicleTypes$', M_VehicleTypesView.as_view()),
            url(r'Vehicle/([0-9]+)$', VehicleView.as_view()),
            url(r'Vehicle$', VehicleView.as_view()),
            url(r'VehicleFilter$', VehicleViewList.as_view()),
            
# Routes 
            url(r'RoutesFilter$', RouteListView.as_view()), 
            url(r'Routes/([0-9]+)$', RoutesView.as_view()), 
            url(r'Routes$', RoutesView.as_view()),
            url(r'RouteUpdateFilter$', RoutesUpdateListView.as_view()),
            url(r'RouteUpdate$',RoutesUpdateView.as_view()),               
            

# Salesman 
            url(r'SalesmanFilter$', SalesmanListView.as_view()), 
            url(r'Salesman/([0-9]+)$', SalesmanView.as_view()), 
            url(r'Salesman$', SalesmanView.as_view()),             
                
                   
#Item All APIs======================================================================================

            url(r'Items/([0-9]+)$', M_ItemsViewSecond.as_view()),
            url(r'ItemsFilter$', M_ItemsFilterView.as_view()),
            url(r'Items$', M_ItemsView.as_view()),
            url(r'ItemTag$',M_ItemTag.as_view()),
            url(r'MCUnitDetails$',MCUnitDetailsView.as_view()),
            url(r'ItemWiseUpdate$', ItemWiseUpdateView.as_view()),
            url(r'ItemWiseSave$', ItemWiseSaveView.as_view()),
            url(r'ImageUploads$', ImageUploadsView.as_view()),
            url(r'ImageUploads/([0-9]+)$', ImageUploadsView.as_view()),  #ItemID,ImageType
            url(r'ItemUnitsForMobileApp$', MC_ItemUnitsView.as_view()),
            # Select Item and Get MCItemUnits
            # url(r'GetItemUnits$',M_ItemsViewThird.as_view()),

#DiscountMaster
            url(r'DiscountMasterSave$',DiscountMasterSaveView.as_view()),
            # url(r'DiscountMaster/([0-9]+)$',DiscountMasterView.as_view()),
            # url(r'GetDiscount$',GetDiscountView.as_view()),
            url(r'DiscountMaster$',DiscountMastergo.as_view()),
            url(r'DiscountMasterr/([0-9]+)$',DiscountMastergo.as_view()),
            url(r'DiscountMasterFilter$',DiscountMasterFilter.as_view()),
            url(r'DiscountPartyType/([0-9]+)$',DiscountPartyTypeView.as_view()),
            url(r'DiscountCustomer/([0-9]+)/([0-9]+)/([0-9]+)$',DiscountCustomerView.as_view()),

# CategoryTypes
            url(r'CategoryTypes/([0-9]+)$', CategoryTypeViewSecond.as_view()),
            url(r'CategoryTypes$', CategoryTypeView.as_view()),
# Category
            url(r'Category/([0-9]+)$', CategoryViewSecond.as_view()),
            url(r'Category$', CategoryView.as_view()),
            url(r'GetCategoryByCategoryTypeID/([0-9]+)$', GetCategoryByCategoryTypeID.as_view()),
# GroupTypes
            url(r'GroupTypes/([0-9]+)$', GroupTypeViewSecond.as_view()),
            url(r'GroupTypes$', GroupTypeView.as_view()),
# Group
            url(r'Group/([0-9]+)$', GroupViewSecond.as_view()),
            url(r'Group$', GroupView.as_view()),
            url(r'GetGroupByGroupTypeID/([0-9]+)$', GetGroupByGroupTypeID.as_view()),
# SubGroups
            url(r'SubGroups/([0-9]+)$', SubGroupViewSecond.as_view()),
            url(r'SubGroups$', SubGroupView.as_view()),
            url(r'GetSubGroupByGroupID/([0-9]+)$', GetSubGroupByGroupID.as_view()),

# Unit 
            url(r'UnitList$', M_UnitsView.as_view()),

# PartyItemList
            url(r'PartyItem/([0-9]+)$',PartyItemsView.as_view()),
            url(r'PartyItem$',PartyItemsView.as_view()),
            url(r'PartyItemFilter$',PartyItemsFilterView.as_view()),
            url(r'PartyItemList$',PartyItemsListView.as_view()),
            url(r'ItemChannelWise$',ChannelWiseItemsView.as_view()),
            url(r'ItemsChannelWiseFilter$',ChannelWiseItemsFilterView.as_view()),
            url(r'CheckPartiesInChannelItem$',CheckPartiesInChanelWiseItemsList.as_view()),
            

            url(r'ItemsChannelWiseList$',ChanelWiseItemsListView.as_view()),
    
# Mrps
            url(r'Mrps$',M_MRPsView.as_view()),
            url(r'Mrps/([0-9]+)$',M_MRPsViewSecond.as_view()),
            url(r'DeleteMrpOnList/([0-9]+)$',M_MRPsViewThird.as_view()),
    
# Margins
            url(r'Margins$',M_MarginsView.as_view()),
            url(r'Margins/([0-9]+)$', M_MarginsViewSecond.as_view()),
            url(r'DeleteMarginOnList/([0-9]+)$', M_MarginsViewThird.as_view()),
    
# GstHsnCode 
            url(r'GstHsnCode$',M_GstHsnCodeView.as_view()),
            url(r'GstHsnCode/([0-9]+)$', M_GSTHSNCodeViewSecond.as_view()),
            url(r'DeleteGstHsnCodeOnList/([0-9]+)$', M_GSTHSNCodeViewThird.as_view()),
    
# GetMRP 
            url(r'GetMRP$',GETMrpDetails.as_view()),
            url(r'GetMargin$',GETMarginDetails.as_view()),
            url(r'GetGstHsncode$',GETGstHsnDetails.as_view()),
            
# BankMaster
            url(r'Bank/([0-9]+)$', BankView.as_view()),
            url(r'Bank$', BankView.as_view()),
            url(r'BankFilter$', BankListView.as_view()),
            
            url(r'PartyBanksFilter$', PartyBanksFilterView.as_view()),
            url(r'PartyBankList$', PartyBanksListView.as_view()),
            url(r'PartyBankSave$', PartyBanksSaveView.as_view()),

# Receipt
            url(r'ReceiptInvoices$', ReceiptInvoicesView.as_view()),
            url(r'Receipt/([0-9]+)$', ReceiptView.as_view()),
            url(r'Receipt$', ReceiptView.as_view()),
            url(r'ReceiptFilter$', ReceiptListView.as_view()),
            url(r'ReceiptNoList$', ReceiptNoView.as_view()),
            
# Make Receipts of Payment entries
            url(r'MakeReceiptofPayment$', MakeReceiptOfPaymentListView.as_view()),
            
#CreditDebit 
            url(r'CreditDebitNote$', CreditDebitNoteView.as_view()), 
            url(r'CreditDebitNote/([0-9]+)$', CreditDebitNoteView.as_view()),   
            url(r'CreditDebitNoteFilter$', CreditDebitNoteListView.as_view()), 
            
            url(r'Uploaded_CreditDebitNotes_EInvoice/([0-9]+)/([0-9]+)$', Uploaded_CreditDebitNotes_EInvoice.as_view()),
            url(r'Cancel_CreditDebitNotes_EInvoice/([0-9]+)/([0-9]+)$', Cancel_CreditDebitNotes_EInvoice.as_view()),
            

#ImportField
            url(r'ImportField$', ImportFieldSaveView.as_view()),  
            url(r'ImportField/([0-9]+)$', ImportFieldSaveView.as_view()),  
            url(r'ImportFieldList$', ImportFieldListView.as_view()),
            url(r'PartyImportFieldFilter$', PartyImportFieldFilterView.as_view()),
            url(r'PartyImportFieldSave$', PartyImportFieldView.as_view()),
            url(r'ImportExcelTypes$', ImportExcelTypeView.as_view()),
            url(r'ImportExcelTypesList$', ImportExcelTypeListView.as_view()),
            
# Sales Return
            url(r'ReturnItemAdd/([0-9]+)$', ReturnItemAddView.as_view()),
            url(r'PurchaseReturn/([0-9]+)$', PurchaseReturnView.as_view()),
            url(r'PurchaseReturn$', PurchaseReturnView.as_view()),
            url(r'PurchaseReturnFilter$', PurchaseReturnListView.as_view()),
            # url(r'PurchaseReturnItem/([0-9]+)$', T_PurchaseReturnView.as_view()),
            url(r'SalesReturnconsolidateItem$', SalesReturnconsolidatePurchaseReturnView.as_view()),
            url(r'ReturnItemApprove$', SalesReturnItemApproveView.as_view()),
            url(r'PurchaseReturnPrint/([0-9]+)$', PurchaseReturnPrintView.as_view()),
            url(r'ReturnImageUpdate/([0-9]+)$', ReturnImageUpdate.as_view()),
            
                    
# Single Invoice details view api for Sales Return, CreditDebitnot
            url(r'InvoiceReturnCRDR/([0-9]+)$', InvoiceViewThird.as_view()),
# Single GRNItem Details for Sales return post body Item and BatchCode
            url(r'ReturnItemBatchcode$', ReturnItemBatchCodeAddView.as_view()),

#MappingMaster
            url(r'PartyCustomerMapping$', PartyCustomerMappingView.as_view()),
            url(r'PartyCustomerMapping/([0-9]+)$', PartyCustomerMappingView.as_view()),
            url(r'ItemsMapping$', PartyItemMappingMasterView.as_view()),
            url(r'ItemsMapping/([0-9]+)$', PartyItemMappingMasterView.as_view()),
            url(r'PartyUnitsMapping$', PartyUnitMappingMasterUnitsView.as_view()),
            url(r'PartyUnitsMapping/([0-9]+)$', PartyUnitMappingMasterUnitsView.as_view()),
     

# RoleAccess========================================= 
            #SideMenu Partyid/Employeeid/CompanyID
            url(r'RoleAccess/([0-9]+)/([0-9]+)/([0-9]+)$', RoleAccessView.as_view()),
            #ListPage API 
            url(r'RoleAccessList$', RoleAccessViewList.as_view()),
            #Post Method API
            url(r'RoleAccess$', RoleAccessView.as_view()),
            #RoleAccess PAge Go button and Edit and Delete Button Role/Division/Company
            url(r'RoleAccessNewUpdated/([0-9]+)/([0-9]+)/([0-9]+)$', RoleAccessViewNewUpdated.as_view()),
            #RoleAccessGetPagesOnModule moduleid/Divisionid
            url(r'RoleAccessGetPages/([0-9]+)/([0-9]+)$', RoleAccessGetPagesOnModule.as_view()),
            #RoleAccess Page AddPage Button
            url(r'RoleAccessAddPage/([0-9]+)$', RoleAccessViewAddPage.as_view()),
    
            # Dependencies APIs IN Projects 
            url(r'showPagesListOnPageType$', showPagesListOnPageType.as_view()),
            url(r'PageMasterForRoleAccess/([0-9]+)$', PagesMasterForRoleAccessView.as_view()),
            url(r'CopyRoleAccessabc$',CopyRoleAccessView.as_view()),
            # url(r'RegenrateToken$', RegenrateToken.as_view()),

#DashBoard
            url(r'getdashboard/([0-9]+)$', DashBoardView.as_view()),

#Report
            # url(r'ProductMarginReport/([0-9]+)/([0-9]+)$',ProductAndMarginReportView.as_view()),
            url(r'ProductMarginReport',ProductAndMarginReportView.as_view()),
            url(r'OrderSummaryReport$',SummaryReportView.as_view()),
            url(r'PartyLedgerReport$',PartyLedgerReportView.as_view()),
            url(r'StockProcessing$',StockProcessingView.as_view()),
            url(r'StockReport$',StockReportView.as_view()),
            url(r'GenericSaleReport$',GenericSaleView.as_view()),
            url(r'RetailerDataReport$',RetailerDataView.as_view()),
            url(r'PurchaseGSTReport$', PurchaseGSTReportView.as_view()),
            url(r'InvoiceDataExport$', InvoiceDateExportReportView.as_view()),
            url(r'DeletedInvoiceData$', DeletedInvoiceDateExportReportView.as_view()),
            url(r'DamageStock$', StockDamageReportView.as_view()),
            url(r'ReturnReport$', ReturnReportDownloadView.as_view()),
            url(r'GSTR1Excel$',GSTR1ExcelDownloadView.as_view()),
            url(r'GSTR3BExcel$',GSTR3BDownloadView.as_view()),
            url(r'AllGSTReportsExport$', AllGSTReportsDownloadView.as_view()),
            url(r'MaterialRegister$', MaterialRegisterDownloadView.as_view()),
            url(r'CreditDebitDataExport$', CreditDebitExportReportView.as_view()),
            url(r'ReceiptDataExport$', ReceiptDataExportReportView.as_view()),
            url(r'OutStandingBalance$', OutStandingBalanceView.as_view()),
            url(r'ManPowerReport$', ManPowerReportView.as_view()),
            url(r'TCSAmountReport$', TCSAmountReportView.as_view()),
            
            
            
#ItemSaleReport
            url(r'ItemSaleReport$', ItemSaleReportView.as_view()),
            url(r'ItemSaleSupplier/([0-9]+)/([0-9]+)$',ItemSaleSupplierDropdownView.as_view()),
            url(r'ItemSaleItemList$',ItemSaleItemDropdownView.as_view()),            
                
# Claim 
            
            url(r'ClaimSummary$',ClaimSummaryView.as_view()),
            url(r'MasterClaimCreate$',MasterClaimView.as_view()),
            url(r'MasterClaimPrint$',MasterClaimPrintView.as_view()),
            url(r'Claimlist$',ClaimlistView.as_view()),
                           
# ClaimTracking
            url(r'ClaimListfortracking$',Listofclaimforclaimtracking.as_view()),
            url(r'ClaimTracking/([0-9]+)$',ClaimTrackingEntryViewSecond.as_view()),
            url(r'ClaimTracking$', ClaimTrackingEntryView.as_view()),
            url(r'ClaimTrackingList$', ClaimTrackingEntryListView.as_view()),
                 
            
# StockAdjustment
            url(r'ShowBatchesForItem/([0-9]+)/([0-9]+)$',ShowBatchesForItemView.as_view()),
            url(r'GetStockCountForParty$',GetStockCountForPartyView.as_view()),
            
# Transactionlog  
            url(r'GetEmployeeFromUser$',EmplyoeeListView.as_view()), 
            url(r'GetTransactionType$',TransactionTypeListView.as_view()),
            url(r'TransactionDetails$',TransactionTypeView.as_view()),

            url(r'TransactionJson/([0-9]+)$',TransactionJsonView.as_view()),    

# RetailerApproval Apis
            url(r'PartyListForApproval$',PartiesListForApprovalView.as_view()),
           
# Cluster 
            url(r'Cluster$',ClusterView.as_view()),
            url(r'Cluster/([0-9]+)$',ClusterViewsecond.as_view()),
          
            
# SubCluster
             url(r'SubClusters$',SubClusterView.as_view()),
             url(r'SubClusters/([0-9]+)$',SubClusterViewsecond.as_view()),
             url(r'GetSubclusterOncluster/([0-9]+)$',GetSubClusterOnclusterView.as_view()),
             
# CentralServiceItem
             url(r'CentralItemService$',CentralServiceItemView.as_view()),
             url(r'CentralItemService/([0-9]+)$',CentralServiceItemViewSecond.as_view()), 
             url(r'CentralServiceItemAssignFilter$',CentralServiceItemAssignFilterView.as_view()),
             url(r'CentralServiceItemAssign$',CentralServiceItemAssignForParty.as_view()),
             url(r'CentralServiceItem$',CentralServiceItemViewThird.as_view()),

#PartyDetails
              url(r'PartyDetails$',PartyDetailsView.as_view()),
              url(r'PartyDetails/([0-9]+)$',PartyDetailsView.as_view()),
              url(r'GetPartydetails/([0-9]+)/([0-9]+)$',GetPartydetailsView.as_view()), #Employee/GroupID  
              url(r'downloadQr/([0-9]+)/([0-9]+)$',FileDownloadView.as_view()),
              url(r'SettingsDataSave$',SettingsView.as_view()), 
             

              url(r'CxDDDiffReport$',CxDDDiffReportView.as_view()),  
            
              url(r'SystemSettings/([0-9]+)$',SystemSettingsView.as_view()),    





]