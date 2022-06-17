from django.urls import re_path as url


from .Views.V_Orders import *

from .Views.V_Companies import *

from .Views.V_Pages import *

from .Views.V_Roles import *

from .Views.V_RoleAccess import *

from .Views.V_Modules import *
# from  .Views.V_Login import UserLoginV iew

from .Views.V_PageAccess import *

from .Views.V_Designations import *

from .Views.V_Login import *

from .Views.V_Items import *

from .Views.V_Employees import *

from .Views.V_Invoices import *






urlpatterns = [
    url(r'Registration', UserRegistrationView.as_view()),
    url(r'Login', UserLoginView.as_view()),
    
    url(r'UserList/([0-9]+)', UserListViewSecond.as_view()),
    url(r'UserList', UserListView.as_view()),
    
    url(r'H_Modules/([0-9]+)', H_ModulesViewSecond.as_view()),
    url(r'H_Modules', H_ModulesView.as_view()),
    
    url(r'RoleAccess', RoleAccessClass.as_view()),
    
    url(r'M_Roles/([0-9]+)$', M_RolesViewSecond.as_view()),
    url(r'M_Roles', M_RolesView.as_view()),
    
    # url(r'H_SubModules/([0-9]+)$', H_SubModulesViewSecond.as_view()),
    # url(r'H_SubModules', H_SubModulesView.as_view()),

    url(r'PagesMaster/([0-9]+)$', M_PagesViewSecond.as_view()),
    url(r'PagesMaster', M_PagesView.as_view()),
    url(r'showPagesListOnPageType/([0-9]+)$', showPagesListOnPageType.as_view()),
    
    url(r'PageAccess', H_PageAccessView.as_view()),
   

    url(r'C_Companies/([0-9]+)$', C_CompaniesViewSecond.as_view()),
    url(r'C_Companies$', C_CompaniesView.as_view()),

    url(r'C_CompanyGroups/([0-9]+)$', C_CompanyGroupsViewSecond.as_view()),
    url(r'C_CompanyGroups$', C_CompanyGroupsView.as_view()),

    # url(r'M_DivisionType/([0-9]+)$', M_DivisionTypeViewSecond.as_view()),
    # url(r'M_DivisionType$', M_DivisionTypeView.as_view()),
    
    url(r'T_Orders/([0-9]+)$', T_OrdersViewSecond.as_view()),
    url(r'T_Orders', T_OrdersView.as_view()),
    url(r'Designations/([0-9]+)$', M_DesignationsViewSecond.as_view()),
    url(r'Designations$',M_DesignationsView.as_view()),
    url(r'M_Items/([0-9]+)$', M_ItemsViewSecond.as_view()),
    url(r'M_Items', M_ItemsView.as_view()),
 
    url(r'M_Employees/([0-9]+)', M_EmployeesViewSecond.as_view()),
    url(r'M_Employees', M_EmployeesView.as_view()),
    url(r'T_Invoices/([0-9]+)$', T_InvoicesViewSecond.as_view()),
    url(r'T_Invoices', T_InvoiceView.as_view()),
  
     
]