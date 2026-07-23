import { CommonModule } from '@angular/common';
import { Component } from '@angular/core';

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './dashboard.component.html',
  styleUrl: './dashboard.component.css'
})
export class DashboardComponent {
  readonly overviewCards = [
    { title: 'Active Vendors', value: '128', tone: 'success' },
    { title: 'Open Procurement', value: '29', tone: 'primary' },
    { title: 'Contracts Expiring Soon', value: '12', tone: 'warning' },
    { title: 'Vendor Reliability Score', value: '92%', tone: 'info' }
  ];

  readonly highlights = [
    'Supplier approval workflow is available through the vendor module.',
    'Performance, procurement, and delivery KPIs are surfaced in one dashboard.',
    'Contract expiry tracking and notification points can be extended on top of the API contract.'
  ];
}
