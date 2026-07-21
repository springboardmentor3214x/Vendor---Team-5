import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';
import { VendorComponent } from '../features/vendor/vendor';

@Injectable({
  providedIn: 'root'
})
export class VendorService {

  private apiUrl = `${environment.apiUrl}/vendors`;

  constructor(private http: HttpClient) {}

  // Get all vendors
  getVendors(status?: string): Observable<VendorComponent[]> {
    if (status) {
      return this.http.get<VendorComponent[]>(
        `${this.apiUrl}?status=${status}`
      );
    }

    return this.http.get<VendorComponent[]>(this.apiUrl);
  }

  // Get vendor by ID
  getVendor(id: number): Observable<VendorComponent> {
    return this.http.get<VendorComponent>(
      `${this.apiUrl}/${id}`
    );
  }

  // Create vendor
  addVendor(vendor: VendorComponent): Observable<VendorComponent> {
    return this.http.post<VendorComponent>(
      this.apiUrl,
      vendor
    );
  }

  // Update vendor
  updateVendor(id: number, vendor: Partial<VendorComponent>): Observable<VendorComponent> {
    return this.http.patch<VendorComponent>(
      `${this.apiUrl}/${id}`,
      vendor
    );
  }

  // Approve vendor
  approveVendor(id: number): Observable<VendorComponent> {
    return this.http.patch<VendorComponent>(
      `${this.apiUrl}/${id}/approve`,
      {}
    );
  }

  // Reject vendor
  rejectVendor(id: number): Observable<VendorComponent> {
    return this.http.patch<VendorComponent>(
      `${this.apiUrl}/${id}/reject`,
      {}
    );
  }

}