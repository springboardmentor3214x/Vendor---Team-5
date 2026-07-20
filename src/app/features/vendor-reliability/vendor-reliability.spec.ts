import { ComponentFixture, TestBed } from '@angular/core/testing';

import { VendorReliability } from './vendor-reliability';

describe('VendorReliability', () => {
  let component: VendorReliability;
  let fixture: ComponentFixture<VendorReliability>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [VendorReliability],
    }).compileComponents();

    fixture = TestBed.createComponent(VendorReliability);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
