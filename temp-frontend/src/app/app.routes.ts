import { Routes } from '@angular/router';
import { authGuard } from './core/guards/auth.guard';
import { roleGuard } from './core/guards/role.guard';
import { DashboardComponent } from './features/dashboard/dashboard.component';
import { ForgotPasswordComponent } from './features/forgot-password/forgot-password.component';
import { LoginComponent } from './features/login/login.component';
import { ProfileComponent } from './features/profile/profile.component';
import { ProcurementComponent } from './features/procurement/procurement.component';
import { RequestApprovalComponent } from './features/procurement/request-approval.component';
import { RequestDetailComponent } from './features/procurement/request-detail.component';
import { RequestFormComponent } from './features/procurement/request-form.component';
import { RequestListComponent } from './features/procurement/request-list.component';
import { PurchaseOrderDetailComponent } from './features/procurement/purchase-order-detail.component';
import { PurchaseOrderFormComponent } from './features/procurement/purchase-order-form.component';
import { PurchaseOrderListComponent } from './features/procurement/purchase-order-list.component';
import { OrderTrackingComponent } from './features/procurement/order-tracking.component';
import { PerformanceDashboardComponent } from './features/performance/performance-dashboard.component';
import { VendorPerformanceDetailComponent } from './features/performance/vendor-performance-detail.component';
import { PerformanceEntryFormComponent } from './features/performance/performance-entry-form.component';
import { VendorAssignmentComponent } from './features/procurement/vendor-assignment.component';
import { RegisterComponent } from './features/register/register.component';
import { ResetPasswordComponent } from './features/reset-password/reset-password.component';
import { VendorDetailComponent } from './features/vendors/vendor-detail.component';
import { VendorFormComponent } from './features/vendors/vendor-form.component';
import { VendorsComponent } from './features/vendors/vendors.component';
import { ReliabilityComponent } from './features/reliability/reliability.component';
import { ReportsComponent } from './features/reports/reports.component';
import { AppShellComponent } from './layout/app-shell.component';
import { ContractRepositoryComponent } from './features/contracts/contract-repository/contract-repository.component';
import { ContractFormComponent } from './features/contracts/contract-form/contract-form.component';
import { ContractDetailsComponent } from './features/contracts/contract-details/contract-details.component';
import { ContractRenewalDashboardComponent } from './features/contracts/contract-renewal-dashboard/contract-renewal-dashboard.component';
import { CertificationManagementComponent } from './features/contracts/certification-management/certification-management.component';
import { VendorDocumentationComponent } from './features/contracts/vendor-documentation/vendor-documentation.component';
import { ComplianceDashboardComponent } from './features/contracts/compliance-dashboard/compliance-dashboard.component';
import { ContractNotificationsComponent } from './features/contracts/contract-notifications/contract-notifications.component';

