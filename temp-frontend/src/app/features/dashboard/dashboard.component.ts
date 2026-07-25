import { CommonModule } from '@angular/common';
import { Component, inject } from '@angular/core';
import { RouterLink } from '@angular/router';
import { AppRole, AuthService } from '../../core/services/auth.service';

interface DashboardView {
  title: string;
  description: string;
  cards: { title: string; description: string; actionLabel: string; path: string; tone: string }[];
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
export class DashboardComponent {
  private readonly authService = inject(AuthService);

  get view(): DashboardView {
    return this.views[this.authService.getUserRole() as AppRole] ?? this.views.Vendor;
  }

  private readonly views: Record<AppRole, DashboardView> = {
    Administrator: {
      title: 'Administrator dashboard',
      description: 'Access the vendor, procurement, and performance workspaces available to your role.',
      cards: [
        { title: 'Vendor management', description: 'Review registered vendors and their current approval status.', actionLabel: 'Open vendors', path: '/vendors', tone: 'success' },
        { title: 'Procurement workflow', description: 'Manage requests, purchase orders, tracking, and invoices.', actionLabel: 'Open procurement', path: '/procurement', tone: 'primary' },
        { title: 'Performance monitoring', description: 'Review vendor performance records and rankings.', actionLabel: 'Open performance', path: '/performance', tone: 'info' }
      ],
      highlights: [
        'Review vendor records; approval actions require the backend approval endpoint to be available.',
        'Use your profile page to keep account information and credentials current.',
        'Additional operational modules remain accessible as their frontend integration is completed.'
      ],
      primaryAction: { label: 'Manage vendors', path: '/vendors' }
    },
    'Procurement Manager': {
      title: 'Procurement dashboard',
      description: 'Manage vendor records and progress pending supplier decisions.',
      cards: [
        { title: 'Vendor workspace', description: 'Review vendor records and statuses.', actionLabel: 'Open vendors', path: '/vendors', tone: 'success' },
        { title: 'Procurement workflow', description: 'Manage requests and purchase orders.', actionLabel: 'Open procurement', path: '/procurement', tone: 'primary' },
        { title: 'Performance monitoring', description: 'Review and record supplier performance.', actionLabel: 'Open performance', path: '/performance', tone: 'info' }
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
        { title: 'Vendor workspace', description: 'Review vendor records and statuses.', actionLabel: 'Open vendors', path: '/vendors', tone: 'success' },
        { title: 'Procurement monitoring', description: 'Monitor purchase orders and delivery tracking.', actionLabel: 'Open procurement', path: '/procurement', tone: 'primary' },
        { title: 'Performance monitoring', description: 'Review vendor performance and rankings.', actionLabel: 'Open performance', path: '/performance', tone: 'info' }
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
        { title: 'Account profile', description: 'Review your registered account details.', actionLabel: 'Open profile', path: '/profile', tone: 'success' },
        { title: 'Password controls', description: 'Update your password from your profile.', actionLabel: 'Manage profile', path: '/profile', tone: 'primary' }
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
        { title: 'Invoice workspace', description: 'Review invoices and backend-supported payment statuses.', actionLabel: 'Open invoices', path: '/procurement/invoices', tone: 'success' },
        { title: 'Account profile', description: 'Review your registered account details.', actionLabel: 'Open profile', path: '/profile', tone: 'primary' }
      ],
      highlights: [
        'Maintain your account and contact details from the profile page.',
        'Use invoice actions only where the backend endpoint supports your workflow.',
        'Your current access remains limited to the permissions assigned to your role.'
      ],
      primaryAction: { label: 'Open profile', path: '/profile' }
    },
    Auditor: {
      title: 'Auditor dashboard',
      description: 'Your role-based workspace is ready for audit integrations.',
      cards: [
        { title: 'Performance monitoring', description: 'Review backend-returned performance records and rankings.', actionLabel: 'Open performance', path: '/performance', tone: 'success' },
        { title: 'Account profile', description: 'Review your registered account details.', actionLabel: 'Open profile', path: '/profile', tone: 'primary' }
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
