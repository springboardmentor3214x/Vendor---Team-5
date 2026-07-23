import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { RouterLink } from '@angular/router';
import { VendorService } from '../../services/vendor.service';

@Component({
  selector: 'app-vendor-approval',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterLink],
  templateUrl: './vendor-approval.html',
  styleUrls: ['./vendor-approval.css']
})
export class VendorApprovalComponent {

  vendorId = 1; // Replace with actual vendor ID later

  vendor = {
    name: 'Bharathi',
    email: 'bharathi12@gmail.com',
    phone: '9876543210',
    submittedOn: '12-04-2025',
    status: 'Pending',
    approvalStatus: 'Pending'
  };

  description = '';
  remarks = '';

  constructor(private vendorService: VendorService) {}

  approveVendor() {

    if (!this.description || !this.remarks) {
      alert('Please fill Description and Remarks');
      return;
    }

    this.vendorService.approveVendor(this.vendorId).subscribe({
      next: () => {
        this.vendor.status = 'Approved';
        this.vendor.approvalStatus = 'Approved';
        alert('Vendor Approved Successfully');
      },
      error: (err) => {
        console.error(err);
        alert('Failed to approve vendor');
      }
    });

  }

  rejectVendor() {

    if (!this.description || !this.remarks) {
      alert('Please fill Description and Remarks');
      return;
    }

    this.vendorService.rejectVendor(this.vendorId).subscribe({
      next: () => {
        this.vendor.status = 'Rejected';
        this.vendor.approvalStatus = 'Rejected';
        alert('Vendor Rejected Successfully');
      },
      error: (err) => {
        console.error(err);
        alert('Failed to reject vendor');
      }
    });

  }

  back() {
    window.history.back();
  }

}