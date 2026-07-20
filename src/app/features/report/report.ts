import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';

interface Report {
  name: string;
  category: string;
  date: string;
  amount: string;
  status: 'Completed' | 'In Progress';
}

@Component({
  selector: 'app-report',
  standalone: true,
  imports: [CommonModule, RouterLink],
  templateUrl: './report.html',
  styleUrls: ['./report.css']
})
export class ReportComponent {

  totalReports = 24;
  completedReports = 18;
  progressReports = 4;
  overdueReports = 2;

  reports: Report[] = [
    {
      name: 'Vendor Performance Audit Report',
      category: 'Vendor',
      date: '20 Jul 2026',
      amount: '5,20,000',
      status: 'Completed'
    },
    {
      name: 'Procurement Compliance Report',
      category: 'Procurement',
      date: '24 Jul 2026',
      amount: '3,75,000',
      status: 'Completed'
    },
    {
      name: 'Financial Transactions Audit',
      category: 'Finance',
      date: '23 Jul 2026',
      amount: '8,90,000',
      status: 'In Progress'
    },
    {
      name: 'User Access Review Report',
      category: 'Security',
      date: '20 Jul 2026',
      amount: '2,15,000',
      status: 'Completed'
    },
    {
      name: 'Contract Compliance Report',
      category: 'Contracts',
      date: '23 Jul 2026',
      amount: '6,40,000',
      status: 'Completed'
    }
  ];

  logout(): void {
    alert('Logged out successfully');
    // If using Angular Router:
    // this.router.navigate(['/login']);
  }
}