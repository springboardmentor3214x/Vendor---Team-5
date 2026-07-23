import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';
import { VendorComponent } from '../features/vendor/vendor';

@Injectable({
  providedIn: 'root'
})
export class VendorService {
  private apiUrl = `${environment.apiUrl}/vendors/`;

  constructor(private http: HttpClient) {}

  getVendors(status?: string): Observable<VendorComponent[]> {
    let params = new HttpParams();

    if (status) {
      params = params.set('status', status);
    }

    return this.http.get<VendorComponent[]>(this.apiUrl, { params });
  }

  getVendor(id: number): Observable<VendorComponent> {
    return this.http.get<VendorComponent>(`${this.apiUrl}${id}`);
  }

  addVendor(vendor: VendorComponent): Observable<VendorComponent> {
    return this.http.post<VendorComponent>(this.apiUrl, vendor);
  }

  updateVendor(id: number, vendor: Partial<VendorComponent>): Observable<VendorComponent> {
    return this.http.patch<VendorComponent>(`${this.apiUrl}${id}`, vendor);
  }

  approveVendor(id: number): Observable<VendorComponent> {
    return this.http.patch<VendorComponent>(`${this.apiUrl}${id}/approve`, {});
  }

  rejectVendor(id: number): Observable<VendorComponent> {
    return this.http.patch<VendorComponent>(`${this.apiUrl}${id}/reject`, {});
  }
}