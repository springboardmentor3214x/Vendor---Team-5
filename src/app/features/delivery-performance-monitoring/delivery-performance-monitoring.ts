import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { RouterLink, RouterLinkActive } from '@angular/router';

@Component({
  selector: 'app-delivery-performance',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    RouterLink,
    RouterLinkActive
  ],
  templateUrl: './delivery-performance-monitoring.html',
  styleUrls: ['./delivery-performance-monitoring.css']
})
export class DeliveryPerformanceMonitoringComponent {

  searchText: string = '';

  deliveries = [

    {
      po: 'PO-2026-00125',
      vendor: 'Vendor A Pvt Ltd',
      expected: '20 Jul 2026',
      actual: '18 Jul 2026',
      delay: '-2',
      status: 'Early Delivered',
      class: 'early',
      remarks: 'Delivered 2 days early'
    },

    {
      po: 'PO-2026-00124',
      vendor: 'Vendor B Solutions',
      expected: '27 Jul 2026',
      actual: '27 Jul 2026',
      delay: '0',
      status: 'On-Time',
      class: 'ontime',
      remarks: 'Delivered on time'
    },

    {
      po: 'PO-2026-00123',
      vendor: 'Vendor C Supplies',
      expected: '26 Jul 2026',
      actual: '28 Jul 2026',
      delay: '2',
      status: 'Delayed',
      class: 'delayed',
      remarks: 'Delivered due to transport issue'
    },

    {
      po: 'PO-2026-00122',
      vendor: 'Vendor D Industries',
      expected: '29 Jul 2026',
      actual: '29 Jul 2026',
      delay: '0',
      status: 'On-Time',
      class: 'ontime',
      remarks: 'Delivered on time'
    },

    {
      po: 'PO-2026-00121',
      vendor: 'Vendor E Enterprises',
      expected: '27 Jul 2026',
      actual: '30 Jul 2026',
      delay: '3',
      status: 'Delayed',
      class: 'delayed',
      remarks: 'Weather conditions'
    },

    {
      po: 'PO-2026-00120',
      vendor: 'Vendor F Solutions',
      expected: '29 Jul 2026',
      actual: '27 Jul 2026',
      delay: '-2',
      status: 'Early Delivered',
      class: 'early',
      remarks: 'Delivered ahead of schedule'
    }

  ];

}