import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { RouterLink } from '@angular/router';

@Component({
  selector: 'app-invoice-managements',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterLink],
  templateUrl: './invoice-managements.html',
  styleUrls: ['./invoice-managements.css']
})
export class InvoiceManagementsComponent {

  invoice = {
    invoiceNumber: 'INV-2026',
    poNumber: 'PO-2026',
    vendorName: 'ABC Pvt Ltd',
    invoiceDate: '2026-07-18',
    invoiceAmount: 45000,
    taxAmount: 5000,
    totalAmount: 50000,
    dueDate: '2026-08-15',
    paymentStatus: 'Pending',
    document: 'ABC_DOCUMENT.pdf'
  };

  invoiceList = [
    {
      invoiceNumber: 'INV-2001',
      poNumber: 'PO-1001',
      vendor: 'ABC Pvt Ltd',
      invoiceDate: '18/07/2026',
      invoiceAmount: '45,000',
      taxAmount: '5,000',
      totalAmount: '50,000',
      dueDate: '14/08/2026',
      paymentStatus: 'Pending'
    },
    {
      invoiceNumber: 'INV-2002',
      poNumber: 'PO-1002',
      vendor: 'XYZ Ltd',
      invoiceDate: '17/07/2026',
      invoiceAmount: '25,000',
      taxAmount: '2,000',
      totalAmount: '27,000',
      dueDate: '15/08/2026',
      paymentStatus: 'Verified'
    },
    {
      invoiceNumber: 'INV-2003',
      poNumber: 'PO-1003',
      vendor: 'LMN Corp',
      invoiceDate: '16/07/2026',
      invoiceAmount: '30,000',
      taxAmount: '3,000',
      totalAmount: '33,000',
      dueDate: '16/08/2026',
      paymentStatus: 'Approved'
    },
    {
      invoiceNumber: 'INV-2004',
      poNumber: 'PO-1004',
      vendor: 'Tech Solutions',
      invoiceDate: '15/07/2026',
      invoiceAmount: '18,000',
      taxAmount: '1,800',
      totalAmount: '19,800',
      dueDate: '17/08/2026',
      paymentStatus: 'Pending'
    }
  ];

  uploadInvoice() {
    alert('Invoice Uploaded Successfully');
  }

  verifyInvoice() {
    this.invoice.paymentStatus = 'Verified';
    alert('Invoice Verified');
  }

  approvePayment() {
    this.invoice.paymentStatus = 'Approved';
    alert('Payment Approved');
  }

  rejectInvoice() {
    alert('Invoice Rejected');
  }

  viewInvoice(item: any) {
    alert('Viewing ' + item.invoiceNumber);
  }

}