import { Routes } from '@angular/router';
import { authGuard } from './core/guards/auth.guard';
import { AnalyticsComponent } from './features/analytics/analytics.component';
import { ContractsComponent } from './features/contracts/contracts.component';
import { DashboardComponent } from './features/dashboard/dashboard.component';
import { LoginComponent } from './features/login/login.component';
import { ProcurementComponent } from './features/procurement/procurement.component';
import { ProfileComponent } from './features/profile/profile.component';
import { RegisterComponent } from './features/register/register.component';
import { VendorsComponent } from './features/vendors/vendors.component';
import { AppShellComponent } from './layout/app-shell.component';

export const routes: Routes = [
  { path: 'login', component: LoginComponent },
  { path: 'register', component: RegisterComponent },
  {
    path: '',
    component: AppShellComponent,
    canActivate: [authGuard],
    children: [
      { path: '', redirectTo: 'dashboard', pathMatch: 'full' },
      { path: 'dashboard', component: DashboardComponent },
      { path: 'profile', component: ProfileComponent },
      { path: 'vendors', component: VendorsComponent },
      { path: 'procurement', component: ProcurementComponent },
      { path: 'contracts', component: ContractsComponent },
      { path: 'analytics', component: AnalyticsComponent }
    ]
  },
  { path: '**', redirectTo: 'login' }
];