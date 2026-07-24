import { HttpClient, HttpParams } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { Observable } from 'rxjs';
import { environment } from '../../../environments/environment';

export const VENDOR_CATEGORIES = [
  'Raw Material Suppliers',
  'Equipment Vendors',
  'IT Vendors',
  'Service Providers',
  'Logistics Partners',
  'Maintenance Vendors'
] as const;

export const VENDOR_STATUSES = ['Active', 'Pending', 'Inactive', 'Suspended', 'Rejected'] as const;
export const APPROVAL_STATUSES = ['Pending', 'Approved', 'Rejected'] as const;

export const VENDOR_APPROVER_ROLES = [
  'Administrator',
  'Procurement Manager',
  'Supply Chain Manager'
] as const;

export interface Vendor {
  id: number;
  company_name: string;
  category_id?: number | null;
  vendor_category?: string | null;
  contact_person_name: string;
  designation?: string | null;
  email: string;
  phone_number: string;
  alternate_phone?: string | null;
  gst_number?: string | null;
  pan_number?: string | null;
  company_registration_number?: string | null;
  address_line1?: string | null;
  address_line2?: string | null;
  city?: string | null;
  state?: string | null;
  country?: string | null;
  pincode?: string | null;
  website?: string | null;
  description?: string | null;
  bank_account_number?: string | null;
  ifsc_code?: string | null;
  payment_terms?: string | null;
  vendor_status: string;
  approval_status: string;
  reliability_score?: number | null;
  created_at?: string | null;
  updated_at?: string | null;
}

export interface VendorCreatePayload {
  company_name: string;
  category_id?: number | null;
  vendor_category?: string | null;
  contact_person_name: string;
  designation?: string | null;
  email: string;
  phone_number: string;
  alternate_phone?: string | null;
  gst_number?: string | null;
  pan_number?: string | null;
  company_registration_number?: string | null;
  address_line1?: string | null;
  address_line2?: string | null;
  city?: string | null;
  state?: string | null;
  country?: string | null;
  pincode?: string | null;
  website?: string | null;
  description?: string | null;
  bank_account_number?: string | null;
  ifsc_code?: string | null;
  payment_terms?: string | null;
  vendor_status?: string | null;
}

export type VendorUpdatePayload = Partial<VendorCreatePayload>;

export interface VendorListParams {
  search?: string;
  category?: string;
  status?: string;
  approval_status?: string;
}

export interface VendorApprovalPayload {
  remarks?: string | null;
}

@Injectable({ providedIn: 'root' })
export class VendorService {
  private readonly http = inject(HttpClient);
  private readonly baseUrl = `${environment.apiUrl}/vendors`;

  listVendors(params: VendorListParams = {}): Observable<Vendor[]> {
    let httpParams = new HttpParams();

    if (params.search?.trim()) {
      httpParams = httpParams.set('search', params.search.trim());
    }
    if (params.category?.trim()) {
      httpParams = httpParams.set('category', params.category.trim());
    }
    if (params.status?.trim()) {
      httpParams = httpParams.set('status', params.status.trim());
    }
    if (params.approval_status?.trim()) {
      httpParams = httpParams.set('approval_status', params.approval_status.trim());
    }

    return this.http.get<Vendor[]>(`${this.baseUrl}/`, { params: httpParams });
  }

  getVendor(id: number): Observable<Vendor> {
    return this.http.get<Vendor>(`${this.baseUrl}/${id}`);
  }

  createVendor(payload: VendorCreatePayload): Observable<Vendor> {
    return this.http.post<Vendor>(`${this.baseUrl}/`, payload);
  }

  updateVendor(id: number, payload: VendorUpdatePayload): Observable<Vendor> {
    return this.http.patch<Vendor>(`${this.baseUrl}/${id}`, payload);
  }

  approveVendor(id: number, payload: VendorApprovalPayload = {}): Observable<Vendor> {
    return this.http.patch<Vendor>(`${this.baseUrl}/${id}/approve`, payload);
  }

  rejectVendor(id: number, payload: VendorApprovalPayload = {}): Observable<Vendor> {
    return this.http.patch<Vendor>(`${this.baseUrl}/${id}/reject`, payload);
  }
}
