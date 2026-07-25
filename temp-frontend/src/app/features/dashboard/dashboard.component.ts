import { CommonModule } from '@angular/common';
import { Component, inject } from '@angular/core';
import { RouterLink } from '@angular/router';
import { AppRole, AuthService } from '../../core/services/auth.service';

interface DashboardView {
  title: string;
  description: string;
  cards: { title: string; value: string; tone: string }[];
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
      description: 'Oversee vendor operations and access the current management workspace.',
      cards: [
        { title: 'Vendor management', value: 'Available', tone: 'success' },
        { title: 'Approval workflow', value: 'Available', tone: 'primary' },
        { title: 'Profile controls', value: 'Ready', tone: 'info' }
      ],
      highlights: [
        'Review vendor details and pending approval decisions from the vendor workspace.',
        'Use your profile page to keep account information and credentials current.',
        'Additional operational modules remain accessible as their frontend integration is completed.'
      ],
      primaryAction: { label: 'Manage vendors', path: '/vendors' }
    },
    'Procurement Manager': {
      title: 'Procurement dashboard',
      description: 'Manage vendor records and progress pending supplier decisions.',
      cards: [
        { title: 'Vendor workspace', value: 'Available', tone: 'success' },
        { title: 'Approval actions', value: 'Available', tone: 'primary' },
        { title: 'Profile controls', value: 'Ready', tone: 'info' }
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
        { title: 'Vendor workspace', value: 'Available', tone: 'success' },
        { title: 'Status monitoring', value: 'Available', tone: 'primary' },
        { title: 'Profile controls', value: 'Ready', tone: 'info' }
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
        { title: 'Account profile', value: 'Available', tone: 'success' },
        { title: 'Role access', value: 'Vendor', tone: 'primary' },
        { title: 'Password controls', value: 'Ready', tone: 'info' }
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
        { title: 'Account profile', value: 'Available', tone: 'success' },
        { title: 'Role access', value: 'Finance', tone: 'primary' },
        { title: 'Password controls', value: 'Ready', tone: 'info' }
      ],
      highlights: [
        'Maintain your account and contact details from the profile page.',
        'Finance-specific workflow pages can be added when their API integration is available.',
        'Your current access remains limited to the permissions assigned to your role.'
      ],
      primaryAction: { label: 'Open profile', path: '/profile' }
    },
    Auditor: {
      title: 'Auditor dashboard',
      description: 'Your role-based workspace is ready for audit integrations.',
      cards: [
        { title: 'Account profile', value: 'Available', tone: 'success' },
        { title: 'Role access', value: 'Auditor', tone: 'primary' },
        { title: 'Password controls', value: 'Ready', tone: 'info' }
      ],
      highlights: [
        'Maintain your account and contact details from the profile page.',
        'Audit-specific workflow pages can be added when their API integration is available.',
        'Your current access remains limited to the permissions assigned to your role.'
      ],
      primaryAction: { label: 'Open profile', path: '/profile' }
    }
  };
}
