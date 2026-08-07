import { CommonModule } from '@angular/common';
import { Component, OnInit, inject, signal } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { RouterLink } from '@angular/router';
import { AppRole, AuthService } from '../../core/services/auth.service';
import { environment } from '../../../environments/environment';

interface DashboardView {
  title: string;
  description: string;
  cards: { title: string; description: string; actionLabel: string; path: string; tone: string; icon: string; badge: string }[];
  highlights: string[];
  primaryAction: {
    label: string;
    path: string;
  };
}

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [CommonModule, RouterLink],
  templateUrl: './dashboard.component.html',
  styleUrl: './dashboard.component.css'
})
export class DashboardComponent implements OnInit {
  private readonly authService = inject(AuthService);
  private readonly http = inject(HttpClient);

  get view(): DashboardView {
    return this.views[this.authService.getUserRole() as AppRole] ?? this.views.Vendor;
  }

  readonly kpis = signal([
    { label: 'Active vendors', value: 0, icon: '👥', tone: 'success' },
    { label: 'Open procurement', value: 0, icon: '📋', tone: 'primary' },
    { label: 'Invoices to review', value: 0, icon: '🧾', tone: 'warning' },
    { label: 'Active contracts', value: 0, icon: '📄', tone: 'info' }
  ]);

  ngOnInit(): void {
    if (this.authService.getUserRole() !== 'Administrator') return;

    this.http.get<{ approvedVendors: number; totalProcurementRequests: number }>(`${environment.apiUrl}/dashboard/admin`)
      .subscribe({
        next: (summary) => {
          this.kpis.update((kpis) => kpis.map((kpi, index) => {
            if (index === 0) return { ...kpi, value: summary.approvedVendors };
            if (index === 1) return { ...kpi, value: summary.totalProcurementRequests };
            return kpi;
          }));
        }
      });
    this.http.get<{ status: string }[]>(`${environment.apiUrl}/contracts/`)
      .subscribe({ next: (contracts) => this.kpis.update((kpis) => kpis.map((kpi, index) =>
        index === 3 ? { ...kpi, value: contracts.filter((contract) => contract.status === 'Active').length } : kpi
      )) });
  }

  private readonly views: Record<AppRole, DashboardView> = {
    Administrator: {
      title: 'Administrator dashboard',
      description: 'Access the vendor, procurement, and performance workspaces available to your role.',
      cards: [
        { title: 'Vendor management', description: 'Review registered vendors and their current approval status.', actionLabel: 'Open vendors', path: '/vendors', tone: 'success', icon: '👥', badge: 'Directory' },
        { title: 'Procurement workflow', description: 'Manage requests, purchase orders, tracking, and invoices.', actionLabel: 'Open procurement', path: '/procurement', tone: 'primary', icon: '📋', badge: 'Operations' },
        { title: 'Performance monitoring', description: 'Review vendor performance records and rankings.', actionLabel: 'Open performance', path: '/performance', tone: 'info', icon: '📈', badge: 'Insights' }
      ],
      highlights: [
        'Review and action vendor records from the vendor workspace.',
        'Use your profile page to keep account information and credentials current.',
        'Additional operational modules remain accessible as their frontend integration is completed.'
      ],
      primaryAction: { label: 'Manage vendors', path: '/vendors' }
    },
    'Procurement Manager': {
      title: 'Procurement dashboard',
      description: 'Manage vendor records and progress pending supplier decisions.',
      cards: [
        { title: 'Vendor workspace', description: 'Review vendor records and statuses.', actionLabel: 'Open vendors', path: '/vendors', tone: 'success', icon: '👥', badge: 'Directory' },
        { title: 'Procurement workflow', description: 'Manage requests and purchase orders.', actionLabel: 'Open procurement', path: '/procurement', tone: 'primary', icon: '📋', badge: 'Operations' },
        { title: 'Performance monitoring', description: 'Review and record supplier performance.', actionLabel: 'Open performance', path: '/performance', tone: 'info', icon: '📈', badge: 'Insights' }
      ],
      highlights: [
        'Search vendor records by company, contact, and current status.',
        'Approve or reject pending vendors directly from their detail pages.',
        'Maintain your account details from the profile page.'
      ],
      primaryAction: { label: 'Open vendors', path: '/vendors' }
    },
    'Supply Chain Manager': {
      title: 'Supply chain dashboard',
      description: 'Monitor vendor status and participate in the approval workflow.',
      cards: [
        { title: 'Vendor workspace', description: 'Review vendor records and statuses.', actionLabel: 'Open vendors', path: '/vendors', tone: 'success', icon: '👥', badge: 'Directory' },
        { title: 'Procurement monitoring', description: 'Monitor purchase orders and delivery tracking.', actionLabel: 'Open procurement', path: '/procurement', tone: 'primary', icon: '🚚', badge: 'Operations' },
        { title: 'Performance monitoring', description: 'Review vendor performance and rankings.', actionLabel: 'Open performance', path: '/performance', tone: 'info', icon: '📈', badge: 'Insights' }
      ],
      highlights: [
        'Use filters to focus on vendors by status and approval state.',
        'Review vendor profiles before taking an approval decision.',
        'Maintain your account details from the profile page.'
      ],
      primaryAction: { label: 'Review vendors', path: '/vendors' }
    },
    Vendor: {
      title: 'Vendor dashboard',
      description: 'Your role-based workspace for account and vendor-related activity.',
      cards: [
        { title: 'Account profile', description: 'Review your registered account details.', actionLabel: 'Open profile', path: '/profile', tone: 'success', icon: '👤', badge: 'Account' },
        { title: 'Password controls', description: 'Update your password from your profile.', actionLabel: 'Manage profile', path: '/profile', tone: 'primary', icon: '🔐', badge: 'Security' }
      ],
      highlights: [
        'Keep your company and contact information up to date in your profile.',
        'Use the password controls in your profile to maintain account security.',
        'Vendor record access is limited to the permissions assigned to your role.'
      ],
      primaryAction: { label: 'Open profile', path: '/profile' }
    },
    'Finance Officer': {
      title: 'Finance dashboard',
      description: 'Your role-based workspace is ready for finance integrations.',
      cards: [
        { title: 'Invoice workspace', description: 'Review invoices and payment statuses.', actionLabel: 'Open invoices', path: '/procurement/invoices', tone: 'success', icon: '🧾', badge: 'Finance' },
        { title: 'Account profile', description: 'Review your registered account details.', actionLabel: 'Open profile', path: '/profile', tone: 'primary', icon: '👤', badge: 'Account' }
      ],
      highlights: [
        'Maintain your account and contact details from the profile page.',
        'Use the invoice workspace to review current payment activity.',
        'Your current access remains limited to the permissions assigned to your role.'
      ],
      primaryAction: { label: 'Open profile', path: '/profile' }
    },
    Auditor: {
      title: 'Auditor dashboard',
      description: 'Your role-based workspace is ready for audit integrations.',
      cards: [
        { title: 'Performance monitoring', description: 'Review performance records and rankings.', actionLabel: 'Open performance', path: '/performance', tone: 'success', icon: '📈', badge: 'Insights' },
        { title: 'Account profile', description: 'Review your registered account details.', actionLabel: 'Open profile', path: '/profile', tone: 'primary', icon: '👤', badge: 'Account' }
      ],
      highlights: [
        'Maintain your account and contact details from the profile page.',
        'Performance records remain read-only for your role in the frontend workflow.',
        'Your current access remains limited to the permissions assigned to your role.'
      ],
      primaryAction: { label: 'Open profile', path: '/profile' }
    }
  };
}
