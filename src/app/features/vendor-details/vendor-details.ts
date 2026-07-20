import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { RouterLink } from '@angular/router';

@Component({
  selector: 'app-vendor-details',
  standalone: true,
  imports: [
    CommonModule,
    RouterLink,
    FormsModule
  ],
  templateUrl: './vendor-details.html',
  styleUrls: ['./vendor-details.css']
})
export class VendorDetailsComponent {

  vendor = {
    vendorName: 'Tech Solution PVT LTD',
    email: 'bharathi12@gmail.com',
    phone: '9876543210',
    address: 'Hyderabad, Telangana, India',
    gst: '74658CT9324103',
    contact: '9087655351',
    company: 'IT Services',
    registrationDate: 'Active',
    status: 'Approved',
    approvalStatus: 'Approved'
  };

  description: string = '';
  remarks: string = '';

  editVendor() {
    alert('Edit Vendor');
  }

  approveVendor() {
    alert('Vendor Approved Successfully');
  }

  rejectVendor() {
    alert('Vendor Rejected Successfully');
  }

  back() {
    history.back();
  }

}