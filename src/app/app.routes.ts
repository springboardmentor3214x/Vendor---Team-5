import { Routes } from '@angular/router';
import { authGuard } from './core/guards/auth.guard';
import { roleGuard } from './core/guards/role.guard';
import { LoginComponent } from './features/auth/login/login';
import { ForgotPasswordComponent } from './features/auth/forgot-password/forgot-password';
import { ResetPasswordComponent } from './features/auth/reset-password/reset-password';
import { RegisterComponent } from './features/auth/register/register';
import { DashboardComponent } from './features/dashboard/dashboard';
import { UserManagementComponent } from './features/user-management/user-management';
import { ReportsComponent } from './features/reports/reports';

import { FinanceOfficerComponent } from './features/finance-officer/finance-officer';
import { PurchaseOrderComponent } from './features/purchase-order/purchase-order';
import { InvoiceManagementComponent } from './features/invoice-management/invoice-management';
import { PaymentDetailsComponent } from './features/payment-details/payment-details';
import { VendorComponent} from './features/vendor/vendor';
import { VendorProfileComponent } from './features/vendor-profile/vendor-profile';
import { OrdersComponent } from './features/orders/orders';
import { ContractsComponent } from './features/contracts/contracts';
import { CommunicationComponent } from './features/communication/communication';
import { AuditorComponent } from './features/auditor/auditor';
import { Notifications } from './features/notifications/notifications';
import { ReportComponent } from './features/report/report';
import { ComplianceComponent } from './features/compliance/compliance';
import { AuditLogsComponent } from './features/audit-logs/audit-logs';
import { AnalyticsComponent } from './features/analytics/analytics';
import { ProfileComponent } from './features/profile/profile';
import { SupplyChainManagerComponent } from './features/supply-chain-manager/supply-chain-manager';
import { VendorPerformanceComponent } from './features/vendor-performance/vendor-performance';
import { VendorReliabilityComponent } from './features/vendor-reliability/vendor-reliability';
import { ProcurementTrackingComponent } from './features/procurement-tracking/procurement-tracking';
import { ProcurementManagementComponent } from './features/procurement-management/procurement-management';
import { VendorManagementComponent } from './features/vendor-management/vendor-management';
import { ContractComponent } from './features/contract/contract';
import { PurchaseOrdersComponent } from './features/purchase-orders/purchase-orders';
import { CreatePurchaseOrderComponent } from './features/create-purchase-order/create-purchase-order';
import { VendorManagementsComponent } from './features/vendor-managements/vendor-managements';
import { VendorListComponent } from './features/vendor-list/vendor-list';
import { AddVendorComponent } from './features/add-vendor/add-vendor';
import { VendorDocumentComponent } from './features/vendor-document/vendor-document';
import { VendorDetailsComponent } from './features/vendor-details/vendor-details';
import { EditVendorComponent } from './features/edit-vendor/edit-vendor';
import { VendorApprovalComponent } from './features/vendor-approval/vendor-approval';
import { VendorStatusComponent } from './features/vendor-status/vendor-status';
import { ProcurementComponent } from './features/procurement/procurement';
import { ProcurementsComponent } from './features/procurements/procurements';
import { ProcurementRequestComponent } from './features/procurement-request/procurement-request';
import { RequestListComponent } from './features/request-list/request-list';
import { ApprovalComponent } from './features/approval/approval';
import { VendorAssignmentComponent } from './features/vendor-assignment/vendor-assignment';
import { PurchaseOrdersCreationComponent } from './features/purchase-orders-creation/purchase-orders-creation';
import { PurchaseOrdersDetailsComponent } from './features/purchase-orders-details/purchase-orders-details';
import { ProcurementStatusManagementComponent } from './features/procurement-status-management/procurement-status-management';
import { OrderTrackingComponent } from './features/order-tracking/order-tracking';
import { InvoiceManagementsComponent } from './features/invoice-managements/invoice-managements';
import { DeliveryPerformanceMonitoringComponent } from './features/delivery-performance-monitoring/delivery-performance-monitoring';
import { ProductQualityEvaluationComponent } from './features/product-quality-evaluation/product-quality-evaluation';
import { CommunicationResponseTrackingComponent } from './features/communication-response-tracking/communication-response-tracking';
import { ServiceRatingComponent } from './features/service-rating/service-rating';
import { PerformanceHistoryComponent } from './features/performance-history/performance-history';
import { VendorRankingComponent } from './features/vendor-ranking/vendor-ranking';
import { PerformanceMetricsComponent } from './features/performance-metrics/performance-metrics';
export const routes: Routes = [

  {
    path: '',
    redirectTo: 'login',
    pathMatch: 'full'
  },

  {
    path: 'login',
    component: LoginComponent
  },
  {
    path: 'register',
    component: RegisterComponent
  },

  {
    path: 'forgot-password',
    component: ForgotPasswordComponent
  },

  {
    path: 'reset-password',
    component: ResetPasswordComponent
  },

  {
    path: 'dashboard',
    component: DashboardComponent,
    canActivate: [authGuard]
  },

  {
    path: 'user-management',
    component: UserManagementComponent,
    canActivate: [authGuard, roleGuard],
    data: { roles: ['Administrator'] }
  },

  {
    path: 'reports',
    component: ReportsComponent,
    canActivate: [authGuard]
  },

  {
    path: 'finance-officer',
    component: FinanceOfficerComponent,
    canActivate: [authGuard, roleGuard],
    data: { roles: ['Finance Officer'] }
  },

  {
    path: 'purchase-order',
    component: PurchaseOrderComponent,
    canActivate: [authGuard]
  },

  {
    path: 'invoice-management',
    component: InvoiceManagementComponent,
    canActivate: [authGuard]
  },

  {
    path: 'payment-details',
    component: PaymentDetailsComponent,
     canActivate: [authGuard]
  },
   {
    path: 'vendor',
    component: VendorComponent,
    canActivate: [authGuard, roleGuard],
    data: { roles: ['Vendor'] }
  },
   {
    path: 'vendor-profile',
    component: VendorProfileComponent,
     canActivate: [authGuard]
  },
  {
    path: 'orders',
    component: OrdersComponent,
     canActivate: [authGuard]
  },
  {
    path: 'contracts',
    component: ContractsComponent,
     canActivate: [authGuard]
  },
   {
    path: 'communication',
    component: CommunicationComponent,
     canActivate: [authGuard]
  },
   {
    path: 'auditor',
    component: AuditorComponent,
    canActivate: [authGuard, roleGuard],
    data: { roles: ['Auditor'] }
  },
   {
    path: 'notifications',
    component: Notifications,
     canActivate: [authGuard]
  },
  {
    path: 'report',
    component: ReportComponent,
     canActivate: [authGuard]
  },
  {
    path: 'compliance',
    component: ComplianceComponent,
     canActivate: [authGuard]
  },
  {
    path: 'audit-logs',
    component: AuditLogsComponent,
     canActivate: [authGuard]
  },
  {
    path: 'analytics',
    component: AnalyticsComponent,
     canActivate: [authGuard]
  },
   {
    path: 'profile',
    component: ProfileComponent,
    canActivate: [authGuard]
  },
  {
    path: 'supply-chain-manager',
    component: SupplyChainManagerComponent,
    canActivate: [authGuard, roleGuard],
    data: { roles: ['Supply Chain Manager'] }
  },
  {
    path: 'vendor-performance',
    component: VendorPerformanceComponent,
     canActivate: [authGuard]
  },
  {
    path: 'vendor-reliability',
    component: VendorReliabilityComponent,
     canActivate: [authGuard]
  },
  {
    path: 'procurement-tracking',
    component: ProcurementTrackingComponent,
     canActivate: [authGuard]
  },
  {
    path: 'procurement-management',
    component: ProcurementManagementComponent,
    canActivate: [authGuard]
  },
   {
    path: 'procurement',
    component: ProcurementComponent,
     canActivate: [authGuard]
  },
   {
    path: 'vendor-management',
    component: VendorManagementComponent,
    canActivate: [authGuard]
  },
   {
    path: 'contract',
    component: ContractComponent,
     canActivate: [authGuard]
  },
  {
    path: 'purchase-orders',
    component: PurchaseOrdersComponent,
    canActivate: [authGuard]
  },
  {
    path: 'create-purchase-order',
    component: CreatePurchaseOrderComponent,
     canActivate: [authGuard]

  },
  {
    path: 'vendor-managements',
    component: VendorManagementsComponent,
     canActivate: [authGuard]
  },
  {
    path: 'vendor-list',
    component: VendorListComponent,
    canActivate: [authGuard]
  },
  {
    path: 'add-vendor',
    component: AddVendorComponent,
     canActivate: [authGuard]
  },
  {
    path: 'vendor-document',
    component: VendorDocumentComponent,
     canActivate: [authGuard]
  },
  {
    path: 'vendor-details/:id',
    component: VendorDetailsComponent,
     canActivate: [authGuard]
  },
   {
    path: 'edit-vendor/"id',
    component: EditVendorComponent,
     canActivate: [authGuard]
  },
  {
    path: 'vendor-approval',
    component: VendorApprovalComponent,
     canActivate: [authGuard]
  },
  {
    path: 'vendor-status',
    component: VendorStatusComponent,
     canActivate: [authGuard]
  },
  { 
    path: 'procurements',
    component: ProcurementsComponent,
     canActivate: [authGuard]
  },
  { 
    path: 'procurement-request',
    component: ProcurementRequestComponent,
    canActivate: [authGuard]
  },
  { 
    path: 'request-list',
    component: RequestListComponent,
     canActivate: [authGuard]
  },
  { 
    path: 'approval',
    component: ApprovalComponent,
     canActivate: [authGuard]
  },
  {
    path: 'vendor-assignment',
    component: VendorAssignmentComponent,
     canActivate: [authGuard]
  },
   {
    path: 'purchase-orders-creation',
    component: PurchaseOrdersCreationComponent,
     canActivate: [authGuard]
  },
   {
    path: 'purchase-orders-details',
    component: PurchaseOrdersDetailsComponent,
     canActivate: [authGuard]
  },
  {
    path: 'procurement-status-management',
    component: ProcurementStatusManagementComponent,
     canActivate: [authGuard]
  },
   {
    path: 'order-tracking',
    component: OrderTrackingComponent,
     canActivate: [authGuard]
  },
  {
    path: 'invoice-managements',
    component: InvoiceManagementsComponent,
     canActivate: [authGuard]
  },
   {
    path: 'delivery-performance-monitoring',
    component: DeliveryPerformanceMonitoringComponent,
     canActivate: [authGuard]
  },
   {
    path: 'product-quality-evaluation',
    component: ProductQualityEvaluationComponent,
     canActivate: [authGuard]
  },
   {
    path: 'communication-response-tracking',
    component: CommunicationResponseTrackingComponent,
     canActivate: [authGuard]
  },
   {
    path: 'service-rating',
    component: ServiceRatingComponent,
     canActivate: [authGuard]
  },
   {
    path: 'performance-history',
    component: PerformanceHistoryComponent,
     canActivate: [authGuard]
  },
  {
    path: 'vendor-ranking',
    component: VendorRankingComponent,
     canActivate: [authGuard]
  },
   {
    path: 'performance-metrics',
    component: PerformanceMetricsComponent,
     canActivate: [authGuard]
  },
  {
    path: '**',
    redirectTo: 'login'
  }

];