import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { RouterLink } from '@angular/router';

@Component({
  selector: 'app-order-tracking',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    RouterLink
  ],
  templateUrl: './order-tracking.html',
  styleUrls: ['./order-tracking.css']
})
export class OrderTrackingComponent {

  vendor = '';
  deliveryStatus = '';
  delayStatus = '';
  fromDate = '';
  toDate = '';

  vendors = [
    'ABC Enterprises',
    'Dell Technologies',
    'XYZ Solutions',
    'Tech Supplies Pvt Ltd',
    'Global Infotech',
    'Smart Office Supplies'
  ];

  deliveryStatuses = [
    'Awaiting Shipment',
    'In Transit',
    'Delivered',
    'Completed',
    'Delayed'
  ];

  delayStatuses = [
    'On Time',
    'At Risk',
    'Delayed'
  ];

  orders = [

    {
      poNumber: 'PO-2026-00125',
      vendor: 'ABC Enterprises',
      dispatchDate: '19 Jul 2026',
      expectedDate: '20 Jul 2026',
      actualDate: '20 Jul 2026',
      deliveryStatus: 'Delivered',
      delayStatus: 'On Time'
    },

    {
      poNumber: 'PO-2026-00124',
      vendor: 'Dell Technologies',
      dispatchDate: '18 Jul 2026',
      expectedDate: '25 Jul 2026',
      actualDate: '26 Jul 2026',
      deliveryStatus: 'Delivered',
      delayStatus: 'Delayed'
    },

    {
      poNumber: 'PO-2026-00123',
      vendor: 'XYZ Solutions',
      dispatchDate: '16 Jul 2026',
      expectedDate: '22 Jul 2026',
      actualDate: '-',
      deliveryStatus: 'In Transit',
      delayStatus: 'At Risk'
    },

    {
      poNumber: 'PO-2026-00122',
      vendor: 'Tech Supplies Pvt Ltd',
      dispatchDate: '17 Jul 2026',
      expectedDate: '24 Jul 2026',
      actualDate: '-',
      deliveryStatus: 'Awaiting Shipment',
      delayStatus: 'On Time'
    },

    {
      poNumber: 'PO-2026-00121',
      vendor: 'Global Infotech',
      dispatchDate: '15 Jul 2026',
      expectedDate: '21 Jul 2026',
      actualDate: '21 Jul 2026',
      deliveryStatus: 'Completed',
      delayStatus: 'On Time'
    },

    {
      poNumber: 'PO-2026-00120',
      vendor: 'Smart Office Supplies',
      dispatchDate: '18 Jul 2026',
      expectedDate: '27 Jul 2026',
      actualDate: '-',
      deliveryStatus: 'In Transit',
      delayStatus: 'At Risk'
    }

  ];

  search(): void {
    console.log('Search Clicked');
  }

  refresh(): void {
    console.log('Refresh Clicked');
  }

}