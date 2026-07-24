import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router, RouterLink, ActivatedRoute } from '@angular/router';
import { VendorService } from '../../services/vendor.service';

@Component({
  selector: 'app-edit-vendor',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterLink],
  templateUrl: './edit-vendor.html',
  styleUrls: ['./edit-vendor.css']
})
export class EditVendorComponent implements OnInit {

  vendorId!: number;

  vendor: any = {};

  constructor(
    private router: Router,
    private route: ActivatedRoute,
    private vendorService: VendorService
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

  saveVendor(): void {
    this.updateVendor();
  }

  updateVendor(): void {
    this.vendorService.updateVendor(this.vendorId, this.vendor).subscribe({
      next: () => {
        alert('Vendor updated successfully.');
        this.router.navigate(['/vendor-details', this.vendorId]);
      },
      error: (err) => {
        console.error(err);
        alert('Failed to update vendor.');
      }
    });
  }

  resetForm(): void {
    this.loadVendor();
  }

  back(): void {
    this.router.navigate(['/vendor-details', this.vendorId]);
  }

}