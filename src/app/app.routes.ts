import { Routes } from '@angular/router';

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
    component: DashboardComponent
  },

  {
    path: 'user-management',
    component: UserManagementComponent
  },

  {
    path: 'reports',
    component: ReportsComponent
  },

  {
    path: 'finance-officer',
    component: FinanceOfficerComponent
  },

  {
    path: 'purchase-order',
    component: PurchaseOrderComponent
  },

  {
    path: 'invoice-management',
    component: InvoiceManagementComponent
  },

  {
    path: 'payment-details',
    component: PaymentDetailsComponent
  },
   {
    path: 'vendor',
    component: VendorComponent
  },
   {
    path: 'vendor-profile',
    component: VendorProfileComponent
  },
  {
    path: 'orders',
    component: OrdersComponent
  },
  {
    path: 'contracts',
    component: ContractsComponent
  },
   {
    path: 'communication',
    component: CommunicationComponent
  },
   {
    path: 'auditor',
    component: AuditorComponent
  },
   {
    path: 'notifications',
    component: Notifications
  },
  {
    path: 'report',
    component: ReportComponent
  },
  {
    path: 'compliance',
    component: ComplianceComponent
  },
  {
    path: 'audit-logs',
    component: AuditLogsComponent
  },
  {
    path: 'analytics',
    component: AnalyticsComponent
  },
   {
    path: 'profile',
    component: ProfileComponent
  },
  {
    path: 'supply-chain-manager',
    component: SupplyChainManagerComponent
  },
  {
    path: 'vendor-performance',
    component: VendorPerformanceComponent
  },
  {
    path: 'vendor-reliability',
    component: VendorReliabilityComponent
  },
  {
    path: 'procurement-tracking',
    component: ProcurementTrackingComponent
  },
  {
    path: 'procurement-management',
    component: ProcurementManagementComponent
  },
   {
    path: 'procurement',
    component: ProcurementComponent
  },
   {
    path: 'vendor-management',
    component: VendorManagementComponent
  },
   {
    path: 'contract',
    component: ContractComponent
  },
  {
    path: 'purchase-orders',
    component: PurchaseOrdersComponent
  },
  {
    path: 'create-purchase-order',
    component: CreatePurchaseOrderComponent
  },
  {
    path: 'vendor-managements',
    component: VendorManagementsComponent
  },
  {
    path: 'vendor-list',
    component: VendorListComponent
  },
  {
    path: 'add-vendor',
    component: AddVendorComponent
  },
  {
    path: 'vendor-document',
    component: VendorDocumentComponent
  },
  {
    path: 'vendor-details',
    component: VendorDetailsComponent
  },
   {
    path: 'edit-vendor',
    component: EditVendorComponent
  },
  {
    path: 'vendor-approval',
    component: VendorApprovalComponent
  },
  {
    path: 'vendor-status',
    component: VendorStatusComponent
  },
  { 
    path: 'procurements',
    component: ProcurementsComponent
  },
  { 
    path: 'procurement-request',
    component: ProcurementRequestComponent
  },
  { 
    path: 'request-list',
    component: RequestListComponent
  },
  { 
    path: 'approval',
    component: ApprovalComponent
  },
  {
    path: 'vendor-assignment',
    component: VendorAssignmentComponent
  },
   {
    path: 'purchase-orders-creation',
    component: PurchaseOrdersCreationComponent
  },
   {
    path: 'purchase-orders-details',
    component: PurchaseOrdersDetailsComponent
  },
  {
    path: 'procurement-status-management',
    component: ProcurementStatusManagementComponent
  },
   {
    path: 'order-tracking',
    component: OrderTrackingComponent
  },
  {
    path: 'invoice-managements',
    component: InvoiceManagementsComponent
  },
   {
    path: 'delivery-performance-monitoring',
    component: DeliveryPerformanceMonitoringComponent
  },
   {
    path: 'product-quality-evaluation',
    component: ProductQualityEvaluationComponent
  },
   {
    path: 'communication-response-tracking',
    component: CommunicationResponseTrackingComponent
  },
   {
    path: 'service-rating',
    component: ServiceRatingComponent
  },
   {
    path: 'performance-history',
    component: PerformanceHistoryComponent
  },
  {
    path: 'vendor-ranking',
    component: VendorRankingComponent
  },
   {
    path: 'performance-metrics',
    component: PerformanceMetricsComponent
  },
  {
    path: '**',
    redirectTo: 'login'
  }

];