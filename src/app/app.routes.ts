import { Routes } from '@angular/router';
import { LoginComponent } from './features/auth/login/login';
import { RegisterComponent } from './features/auth/register/register';
import { ForgotPasswordComponent } from './features/auth/forgot-password/forgot-password';
import { ResetPasswordComponent } from './features/auth/reset-password/reset-password';
import { DashboardComponent } from './features/dashboard/dashboard';
import { UserManagementComponent } from './features/user-management/user-management';
import { ProcurementComponent } from './features/procurement/procurement';
import { MainLayoutComponent } from './core/layout/main-layout.component';
import { PurchaseOrderComponent } from './features/purchase-order/purchase-order';

export const routes: Routes = [
  { path: '', redirectTo: 'login', pathMatch: 'full' },
  { path: 'login', component: LoginComponent },
  { path: 'register', component: RegisterComponent},
  { path: 'forgot-password', component: ForgotPasswordComponent },
  { path: 'reset-password', component: ResetPasswordComponent },

  {
    path: '',
    component: MainLayoutComponent,
    children: [
      { path: 'dashboard', component: DashboardComponent },
      { path: 'user-management', component: UserManagementComponent },
      { path: 'procurement', component: ProcurementComponent },
      { path: 'purchase-order', component: PurchaseOrderComponent}
    ]
  },

  { path: '**', redirectTo: 'login' }
];