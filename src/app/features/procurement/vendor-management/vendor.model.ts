export interface Vendor {
  vendorId: string;
  companyName: string;
  category: string;
  contactPerson: string;
  status: 'Active' | 'Pending' | 'Inactive';
  approvalStatus: 'Approved' | 'Pending' | 'Rejected';
}