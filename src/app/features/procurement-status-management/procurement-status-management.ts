import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { RouterLink } from '@angular/router';

@Component({
  selector: 'app-procurement-status-management',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    RouterLink
  ],
  templateUrl: './procurement-status-management.html',
  styleUrls: ['./procurement-status-management.css']
})
export class ProcurementStatusManagementComponent {

  statuses = [
    { name: 'Pending', count: 18, color: '#f39c12' },
    { name: 'Approved', count: 60, color: '#27ae60' },
    { name: 'Ordered', count: 42, color: '#3f51b5' },
    { name: 'Delivered', count: 30, color: '#00bcd4' },
    { name: 'Completed', count: 28, color: '#9c27b0' },
    { name: 'Cancelled', count: 5, color: '#e53935' }
  ];

  requests = [

    {
      number:'PR-2026-00125',
      title:'Office Furniture Purchase',
      department:'HR Department',
      vendor:'ABC Enterprises',
      priority:'High',
      status:'Pending',
      updated:'19 Jul 2026,10:30 AM',
      by:'John Mathew'
    },

    {
      number:'PR-2026-00124',
      title:'Laptop Purchase',
      department:'IT Department',
      vendor:'Dell Technologies',
      priority:'High',
      status:'Approved',
      updated:'18 Jul 2026,09:16 AM',
      by:'Priya Menon'
    },

    {
      number:'PR-2026-00123',
      title:'Printer Accessories',
      department:'Admin Department',
      vendor:'XYZ Solutions',
      priority:'Medium',
      status:'Ordered',
      updated:'20 Jul 2026',
      by:'Priya Menon'
    },

    {
      number:'PR-2026-00122',
      title:'AC Maintenance',
      department:'Facilities',
      vendor:'Tech Services Ltd',
      priority:'Low',
      status:'Delivered',
      updated:'17 Jul 2026',
      by:'Rohit Kumar'
    },

    {
      number:'PR-2026-00121',
      title:'Server Hardware Upgrade',
      department:'IT Department',
      vendor:'ABC Enterprises',
      priority:'High',
      status:'Completed',
      updated:'18 Jul 2026',
      by:'Priya Menon'
    },

    {
      number:'PR-2026-00120',
      title:'Stationery Supplies',
      department:'Admin Department',
      vendor:'Global Infotech',
      priority:'Low',
      status:'Cancelled',
      updated:'18 Jul 2026',
      by:'Priya Menon'
    }

  ];

}