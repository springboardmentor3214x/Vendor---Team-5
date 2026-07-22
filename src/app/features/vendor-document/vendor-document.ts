import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router, RouterLink } from '@angular/router';

interface VendorDocument {
  name: string;
  file: File | null;
  fileName: string;
  size: string;
}

@Component({
  selector: 'app-vendor-document',
  standalone: true,
  imports: [CommonModule, RouterLink],
  templateUrl: './vendor-document.html',
  styleUrls: ['./vendor-document.css']
})
export class VendorDocumentComponent {

  constructor(private router: Router) {}

  documents: VendorDocument[] = [
    {
      name: 'GST Certificate',
      file: null,
      fileName: 'gst_certificate.pdf',
      size: '1.2 MB'
    },
    {
      name: 'PAN Card',
      file: null,
      fileName: 'pan_card.pdf',
      size: '534 KB'
    },
    {
      name: 'Company Registration Certificate',
      file: null,
      fileName: 'company_registration.pdf',
      size: '1.8 MB'
    },
    {
      name: 'ISO Certificate',
      file: null,
      fileName: 'iso_certificate.pdf',
      size: '1.1 MB'
    },
    {
      name: 'Other Supporting Documents',
      file: null,
      fileName: 'other_docs.pdf',
      size: '2.3 MB'
    }
  ];

  uploadFile(event: Event, index: number): void {
    const input = event.target as HTMLInputElement;

    if (input.files && input.files.length > 0) {

      const file = input.files[0];

      this.documents[index].file = file;
      this.documents[index].fileName = file.name;
      this.documents[index].size =
        (file.size / 1024 / 1024).toFixed(2) + ' MB';
    }
  }

  viewFile(index: number): void {

    if (this.documents[index].file) {

      const url = URL.createObjectURL(this.documents[index].file!);
      window.open(url, '_blank');

    } else {

      alert('No file uploaded.');

    }

  }

  deleteFile(index: number): void {

    this.documents[index].file = null;
    this.documents[index].fileName = '';
    this.documents[index].size = '';

    alert('File deleted successfully.');

  }

  save(): void {

    alert('Documents saved successfully.');

  }

  finish(): void {

    alert('Vendor registration completed.');

    this.router.navigate(['/vendor-list']);

  }

}