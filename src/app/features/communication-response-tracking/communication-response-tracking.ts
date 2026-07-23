import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { RouterLink, RouterLinkActive } from '@angular/router';

@Component({
  selector: 'app-communication-response-tracking',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    RouterLink,
    RouterLinkActive
  ],
  templateUrl: './communication-response-tracking.html',
  styleUrls: ['./communication-response-tracking.css']
})
export class CommunicationResponseTrackingComponent {

  searchText: string = '';

  selectedVendor: string = 'All Vendors';
  selectedStatus: string = 'All Status';
  dateRange: string = '';

  vendors = [
    'All Vendors',
    'Vendor A Pvt Ltd',
    'Vendor B Solutions',
    'Vendor C Supplies',
    'Vendor D Industries',
    'Vendor E Enterprises'
  ];

  statuses = [
    'All Status',
    'Responded',
    'Pending',
    'No Response'
  ];

  communications = [
    {
      po: 'PO-2026-00125',
      vendor: 'Vendor A Pvt Ltd',
      sentTime: '20 Jul 2026 10:30 AM',
      responseTime: '27 Jul 2026 11:15 AM',
      duration: '45 mins',
      status: 'Responded',
      remarks: 'Quotation Confirmation'
    },
    {
      po: 'PO-2026-00124',
      vendor: 'Vendor B Solutions',
      sentTime: '27 Jul 2026 11:15 AM',
      responseTime: '27 Jul 2026 03:10 PM',
      duration: '50 mins',
      status: 'Responded',
      remarks: 'Delivery Schedule Update'
    },
    {
      po: 'PO-2026-00123',
      vendor: 'Vendor C Supplies',
      sentTime: '26 Jul 2026 04:45 PM',
      responseTime: '26 Jul 2026 09:15 PM',
      duration: '4 hrs 30 mins',
      status: 'Responded',
      remarks: 'Material Availability'
    },
    {
      po: 'PO-2026-00122',
      vendor: 'Vendor D Industries',
      sentTime: '29 Jul 2026 10:10 AM',
      responseTime: '-',
      duration: '-',
      status: 'Pending',
      remarks: 'Waiting for Response'
    },
    {
      po: 'PO-2026-00121',
      vendor: 'Vendor E Enterprises',
      sentTime: '27 Jul 2026 03:30 PM',
      responseTime: '27 Jul 2026 10:35 AM',
      duration: '25 mins',
      status: 'Responded',
      remarks: 'Invoice Clarification'
    },
    {
      po: 'PO-2026-00120',
      vendor: 'Vendor F Solutions',
      sentTime: '29 Jul 2026 11:20 AM',
      responseTime: '29 Jul 2026 01:05 PM',
      duration: '2 hrs 45 mins',
      status: 'Responded',
      remarks: 'Transport Details'
    }
  ];

  get filteredCommunications() {
    return this.communications.filter(item => {

      const vendorMatch =
        this.selectedVendor === 'All Vendors' ||
        item.vendor === this.selectedVendor;

      const statusMatch =
        this.selectedStatus === 'All Status' ||
        item.status === this.selectedStatus;

      const searchMatch =
        this.searchText === '' ||
        item.vendor.toLowerCase().includes(this.searchText.toLowerCase()) ||
        item.po.toLowerCase().includes(this.searchText.toLowerCase());

      return vendorMatch && statusMatch && searchMatch;
    });
  }

}