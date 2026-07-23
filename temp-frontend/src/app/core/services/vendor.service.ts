import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { environment } from '../../../environments/environment';

export interface VendorRecord {
  id: number;
  vendor_name: string;
  status: string;
  rating?: number;
}

@Injectable({ providedIn: 'root' })
export class VendorService {
  private readonly baseUrl = `${environment.apiUrl}/vendors`;

  constructor(private readonly http: HttpClient) {}

  listVendors() {
    return this.http.get<VendorRecord[]>(this.baseUrl);
  }

  getVendor(id: number) {
    return this.http.get<VendorRecord>(`${this.baseUrl}/${id}`);
  }

  createVendor(payload: Partial<VendorRecord>) {
    return this.http.post<VendorRecord>(this.baseUrl, payload);
  }

  updateVendor(id: number, payload: Partial<VendorRecord>) {
    return this.http.put<VendorRecord>(`${this.baseUrl}/${id}`, payload);
  }

  approveVendor(id: number) {
    return this.http.post<VendorRecord>(`${this.baseUrl}/${id}/approve`, {});
  }

  rejectVendor(id: number) {
    return this.http.post<VendorRecord>(`${this.baseUrl}/${id}/reject`, {});
  }
}
