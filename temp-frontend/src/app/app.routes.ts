import { Routes } from '@angular/router';
import { authGuard } from './core/guards/auth.guard';
import { roleGuard } from './core/guards/role.guard';
import { DashboardComponent } from './features/dashboard/dashboard.component';
import { ForgotPasswordComponent } from './features/forgot-password/forgot-password.component';
import { LoginComponent } from './features/login/login.component';
import { ProfileComponent } from './features/profile/profile.component';
import { RegisterComponent } from './features/register/register.component';
import { ResetPasswordComponent } from './features/reset-password/reset-password.component';
import { VendorDetailComponent } from './features/vendors/vendor-detail.component';
import { VendorFormComponent } from './features/vendors/vendor-form.component';
import { VendorsComponent } from './features/vendors/vendors.component';
import { AppShellComponent } from './layout/app-shell.component';

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
        path: 'procurement',
        redirectTo: 'dashboard'
      },
      {
        path: 'contracts',
        redirectTo: 'dashboard'
      },
      {
        path: 'analytics',
        redirectTo: 'dashboard'
      }
    ]
  },
  { path: '**', redirectTo: 'login' }
];