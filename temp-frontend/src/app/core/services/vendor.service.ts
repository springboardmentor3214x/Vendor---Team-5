import { HttpClient, HttpParams } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { Observable, map } from 'rxjs';
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
  'Procurement Manager'
] as const;

export const VENDOR_DOCUMENT_TYPES = [
  { label: 'GST Certificate', value: 'GST Certificate' },
  { label: 'PAN Card', value: 'PAN Card' },
  { label: 'Company Registration Certificate', value: 'Company Registration Certificate' },
  { label: 'ISO Certificate', value: 'ISO Certificate' },
  { label: 'Other Supporting Documents', value: 'Other Supporting Document' }
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

export interface VendorDocumentUploadResponse {
  vendorId?: number;
  vendor_id?: number;
  documentType?: string;
  document_type?: string;
  fileName?: string;
  file_name?: string;
  message: string;
}

export interface VendorDocument {
  id: number;
  vendorId?: number;
  vendor_id?: number;
  documentType?: string;
  document_type?: string;
  fileName?: string;
  file_name?: string;
  downloadUrl?: string;
  download_url?: string;
}

export interface VendorDeleteResponse {
  message: string;
}

export interface VendorCategory {
  id: number;
  name: string;
  description?: string | null;
  isActive?: boolean | null;
}

interface VendorApiResponse {
  id: number;
  companyName?: string;
  company_name?: string;
  categoryId?: number | null;
  category_id?: number | null;
  vendorCategory?: string | null;
  vendor_category?: string | null;
  contactPerson?: string;
  contact_person_name?: string;
  designation?: string | null;
  email: string;
  phone?: string;
  phone_number?: string;
  alternatePhone?: string | null;
  alternate_phone?: string | null;
  gstNumber?: string | null;
  gst_number?: string | null;
  panNumber?: string | null;
  pan_number?: string | null;
  registrationNumber?: string | null;
  company_registration_number?: string | null;
  address1?: string | null;
  address_line1?: string | null;
  address2?: string | null;
  address_line2?: string | null;
  city?: string | null;
  state?: string | null;
  country?: string | null;
  pincode?: string | null;
  website?: string | null;
  description?: string | null;
  bankAccountNumber?: string | null;
  bank_account_number?: string | null;
  ifscCode?: string | null;
  ifsc_code?: string | null;
  paymentTerms?: string | null;
  payment_terms?: string | null;
  vendorStatus?: string;
  vendor_status?: string;
  approvalStatus?: string;
  approval_status?: string;
  reliabilityScore?: number | null;
  reliability_score?: number | null;
  createdAt?: string | null;
  created_at?: string | null;
  updatedAt?: string | null;
  updated_at?: string | null;
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

    return this.http
      .get<VendorApiResponse[]>(`${this.baseUrl}/`, { params: httpParams })
      .pipe(map((vendors) => vendors.map((vendor) => this.mapVendor(vendor))));
  }

  listCategories(): Observable<VendorCategory[]> {
    return this.http.get<VendorCategory[]>(`${this.baseUrl}/categories`);
  }

  getVendor(id: number): Observable<Vendor> {
    return this.http
      .get<VendorApiResponse>(`${this.baseUrl}/${id}`)
      .pipe(map((vendor) => this.mapVendor(vendor)));
  }

  createVendor(payload: VendorCreatePayload): Observable<Vendor> {
    return this.http
      .post<VendorApiResponse>(`${this.baseUrl}/`, payload)
      .pipe(map((vendor) => this.mapVendor(vendor)));
  }

  updateVendor(id: number, payload: VendorUpdatePayload): Observable<Vendor> {
    return this.http
      .put<VendorApiResponse>(`${this.baseUrl}/${id}`, payload)
      .pipe(map((vendor) => this.mapVendor(vendor)));
  }

  deleteVendor(id: number): Observable<VendorDeleteResponse> {
    return this.http.delete<VendorDeleteResponse>(`${this.baseUrl}/${id}`);
  }

  approveVendor(id: number, payload: VendorApprovalPayload = {}): Observable<Vendor> {
    return this.http
      .patch<VendorApiResponse>(`${this.baseUrl}/${id}/approve`, payload)
      .pipe(map((vendor) => this.mapVendor(vendor)));
  }

  rejectVendor(id: number, payload: VendorApprovalPayload = {}): Observable<Vendor> {
    return this.http
      .patch<VendorApiResponse>(`${this.baseUrl}/${id}/reject`, payload)
      .pipe(map((vendor) => this.mapVendor(vendor)));
  }

  uploadDocument(
    vendorId: number,
    documentType: string,
    file: File
  ): Observable<VendorDocumentUploadResponse> {
    const formData = new FormData();
    formData.append('document_type', documentType);
    formData.append('file', file, file.name);

    return this.http.post<VendorDocumentUploadResponse>(
      `${this.baseUrl}/${vendorId}/documents`,
      formData
    );
  }

  listDocuments(vendorId: number): Observable<VendorDocument[]> {
    return this.http.get<VendorDocument[]>(`${this.baseUrl}/${vendorId}/documents`);
  }

  private mapVendor(vendor: VendorApiResponse): Vendor {
    return {
      id: vendor.id,
      company_name: vendor.companyName ?? vendor.company_name ?? '',
      category_id: vendor.categoryId ?? vendor.category_id,
      vendor_category: vendor.vendorCategory ?? vendor.vendor_category,
      contact_person_name: vendor.contactPerson ?? vendor.contact_person_name ?? '',
      designation: vendor.designation,
      email: vendor.email,
      phone_number: vendor.phone ?? vendor.phone_number ?? '',
      alternate_phone: vendor.alternatePhone ?? vendor.alternate_phone,
      gst_number: vendor.gstNumber ?? vendor.gst_number,
      pan_number: vendor.panNumber ?? vendor.pan_number,
      company_registration_number:
        vendor.registrationNumber ?? vendor.company_registration_number,
      address_line1: vendor.address1 ?? vendor.address_line1,
      address_line2: vendor.address2 ?? vendor.address_line2,
      city: vendor.city,
      state: vendor.state,
      country: vendor.country,
      pincode: vendor.pincode,
      website: vendor.website,
      description: vendor.description,
      bank_account_number: vendor.bankAccountNumber ?? vendor.bank_account_number,
      ifsc_code: vendor.ifscCode ?? vendor.ifsc_code,
      payment_terms: vendor.paymentTerms ?? vendor.payment_terms,
      vendor_status: vendor.vendorStatus ?? vendor.vendor_status ?? '',
      approval_status: vendor.approvalStatus ?? vendor.approval_status ?? '',
      reliability_score: vendor.reliabilityScore ?? vendor.reliability_score,
      created_at: vendor.createdAt ?? vendor.created_at,
      updated_at: vendor.updatedAt ?? vendor.updated_at
    };
  }
}
