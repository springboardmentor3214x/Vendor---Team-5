import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { RouterLink } from '@angular/router';
import { VendorService } from '../../services/vendor.service';

@Component({
  selector: 'app-vendor-status',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterLink],
  templateUrl: './vendor-status.html',
  styleUrls: ['./vendor-status.css']
})
export class VendorStatusComponent implements OnInit {

  search = '';
  selectedStatus = 'All Status';

  vendors: any[] = [];

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

  filterByStatus(): void {

    if (this.selectedStatus === 'All Status') {
      this.loadVendors();
      return;
    }

    this.vendorService.getVendors(this.selectedStatus.toLowerCase()).subscribe({
      next: (data: any) => {
        this.vendors = data;
      },
      error: (err) => {
        console.error('Error filtering vendors', err);
      }
    });

  }

}