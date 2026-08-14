import { HttpClient, HttpParams } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { Observable, map } from 'rxjs';
import { environment } from '../../../environments/environment';

export const PROCUREMENT_PRIORITIES = ['Low', 'Medium', 'High', 'Critical'] as const;
export const PROCUREMENT_APPROVAL_STATUSES = ['Pending', 'Approved', 'Rejected', 'Sent Back', 'Cancelled'] as const;
export const PURCHASE_ORDER_STATUSES = ['Draft', 'Issued', 'In Progress', 'Delivered', 'Completed', 'Cancelled'] as const;
export const DELIVERY_STATUSES = ['Awaiting Shipment', 'In Transit', 'Delivered', 'Delayed', 'Completed'] as const;
export const PAYMENT_STATUSES = ['Pending', 'Verified', 'Approved', 'Paid', 'Rejected'] as const;

export interface ProcurementRequest {
  id: number;
  request_number: string;
  request_title: string;
  department_name: string;
  item_description: string | null;
  item_product_name: string | null;
  product_category: string | null;
  quantity_required: number | null;
  unit_of_measurement: string | null;
  estimated_budget: number | null;
  required_delivery_date: string | null;
  priority: string | null;
  business_justification: string | null;
  additional_remarks: string | null;
  requested_by: number | null;
  request_date: string | null;
  approval_status: string | null;
  approval_remarks: string | null;
  approved_by: number | null;
  approved_date: string | null;
  vendor_id: number | null;
  created_at: string | null;
  updated_at: string | null;
}

export interface PurchaseOrder {
  id: number;
  po_number: string;
  procurement_request_id: number | null;
  vendor_id: number | null;
  contract_id: number | null;
  quantity_ordered: number | null;
  unit_price: number | null;
  total_cost: number | null;
  tax_details: number | null;
  shipping_address: string | null;
  expected_delivery_date: string | null;
  actual_delivery_date: string | null;
  payment_terms: string | null;
  po_status: string | null;
  created_by: number | null;
  approved_by: number | null;
  po_date: string | null;
  created_at: string | null;
  updated_at: string | null;
}

export interface ProcurementRequestListParams {
  department?: string;
  status?: string;
  priority?: string;
  requested_by?: number;
}

export interface ProcurementRequestCreatePayload {
  requestTitle: string;
  departmentName: string;
  itemDescription: string;
  itemProductName: string;
  productCategory: string;
  quantityRequired: number;
  unitOfMeasurement?: string | null;
  estimatedBudget: number;
  requiredDeliveryDate: string;
  priority: string;
  businessJustification: string;
  additionalRemarks?: string | null;
  requestedBy?: number | null;
}

export interface ProcurementStatusHistoryEntry {
  id: number;
  procurement_request_id: number | null;
  old_status: string | null;
  new_status: string;
  changed_by: number | null;
  remarks: string | null;
  changed_at: string | null;
}

export interface ApprovedProcurementVendor {
  id: number;
  company_name: string;
  contact_person_name: string;
  reliability_score: number | null;
  vendor_status: string | null;
  approval_status: string | null;
}

export interface ProcurementApprovalPayload {
  approvedBy?: number | null;
  remarks?: string | null;
}

export interface PurchaseOrderListParams {
  vendor_id?: number;
  status?: string;
}

export interface PurchaseOrderCreatePayload {
  procurementRequestId: number;
  contractId?: number | null;
  quantityOrdered: number;
  unitPrice: number;
  taxDetails?: number | null;
  shippingAddress?: string | null;
  expectedDeliveryDate: string;
  paymentTerms?: string | null;
  createdBy?: number | null;
}

export interface OrderTracking {
  id: number;
  purchase_order_id: number;
  dispatch_date: string | null;
  expected_delivery_date: string | null;
  actual_delivery_date: string | null;
  delivery_status: string | null;
  delay_days: number;
  remarks: string | null;
}

