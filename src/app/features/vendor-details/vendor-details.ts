import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { RouterLink, ActivatedRoute } from '@angular/router';
import { VendorService } from '../../services/vendor.service';

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
export class VendorDetailsComponent implements OnInit {

  vendorId!: number;

  vendor: any = {};

  description = '';
  remarks = '';

  constructor(
    private vendorService: VendorService,
    private route: ActivatedRoute
  ) {}

  ngOnInit(): void {
    this.vendorId = Number(this.route.snapshot.paramMap.get('id'));
    this.loadVendor();
  }

  loadVendor(): void {
    this.vendorService.getVendor(this.vendorId).subscribe({
      next: (data) => {
        this.vendor = data;
      },
      error: (err) => {
        console.error('Failed to load vendor', err);
      }
    });
  }

  editVendor() {
    alert('Edit Vendor');
  }

  approveVendor() {
    this.vendorService.approveVendor(this.vendorId).subscribe({
      next: () => {
        alert('Vendor Approved Successfully');
        this.loadVendor();
      },
      error: (err) => {
        console.error(err);
        alert('Failed to approve vendor');
      }
    });
  }

  rejectVendor() {
    this.vendorService.rejectVendor(this.vendorId).subscribe({
      next: () => {
        alert('Vendor Rejected Successfully');
        this.loadVendor();
      },
      error: (err) => {
        console.error(err);
        alert('Failed to reject vendor');
      }
    });
  }

  back() {
    history.back();
  }

}