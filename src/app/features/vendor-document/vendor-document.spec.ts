import { ComponentFixture, TestBed } from '@angular/core/testing';

import { VendorDocumentComponent } from './vendor-document';

describe('VendorDocument', () => {
  let component: VendorDocumentComponent;
  let fixture: ComponentFixture<VendorDocumentComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [VendorDocumentComponent],
    }).compileComponents();

    fixture = TestBed.createComponent(VendorDocumentComponent);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
