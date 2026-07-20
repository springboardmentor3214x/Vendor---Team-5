import { ComponentFixture, TestBed } from '@angular/core/testing';

import { VendorApproval } from './vendor-approval';

describe('VendorApproval', () => {
  let component: VendorApproval;
  let fixture: ComponentFixture<VendorApproval>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [VendorApproval],
    }).compileComponents();

    fixture = TestBed.createComponent(VendorApproval);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
