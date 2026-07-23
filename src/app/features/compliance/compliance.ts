import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';

interface ComplianceIssue {
  id: string;
  title: string;
  category: string;
  severity: string;
  status: string;
  date: string;
}

@Component({
  selector: 'app-compliance',
  standalone: true,
  imports: [CommonModule, RouterLink],
  templateUrl: './compliance.html',
  styleUrls: ['./compliance.css']
})
export class ComplianceComponent {

  complianceScore = 92;
  compliant = 18;
  minor = 6;
  major = 3;
  critical = 1;

  issues: ComplianceIssue[] = [
    {
      id:'COMP-2026-001',
      title:'Incomplete Vendor Documentation',
      category:'Vendor',
      severity:'Major',
      status:'Open',
      date:'20 Jul 2026'
    },
    {
      id:'COMP-2026-002',
      title:'Missing Contract Renewal Date',
      category:'Contracts',
      severity:'Minor',
      status:'Open',
      date:'24 Jul 2026'
    },
    {
      id:'COMP-2026-003',
      title:'Delayed Payment Approval',
      category:'Finance',
      severity:'Major',
      status:'In Progress',
      date:'23 Jul 2026'
    },
    {
      id:'COMP-2026-004',
      title:'User Access Without Approval',
      category:'Security',
      severity:'Critical',
      status:'Open',
      date:'20 Jul 2026'
    },
    {
      id:'COMP-2026-005',
      title:'Compliance Certificate Expired',
      category:'Vendor',
      severity:'Minor',
      status:'Resolved',
      date:'23 Jul 2026'
    }
  ];

  logout(){
    alert('Logged Out');
  }

}