export const routes: Routes = [
  { path: 'login', component: LoginComponent },
  { path: 'register', component: RegisterComponent },
  { path: 'forgot-password', component: ForgotPasswordComponent },
  { path: 'reset-password', component: ResetPasswordComponent },
  {
    path: '',
    component: AppShellComponent,
    canActivate: [authGuard],
    children: [
      { path: '', redirectTo: 'dashboard', pathMatch: 'full' },
      {
        path: 'dashboard',
        component: DashboardComponent,
        canActivate: [roleGuard],
        data: {
          roles: [
            'Administrator',
            'Procurement Manager',
            'Supply Chain Manager',
            'Vendor',
            'Finance Officer',
            'Auditor'
          ]
        }
      },
      {
        path: 'profile',
        component: ProfileComponent,
        canActivate: [roleGuard],
        data: {
          roles: [
            'Administrator',
            'Procurement Manager',
            'Supply Chain Manager',
            'Vendor',
            'Finance Officer',
            'Auditor'
          ]
        }
      },
      {
        path: 'vendors',
        component: VendorsComponent,
        canActivate: [roleGuard],
        data: {
          roles: ['Administrator', 'Procurement Manager', 'Supply Chain Manager']
        }
      },
      {
        path: 'vendors/new',
        component: VendorFormComponent,
        canActivate: [roleGuard],
        data: {
          roles: ['Administrator', 'Procurement Manager']
        }
      },
      {
        path: 'vendors/:id/edit',
        component: VendorFormComponent,
        canActivate: [roleGuard],
        data: {
          roles: ['Administrator', 'Procurement Manager']
        }
      },
      {
        path: 'vendors/:id',
        component: VendorDetailComponent,
        canActivate: [roleGuard],
        data: {
          roles: ['Administrator', 'Procurement Manager', 'Supply Chain Manager', 'Vendor']
        }
      },
      {
        path: 'performance/vendors/:id/record/:type',
        component: PerformanceEntryFormComponent,
        canActivate: [roleGuard],
        data: { roles: ['Administrator', 'Procurement Manager'] }
      },
      {
        path: 'performance/vendors/:id',
        component: VendorPerformanceDetailComponent,
        canActivate: [roleGuard],
        data: { roles: ['Administrator', 'Procurement Manager', 'Supply Chain Manager', 'Auditor'] }
      },
      {
        path: 'performance',
        component: PerformanceDashboardComponent,
        canActivate: [roleGuard],
        data: { roles: ['Administrator', 'Procurement Manager', 'Supply Chain Manager', 'Auditor'] }
      },
      {
        path: 'reliability',
        component: ReliabilityComponent,
        canActivate: [roleGuard],
        data: { roles: ['Administrator', 'Procurement Manager', 'Supply Chain Manager', 'Auditor'] }
      },
      {
        path: 'reports',
        component: ReportsComponent,
        canActivate: [roleGuard],
        data: { roles: ['Administrator', 'Procurement Manager', 'Supply Chain Manager', 'Finance Officer', 'Auditor'] }
      },
      {
        path: 'procurement/invoices/new',
        loadComponent: () => import('./features/procurement/invoice-form.component').then((module) => module.InvoiceFormComponent),
        canActivate: [roleGuard],
        data: { roles: ['Administrator', 'Procurement Manager', 'Finance Officer'] }
      },
      {
        path: 'procurement/invoices/:id',
        loadComponent: () => import('./features/procurement/invoice-detail.component').then((module) => module.InvoiceDetailComponent),
        canActivate: [roleGuard],
        data: { roles: ['Administrator', 'Procurement Manager', 'Finance Officer'] }
      },
      {
        path: 'procurement/invoices',
        loadComponent: () => import('./features/procurement/invoice-list.component').then((module) => module.InvoiceListComponent),
        canActivate: [roleGuard],
        data: { roles: ['Administrator', 'Procurement Manager', 'Finance Officer'] }
      },
      {
        path: 'procurement/purchase-orders/new',
        component: PurchaseOrderFormComponent,
        canActivate: [roleGuard],
        data: { roles: ['Administrator', 'Procurement Manager'] }
      },
      {
        path: 'procurement/purchase-orders/:id/tracking',
        component: OrderTrackingComponent,
        canActivate: [roleGuard],
        data: { roles: ['Administrator', 'Procurement Manager', 'Supply Chain Manager'] }
      },
      {
        path: 'procurement/purchase-orders/:id',
        component: PurchaseOrderDetailComponent,
        canActivate: [roleGuard],
        data: { roles: ['Administrator', 'Procurement Manager', 'Supply Chain Manager'] }
      },
      {
        path: 'procurement/purchase-orders',
        component: PurchaseOrderListComponent,
        canActivate: [roleGuard],
        data: { roles: ['Administrator', 'Procurement Manager', 'Supply Chain Manager'] }
      },
      {
        path: 'procurement/requests/new',
        component: RequestFormComponent,
        canActivate: [roleGuard],
        data: { roles: ['Administrator', 'Procurement Manager', 'Supply Chain Manager'] }
      },
      {
        path: 'procurement/requests/:id/approval',
        component: RequestApprovalComponent,
        canActivate: [roleGuard],
        data: { roles: ['Administrator', 'Procurement Manager'] }
      },
      {
        path: 'procurement/requests/:id/vendor-assignment',
        component: VendorAssignmentComponent,
        canActivate: [roleGuard],
        data: { roles: ['Administrator', 'Procurement Manager'] }
      },
      {
        path: 'procurement/requests/:id',
        component: RequestDetailComponent,
        canActivate: [roleGuard],
        data: { roles: ['Administrator', 'Procurement Manager', 'Supply Chain Manager'] }
      },
      {
        path: 'procurement/requests',
        component: RequestListComponent,
        canActivate: [roleGuard],
        data: { roles: ['Administrator', 'Procurement Manager', 'Supply Chain Manager'] }
      },
      {
        path: 'procurement',
        component: ProcurementComponent,
        canActivate: [roleGuard],
        data: {
          roles: ['Administrator', 'Procurement Manager', 'Supply Chain Manager']
        }
      },
      { path: 'contracts/new', component: ContractFormComponent, canActivate: [roleGuard], data: { roles: ['Administrator', 'Procurement Manager'] } },
      { path: 'contracts/renewals', component: ContractRenewalDashboardComponent, canActivate: [roleGuard], data: { roles: ['Administrator', 'Procurement Manager', 'Auditor', 'Finance Officer'] } },
      { path: 'contracts/certifications', component: CertificationManagementComponent, canActivate: [roleGuard], data: { roles: ['Administrator', 'Procurement Manager', 'Auditor'] } },
      { path: 'contracts/documents', component: VendorDocumentationComponent, canActivate: [roleGuard], data: { roles: ['Administrator', 'Procurement Manager', 'Auditor'] } },
      { path: 'contracts/compliance', component: ComplianceDashboardComponent, canActivate: [roleGuard], data: { roles: ['Administrator', 'Procurement Manager', 'Auditor'] } },
      { path: 'contracts/notifications', component: ContractNotificationsComponent, canActivate: [roleGuard], data: { roles: ['Administrator', 'Procurement Manager', 'Auditor', 'Finance Officer'] } },
      { path: 'contracts/:id/edit', component: ContractFormComponent, canActivate: [roleGuard], data: { roles: ['Administrator', 'Procurement Manager'] } },
      { path: 'contracts/:id', component: ContractDetailsComponent, canActivate: [roleGuard], data: { roles: ['Administrator', 'Procurement Manager', 'Auditor', 'Finance Officer'] } },
      { path: 'contracts', component: ContractRepositoryComponent, canActivate: [roleGuard], data: { roles: ['Administrator', 'Procurement Manager', 'Auditor', 'Finance Officer'] } },
      {
        path: 'analytics',
        redirectTo: 'dashboard'
      }
    ]
  },
  { path: '**', redirectTo: 'login' }
];
