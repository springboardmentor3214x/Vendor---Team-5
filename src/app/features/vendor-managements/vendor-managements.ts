import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';
import { VendorService } from '../../services/vendor.service';

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
export class VendorManagementsComponent implements OnInit {

  searchText: string = '';
  vendors: Vendor[] = [];

  constructor(private vendorService: VendorService) {}

  ngOnInit(): void {
    this.loadVendors();
  }

  loadVendors(): void {
    this.vendorService.getVendors().subscribe({
      next: (data: any) => {
        this.vendors = data;
      },
      error: (err) => {
        console.error('Error loading vendors', err);
      }
    });
  }

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