export interface OrderTrackingUpdatePayload {
  dispatchDate?: string | null;
  actualDeliveryDate?: string | null;
  deliveryStatus?: string | null;
  remarks?: string | null;
}

export interface Invoice {
  id: number;
  invoice_number: string;
  purchase_order_id: number;
  invoice_amount: number;
  tax_amount: number;
  total_amount: number;
  supporting_document_url: string | null;
  invoice_date: string | null;
  due_date: string | null;
  paid_date: string | null;
  payment_status: string | null;
}

export interface InvoiceCreatePayload {
  purchaseOrderId: number;
  invoiceNumber: string;
  invoiceAmount: number;
  taxAmount?: number | null;
  supportingInvoiceDocument?: string | null;
  invoiceDate: string;
  dueDate?: string | null;
}

type ApiRecord = Record<string, unknown>;

@Injectable({ providedIn: 'root' })
export class ProcurementService {
  private readonly http = inject(HttpClient);
  private readonly baseUrl = `${environment.apiUrl}/procurement`;

  listRequests(params: ProcurementRequestListParams = {}): Observable<ProcurementRequest[]> {
    let httpParams = new HttpParams();
    if (params.department) httpParams = httpParams.set('department', params.department);
    if (params.status) httpParams = httpParams.set('approval_status', params.status);
    if (params.priority) httpParams = httpParams.set('priority', params.priority);
    if (params.requested_by !== undefined) httpParams = httpParams.set('requested_by', String(params.requested_by));

    return this.http
      .get<ApiRecord[]>(`${this.baseUrl}/procurement-requests`, { params: httpParams })
      .pipe(map((records) => records.map((record) => this.mapRequest(record))));
  }

  getRequest(requestId: number): Observable<ProcurementRequest> {
    return this.http
      .get<ApiRecord>(`${this.baseUrl}/procurement-requests/${requestId}`)
      .pipe(map((record) => this.mapRequest(record)));
  }

  createRequest(payload: ProcurementRequestCreatePayload): Observable<ProcurementRequest> {
    return this.http
      .post<ApiRecord>(`${this.baseUrl}/procurement-requests`, payload)
      .pipe(map((record) => this.mapRequest(record)));
  }

  getRequestStatusHistory(requestId: number): Observable<ProcurementStatusHistoryEntry[]> {
    return this.http
      .get<ApiRecord[]>(`${this.baseUrl}/procurement-requests/${requestId}/status-history`)
      .pipe(map((records) => records.map((record) => this.mapStatusHistory(record))));
  }

  approveRequest(requestId: number, payload: ProcurementApprovalPayload): Observable<ProcurementRequest> {
    return this.requestApprovalAction(requestId, 'approve', payload);
  }

  rejectRequest(requestId: number, payload: ProcurementApprovalPayload): Observable<ProcurementRequest> {
    return this.requestApprovalAction(requestId, 'reject', payload);
  }

  sendBackRequest(requestId: number, payload: ProcurementApprovalPayload): Observable<ProcurementRequest> {
    return this.requestApprovalAction(requestId, 'send-back', payload);
  }

  getApprovedVendors(requestId: number): Observable<ApprovedProcurementVendor[]> {
    return this.http
      .get<ApiRecord[]>(`${this.baseUrl}/procurement-requests/${requestId}/approved-vendors`)
      .pipe(map((records) => records.map((record) => this.mapApprovedVendor(record))));
  }

  assignVendor(requestId: number, vendorId: number): Observable<ProcurementRequest> {
    return this.http
      .patch<ApiRecord>(`${this.baseUrl}/procurement-requests/${requestId}/assign-vendor`, { vendorId })
      .pipe(map((record) => this.mapRequest(record)));
  }

  listPurchaseOrders(params: PurchaseOrderListParams = {}): Observable<PurchaseOrder[]> {
    let httpParams = new HttpParams();
    if (params.vendor_id !== undefined) httpParams = httpParams.set('vendor_id', String(params.vendor_id));
    if (params.status) httpParams = httpParams.set('po_status', params.status);

    return this.http
      .get<ApiRecord[]>(`${this.baseUrl}/purchase-orders`, { params: httpParams })
      .pipe(map((records) => records.map((record) => this.mapPurchaseOrder(record))));
  }

