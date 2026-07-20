import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';

interface AuditLog {
  logId: string;
  user: string;
  action: string;
  module: string;
  address: string;
  dateTime: string;
}

@Component({
  selector: 'app-audit-logs',
  standalone: true,
  imports: [CommonModule, RouterLink],
  templateUrl: './audit-logs.html',
  styleUrls: ['./audit-logs.css']
})
export class AuditLogsComponent {

  logs: AuditLog[] = [
    {
      logId: 'LOG-2026-001',
      user: 'Admin User',
      action: 'User Login',
      module: 'Authentication',
      address: '192.168.1.10',
      dateTime: 'Jul 11, 2026 10:30 AM'
    },
    {
      logId: 'LOG-2026-002',
      user: 'Admin User',
      action: 'Downloaded Report',
      module: 'Reports',
      address: '192.168.1.10',
      dateTime: 'Jul 11, 2026 09:15 AM'
    },
    {
      logId: 'LOG-2026-003',
      user: 'Finance Officer',
      action: 'Updated Invoice',
      module: 'Invoice Management',
      address: '192.168.1.11',
      dateTime: 'Jul 10, 2026 10:30 AM'
    },
    {
      logId: 'LOG-2026-004',
      user: 'Procurement Manager',
      action: 'Created Document',
      module: 'Purchase Orders',
      address: '192.168.1.19',
      dateTime: 'Jul 10, 2026 11:00 AM'
    },
    {
      logId: 'LOG-2026-005',
      user: 'Vendor User',
      action: 'Uploaded Document',
      module: 'Vendor Profile',
      address: '192.168.1.17',
      dateTime: 'Jul 12, 2026 10:30 AM'
    }
  ];

  logout() {
    alert('Logged Out Successfully');
  }

}