import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';
interface Vendor {
  vendorId: string;
  vendorName: string;
  companyName: string;
  category: string;
  email: string;
  status: string;
  approvedStatus: string;
}

@Component({
  selector: 'app-vendor-managements',
  standalone: true,
  imports: [CommonModule, RouterLink],
  templateUrl: './vendor-managements.html',
  styleUrls: ['./vendor-managements.css']
})
export class VendorManagementsComponent {

  searchText: string = '';

  vendors: Vendor[] = [

    {
      vendorId: 'VEN-0001',
      vendorName: 'Tech Solutions',
      companyName: 'Tech Solutions',
      category: 'IT',
      email: 'bharathi12@gmail.com',
      status: 'Active',
      approvedStatus: 'Approved'
    },

    {
      vendorId: 'VEN-0002',
      vendorName: 'Build Constructions',
      companyName: 'Build Pvt Ltd',
      category: 'Procurement',
      email: 'sonali65@gmail.com',
      status: 'Pending',
      approvedStatus: 'Pending'
    },

    {
      vendorId: 'VEN-0003',
      vendorName: 'Green Supplies',
      companyName: 'Green Supplies',
      category: 'Analytics',
      email: 'swathi123@gmail.com',
      status: 'Active',
      approvedStatus: 'Approved'
    },

    {
      vendorId: 'VEN-0004',
      vendorName: 'Security Systems',
      companyName: 'Security Systems',
      category: 'Finance',
      email: 'pranjelly20@gmail.com',
      status: 'Inactive',
      approvedStatus: 'Approved'
    },

    {
      vendorId: 'VEN-0005',
      vendorName: 'Future Tech',
      companyName: 'Future Tech',
      category: 'Procurement',
      email: 'priya120@gmail.com',
      status: 'Inactive',
      approvedStatus: 'Pending'
    }

  ];

  addVendor() {
    alert('Add Vendor Clicked');
  }

  filterVendor() {
    alert('Filter Clicked');
  }

  exportVendor() {
    alert('Export Clicked');
  }

  viewVendor(vendor: Vendor) {
    alert('Viewing : ' + vendor.vendorName);
  }

  editVendor(vendor: Vendor) {
    alert('Editing : ' + vendor.vendorName);
  }

  deleteVendor(vendor: Vendor) {

    if (confirm('Delete ' + vendor.vendorName + ' ?')) {

      this.vendors = this.vendors.filter(
        v => v.vendorId !== vendor.vendorId
      );

    }

  }

}