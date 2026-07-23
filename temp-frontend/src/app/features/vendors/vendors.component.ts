import { CommonModule } from '@angular/common';
import { Component, OnInit, signal } from '@angular/core';
import { VendorRecord, VendorService } from '../../core/services/vendor.service';

@Component({
  selector: 'app-vendors',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './vendors.component.html',
  styleUrl: './vendors.component.css'
})
export class VendorsComponent implements OnInit {
  readonly vendors = signal<VendorRecord[]>([]);
  readonly loading = signal(false);

  constructor(private readonly vendorService: VendorService) {}

  ngOnInit(): void {
    this.loading.set(true);
    this.vendorService.listVendors().subscribe({
      next: (items) => this.vendors.set(items),
      complete: () => this.loading.set(false),
      error: () => this.loading.set(false)
    });
  }
}
