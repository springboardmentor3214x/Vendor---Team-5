import { ComponentFixture, TestBed } from '@angular/core/testing';

import { VendorStatus } from './vendor-status';

describe('VendorStatus', () => {
  let component: VendorStatus;
  let fixture: ComponentFixture<VendorStatus>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [VendorStatus],
    }).compileComponents();

    fixture = TestBed.createComponent(VendorStatus);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