  getPurchaseOrder(poId: number): Observable<PurchaseOrder> {
    return this.http.get<ApiRecord>(`${this.baseUrl}/purchase-orders/${poId}`).pipe(map((record) => this.mapPurchaseOrder(record)));
  }

  createPurchaseOrder(payload: PurchaseOrderCreatePayload): Observable<PurchaseOrder> {
    return this.http.post<ApiRecord>(`${this.baseUrl}/purchase-orders`, payload).pipe(map((record) => this.mapPurchaseOrder(record)));
  }

  issuePurchaseOrder(poId: number): Observable<PurchaseOrder> {
    return this.updatePurchaseOrderAction(poId, 'issue');
  }

  deliverPurchaseOrder(poId: number): Observable<PurchaseOrder> {
    return this.updatePurchaseOrderAction(poId, 'deliver');
  }

  cancelPurchaseOrder(poId: number): Observable<PurchaseOrder> {
    return this.updatePurchaseOrderAction(poId, 'cancel');
  }

  downloadPurchaseOrderPdf(poId: number): Observable<Blob> {
    return this.http.get(`${this.baseUrl}/purchase-orders/${poId}/print`, { responseType: 'blob' });
  }

  getOrderTracking(poId: number): Observable<OrderTracking> {
    return this.http.get<ApiRecord>(`${this.baseUrl}/order-tracking/${poId}`).pipe(map((record) => this.mapOrderTracking(record)));
  }

  updateOrderTracking(poId: number, payload: OrderTrackingUpdatePayload): Observable<OrderTracking> {
    return this.http.patch<ApiRecord>(`${this.baseUrl}/order-tracking/${poId}`, payload).pipe(map((record) => this.mapOrderTracking(record)));
  }

  listInvoices(paymentStatus?: string): Observable<Invoice[]> {
    let params = new HttpParams();
    if (paymentStatus) params = params.set('payment_status', paymentStatus);
    return this.http.get<ApiRecord[]>(`${this.baseUrl}/invoices`, { params }).pipe(map((records) => records.map((record) => this.mapInvoice(record))));
  }

  getInvoice(invoiceId: number): Observable<Invoice> {
    return this.http.get<ApiRecord>(`${this.baseUrl}/invoices/${invoiceId}`).pipe(map((record) => this.mapInvoice(record)));
  }

  createInvoice(payload: InvoiceCreatePayload): Observable<Invoice> {
    return this.http.post<ApiRecord>(`${this.baseUrl}/invoices`, payload).pipe(map((record) => this.mapInvoice(record)));
  }

  verifyInvoice(invoiceId: number, remarks: string | null): Observable<Invoice> {
    return this.invoiceAction(invoiceId, 'verify', { remarks });
  }

  rejectInvoice(invoiceId: number, remarks: string | null): Observable<Invoice> {
    return this.invoiceAction(invoiceId, 'reject', { remarks });
  }

  updateInvoicePaymentStatus(invoiceId: number, paymentStatus: string): Observable<Invoice> {
    return this.http.patch<ApiRecord>(`${this.baseUrl}/invoices/${invoiceId}/payment-status`, { paymentStatus }).pipe(map((record) => this.mapInvoice(record)));
  }

