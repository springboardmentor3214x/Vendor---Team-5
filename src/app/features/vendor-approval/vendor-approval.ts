import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { RouterLink } from '@angular/router';
@Component({
  selector: 'app-vendor-approval',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterLink],
  templateUrl: './vendor-approval.html',
  styleUrls: ['./vendor-approval.css']
})
export class VendorApprovalComponent {

  vendor = {
    name: 'Bharathi',
    email: 'bharathi12@gmail.com',
    phone: '9876543210',
    submittedOn: '12-04-2025',
    status: 'Pending',
    approvalStatus: 'Pending'
  };

  description: string = '';
  remarks: string = '';

  approveVendor() {

    if (!this.description || !this.remarks) {
      alert('Please fill Description and Remarks');
      return;
    }

    this.vendor.status = 'Approved';
    this.vendor.approvalStatus = 'Approved';

    alert('Vendor Approved Successfully');
  }

  rejectVendor() {

    if (!this.description || !this.remarks) {
      alert('Please fill Description and Remarks');
      return;
    }

    this.vendor.status = 'Rejected';
    this.vendor.approvalStatus = 'Rejected';

    alert('Vendor Rejected Successfully');
  }

  back() {
    window.history.back();
  }


}