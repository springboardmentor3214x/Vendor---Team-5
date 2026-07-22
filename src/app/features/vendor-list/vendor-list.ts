import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { RouterLink } from '@angular/router';
import { VendorService } from '../../services/vendor.service';

@Component({
  selector: 'app-vendor-list',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterLink],
  templateUrl: './vendor-list.html',
  styleUrls: ['./vendor-list.css']
})
export class VendorListComponent {

  searchText: string = '';

  vendors: any[] = [];

  constructor(private vendorService: VendorService) {
    this.loadVendors();
  }

  loadVendors(): void {
    this.vendorService.getVendors().subscribe({
      next: (data) => {
        this.vendors = data;
      },
      error: (err) => {
        console.error('Failed to load vendors', err);
      }
    });
  }

  addVendor() {
    alert('Add Vendor Clicked');
  }

  viewVendor(vendor: any) {
    console.log('View Vendor', vendor);
  }

  editVendor(vendor: any) {
    console.log('Edit Vendor', vendor);
  }

  deleteVendor(vendor: any) {
    const confirmDelete = confirm(
      `Are you sure you want to delete ${vendor.name}?`
    );

    if (confirmDelete) {
      this.vendors = this.vendors.filter(v => v !== vendor);
    }
  }
}