  private mapRequest(record: ApiRecord): ProcurementRequest {
    return {
      id: this.numberValue(record, 'id') ?? 0,
      request_number: this.stringValue(record, 'requestNumber', 'request_number') ?? '—',
      request_title: this.stringValue(record, 'requestTitle', 'request_title') ?? 'Untitled request',
      department_name: this.stringValue(record, 'departmentName', 'department_name') ?? '—',
      item_description: this.stringValue(record, 'itemDescription', 'item_description'),
      item_product_name: this.stringValue(record, 'itemProductName', 'item_product_name'),
      product_category: this.stringValue(record, 'productCategory', 'product_category'),
      quantity_required: this.numberValue(record, 'quantityRequired', 'quantity_required'),
      unit_of_measurement: this.stringValue(record, 'unitOfMeasurement', 'unit_of_measurement'),
      estimated_budget: this.numberValue(record, 'estimatedBudget', 'estimated_budget'),
      required_delivery_date: this.stringValue(record, 'requiredDeliveryDate', 'required_delivery_date'),
      priority: this.stringValue(record, 'priority'),
      business_justification: this.stringValue(record, 'businessJustification', 'business_justification'),
      additional_remarks: this.stringValue(record, 'additionalRemarks', 'additional_remarks'),
      requested_by: this.numberValue(record, 'requestedBy', 'requested_by'),
      request_date: this.stringValue(record, 'requestDate', 'request_date'),
      approval_status: this.stringValue(record, 'approvalStatus', 'approval_status'),
      approval_remarks: this.stringValue(record, 'approvalRemarks', 'approval_remarks'),
      approved_by: this.numberValue(record, 'approvedBy', 'approved_by'),
      approved_date: this.stringValue(record, 'approvedDate', 'approved_date'),
      vendor_id: this.numberValue(record, 'vendorId', 'vendor_id'),
      created_at: this.stringValue(record, 'createdAt', 'created_at'),
      updated_at: this.stringValue(record, 'updatedAt', 'updated_at')
    };
  }

  private mapPurchaseOrder(record: ApiRecord): PurchaseOrder {
    return {
      id: this.numberValue(record, 'id') ?? 0,
      po_number: this.stringValue(record, 'poNumber', 'po_number') ?? '—',
      procurement_request_id: this.numberValue(record, 'procurementRequestId', 'procurement_request_id'),
      vendor_id: this.numberValue(record, 'vendorId', 'vendor_id'),
      contract_id: this.numberValue(record, 'contractId', 'contract_id'),
      quantity_ordered: this.numberValue(record, 'quantityOrdered', 'quantity_ordered'),
      unit_price: this.numberValue(record, 'unitPrice', 'unit_price'),
      total_cost: this.numberValue(record, 'totalCost', 'total_cost'),
      tax_details: this.numberValue(record, 'taxDetails', 'tax_details'),
      shipping_address: this.stringValue(record, 'shippingAddress', 'shipping_address'),
      expected_delivery_date: this.stringValue(record, 'expectedDeliveryDate', 'expected_delivery_date'),
      actual_delivery_date: this.stringValue(record, 'actualDeliveryDate', 'actual_delivery_date'),
      payment_terms: this.stringValue(record, 'paymentTerms', 'payment_terms'),
      po_status: this.stringValue(record, 'poStatus', 'po_status'),
      created_by: this.numberValue(record, 'createdBy', 'created_by'),
      approved_by: this.numberValue(record, 'approvedBy', 'approved_by'),
      po_date: this.stringValue(record, 'poDate', 'po_date'),
      created_at: this.stringValue(record, 'createdAt', 'created_at'),
      updated_at: this.stringValue(record, 'updatedAt', 'updated_at')
    };
  }

  private requestApprovalAction(requestId: number, action: 'approve' | 'reject' | 'send-back', payload: ProcurementApprovalPayload): Observable<ProcurementRequest> {
    return this.http
      .patch<ApiRecord>(`${this.baseUrl}/procurement-requests/${requestId}/${action}`, payload)
      .pipe(map((record) => this.mapRequest(record)));
  }

  private updatePurchaseOrderAction(poId: number, action: 'issue' | 'deliver' | 'cancel'): Observable<PurchaseOrder> {
    return this.http.patch<ApiRecord>(`${this.baseUrl}/purchase-orders/${poId}/${action}`, {}).pipe(map((record) => this.mapPurchaseOrder(record)));
  }

  private mapStatusHistory(record: ApiRecord): ProcurementStatusHistoryEntry {
    return {
      id: this.numberValue(record, 'id') ?? 0,
      procurement_request_id: this.numberValue(record, 'procurementRequestId', 'procurement_request_id'),
      old_status: this.stringValue(record, 'oldStatus', 'old_status'),
      new_status: this.stringValue(record, 'newStatus', 'new_status') ?? 'Not set',
      changed_by: this.numberValue(record, 'changedBy', 'changed_by'),
      remarks: this.stringValue(record, 'remarks'),
      changed_at: this.stringValue(record, 'changedAt', 'changed_at')
    };
  }

  private mapApprovedVendor(record: ApiRecord): ApprovedProcurementVendor {
    return {
      id: this.numberValue(record, 'id') ?? 0,
      company_name: this.stringValue(record, 'companyName', 'company_name') ?? 'Unnamed vendor',
      contact_person_name: this.stringValue(record, 'contactPerson', 'contact_person_name') ?? 'Not provided',
      reliability_score: this.numberValue(record, 'reliabilityScore', 'reliability_score'),
      vendor_status: this.stringValue(record, 'vendorStatus', 'vendor_status'),
      approval_status: this.stringValue(record, 'approvalStatus', 'approval_status')
    };
  }

  private mapOrderTracking(record: ApiRecord): OrderTracking {
    return {
      id: this.numberValue(record, 'id') ?? 0,
      purchase_order_id: this.numberValue(record, 'purchaseOrderId', 'purchase_order_id') ?? 0,
      dispatch_date: this.stringValue(record, 'dispatchDate', 'dispatch_date'),
      expected_delivery_date: this.stringValue(record, 'expectedDeliveryDate', 'expected_delivery_date'),
      actual_delivery_date: this.stringValue(record, 'actualDeliveryDate', 'actual_delivery_date'),
      delivery_status: this.stringValue(record, 'deliveryStatus', 'delivery_status'),
      delay_days: this.numberValue(record, 'delayDays', 'delay_days') ?? 0,
      remarks: this.stringValue(record, 'remarks')
    };
  }

  private invoiceAction(invoiceId: number, action: 'verify' | 'reject', payload: { remarks: string | null }): Observable<Invoice> {
    return this.http.patch<ApiRecord>(`${this.baseUrl}/invoices/${invoiceId}/${action}`, payload).pipe(map((record) => this.mapInvoice(record)));
  }

  private mapInvoice(record: ApiRecord): Invoice {
    return {
      id: this.numberValue(record, 'id') ?? 0,
      invoice_number: this.stringValue(record, 'invoiceNumber', 'invoice_number') ?? 'Unnamed invoice',
      purchase_order_id: this.numberValue(record, 'purchaseOrderId', 'purchase_order_id') ?? 0,
      invoice_amount: this.numberValue(record, 'invoiceAmount', 'invoice_amount') ?? 0,
      tax_amount: this.numberValue(record, 'taxAmount', 'tax_amount') ?? 0,
      total_amount: this.numberValue(record, 'totalAmount', 'total_amount') ?? 0,
      supporting_document_url: this.stringValue(record, 'supportingInvoiceDocument', 'supporting_document_url'),
      invoice_date: this.stringValue(record, 'invoiceDate', 'invoice_date'),
      due_date: this.stringValue(record, 'dueDate', 'due_date'),
      paid_date: this.stringValue(record, 'paidDate', 'paid_date'),
      payment_status: this.stringValue(record, 'paymentStatus', 'payment_status')
    };
  }

  private stringValue(record: ApiRecord, ...keys: string[]): string | null {
    const value = this.value(record, keys);
    return typeof value === 'string' ? value : null;
  }

  private numberValue(record: ApiRecord, ...keys: string[]): number | null {
    const value = this.value(record, keys);
    return typeof value === 'number' ? value : null;
  }

  private value(record: ApiRecord, keys: string[]): unknown {
    for (const key of keys) {
      if (record[key] !== undefined && record[key] !== null) return record[key];
    }
    return null;
  }
}
